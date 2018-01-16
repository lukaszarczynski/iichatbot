# coding=utf-8
from __future__ import print_function, unicode_literals, division
from codecs import open
from helpers.fix_input import fix_input

import sys
import os
import random
import math
from collections import defaultdict

import morphosyntactic as morph
from talker import Talker
from tf_idf import TF_IDF
from tokenization import tokenize, tokenize_dialogue
from dialogue_load import load_dialogues_from_file, split_dialogue
from reverse_index_serialization import load_reverse_index, reverse_index_created, store_reverse_index, IndexType
from helpers import spellcheck


input = fix_input()


def create_reverse_index(path_to_documents_collection, morphosyntactic):
    index = defaultdict(lambda: set())

    with open(path_to_documents_collection, 'r', encoding='utf-8') as file:
        print("+++ creating reverse index +++", file=sys.stderr)
        for line_number, line in enumerate(file):
            if line.startswith("#"):
                continue
            line = tokenize(line.split(":")[-1])
            for token in line:
                base_tokens = morphosyntactic.get_dictionary().get(token.lower(), [])
                for base_token in base_tokens:
                    index[base_token.encode("utf-8")].add(line_number)
        print("+++ reverse index created +++", file=sys.stderr)
        print("Index length: ", len(index), file=sys.stderr)
    return [index, []]


def create_dialogue_reverse_index(path_to_documents_collection, morphosyntactic):
    index = defaultdict(lambda: set())

    dialogues = load_dialogues_from_file(path_to_documents_collection,
                                         remove_authors=True, do_tokenization=True)
    print("+++ creating reverse index +++", file=sys.stderr)
    for dialogue_idx, dialogue in enumerate(dialogues):
        for token in dialogue:
            base_tokens = morphosyntactic.get_dictionary().get(token, [])
            for base_token in base_tokens:
                index[base_token.encode("utf-8")].add(dialogue_idx)
    print("+++ reverse index created +++", file=sys.stderr)
    print("Index length: ", len(index), file=sys.stderr)
    return [index, []]


def weighted_draw(possible_quotes):
    total = sum(w for c, w in possible_quotes)
    r = random.uniform(0, total)
    upto = 0
    for c, w in possible_quotes:
        if upto + w >= r:
            return c, w
        upto += w


class MCRTalker(Talker):
    def __init__(self,
                 morphosyntactic_path="big_data/polimorfologik-2.1.txt",
                 quotes_path="../data/drama_quotes_longer.txt",
                 stopwords_path="../data/stopwords.txt",
                 filter_rare_results=False,
                 default_quote="Jeden rabin powie tak, a inny powie nie.",
                 randomized=False):
        self.morphosyntactic = morph.Morphosyntactic(morphosyntactic_path)
        self.morphosyntactic.get_dictionary()
        self.stopwords = MCRTalker.load_stopwords(stopwords_path)
        self.index = self.load_index(quotes_path)
        self.quotes = load_dialogues_from_file(quotes_path,
                                               do_tokenization=False, remove_authors=False)  # type: list[str]
        tf_idf_generator = TF_IDF(quotes_path, self.morphosyntactic)
        self.tf_idf = tf_idf_generator.load()  # type: dict[int, dict[str, float]]
        self.filter_rare_results = filter_rare_results
        self.default_quote = default_quote
        self.randomized = randomized
        self.used_quotes = {""}
        quotes_source = quotes_path.split("/")[-1].split("\\")[-1]
        self.name = "{0} ({1})".format(self.__class__.__name__, quotes_source)

    def get_answer(self, question, status):
        real_question = question["fixed_typos"]
        selected_quote, score = self._get_answer(real_question)
        if selected_quote == self.default_quote:
            return {"answer": selected_quote,
                    "score": 0}
        else:
            return {"answer": selected_quote,
                    "score": min(score, 1.)}

    def _get_answer(self, question):
        line = self.tokenize_input(question)
        results = self.find_matching_quotes(line)
        selected_quote, score = self.select_quote(results, line)
        # self.used_quotes.add(selected_quote)
        return selected_quote, score

    def my_name(self):
        return self.name

    @staticmethod
    def load_stopwords(stopwords_path):
        try:
            with open(stopwords_path, encoding="utf-8") as file:
                line = file.readline()
                stopwords = line.split(", ")
        except IOError:
            stopwords = ()
        return stopwords

    def load_index(self, quotes_path):
        if reverse_index_created(quotes_path, IndexType.DIALOGUE):
            index = load_reverse_index(quotes_path, IndexType.DIALOGUE)
        else:
            index = store_reverse_index(quotes_path, create_dialogue_reverse_index, [self.morphosyntactic],
                                        index_type=IndexType.DIALOGUE)
        return index

    def test(self):
        try:
            while True:
                line = input("> ").strip()
                line = spellcheck.spellcheck(line)
                line = self.tokenize_input(line)
                results = self.find_matching_quotes(line)
                selected_quote, score = self.select_quote(results, line)
                self.used_quotes.add(selected_quote)
                print(selected_quote, score)
        except KeyboardInterrupt:
            return
        except EOFError:
            return

    def tokenize_input(self, line):
        if len(line) > 0 and line[0].upper():
            line = line[0].lower() + line[1:]

        line = list(filter(lambda x: x not in self.stopwords, tokenize(line)))
        line = [self.morphosyntactic.get_dictionary().get(token, []) for token in line]
        return line

    def find_matching_quotes(self, line):
        quotes_sets = []
        for base_tokens in line:
            quotes_indices = set()
            for base_token in base_tokens:
                base_token_bytes = base_token.encode("utf-8")
                quotes_indices.update(self.index.get(base_token_bytes, []))
            quotes_sets.append(quotes_indices)
        results = defaultdict(lambda: set())
        for i, quotes_set in enumerate(quotes_sets):
            for quote_number in quotes_set:
                results[quote_number].add(i)
        return results

    def select_quote(self, results, line):
        # type: (MCRTalker, dict[int, set[int]], list[list[str]]) -> tuple[unicode, float]
        if len(results) == 0:
            return self.default_quote, 0.
        if self.filter_rare_results:  # TODO: Test impact on speed and correctness
            if any((len(k) > 1 for k in results.values())):
                results = {k: v for k, v in results.items() if len(v) > 1}

        line = [base_words for base_words in line if base_words != []]

        possible_quotes = self._get_quotes_from_indices(results)
        for possible_quote in possible_quotes:
            possible_quote[0], possible_quote[1] = self.evaluate_quote(possible_quote, line)  # TODO: Select best quote

        if self.randomized:
            selected_quote, score = self._select_randomized_quote(possible_quotes)
        else:
            selected_quote, score = self._select_best_quote(possible_quotes)
        return selected_quote, score

    def _get_quotes_from_indices(self, results):
        possible_quotes = []
        for result in results.keys():
            try:
                possible_quotes.append([self.quotes[result], result])
            except IndexError:
                pass
        return possible_quotes

    def _select_randomized_quote(self, possible_quotes):
        selected_quote = [""]
        while selected_quote[0] in self.used_quotes:
            if len(possible_quotes) == 0:
                return self.default_quote
            selected_quote = weighted_draw(possible_quotes)
            possible_quotes.remove(list(selected_quote))
        return selected_quote

    def _select_best_quote(self, possible_quotes):
        max_value = max(possible_quotes, key=lambda x: x[1])[1]
        possible_quotes.sort(key=lambda x: x[1], reverse=True)
        possible_quotes_max = list(filter(lambda x: x[1] == max_value, possible_quotes))
        selected_quote = possible_quotes_max[0]
        i = 0
        while selected_quote[0] in self.used_quotes:
            i += 1
            if i < len(possible_quotes):
                selected_quote = possible_quotes[i]
            else:
                return self.default_quote
        return selected_quote

    def _score_function(self, word, quote_idx):
        return self.tf_idf[quote_idx].get(word, 0)

    def evaluate_quote(self, quote, question, choose_answer=False):
        quote_idx = quote[1]
        raw_quote_text = split_dialogue(quote[0])
        quote_text = tokenize_dialogue(quote[0])  # TODO: faster?
        for dialogue_idx, dialogue in enumerate(quote_text):
            _quote_text = [self.morphosyntactic.get_dictionary().get(token, []) for token in dialogue]
            quote_text[dialogue_idx] = [base_words for base_words in _quote_text if base_words != []]

        best_quote = raw_quote_text[0]
        cosine = 0
        question_vector = WordVector(question, self._score_function, quote_idx)

        for dialogue_idx, dialogue in enumerate(quote_text):
            quote_slice = quote_text[:dialogue_idx + 1]
            quote_slice = [item for sublist in quote_slice for item in sublist]
            quote_vector = WordVector(quote_slice, self._score_function, quote_idx)

            try:
                new_cosine = ((quote_vector.__matmul__(question_vector)) /
                              (quote_vector.len() * question_vector.len()))
            except ZeroDivisionError:  # TODO: Check tf-idf
                new_cosine = 0
            if new_cosine > cosine and (not choose_answer or len(quote_text) > dialogue_idx + 1):
                cosine = new_cosine
                best_quote = raw_quote_text[dialogue_idx + choose_answer]

        return best_quote, cosine


class WordVector:  # TODO: faster!
    def __init__(self, quote, score_function, quote_idx):
        self.vector = defaultdict(lambda: 0)
        for possible_words in quote:
            for base_word in possible_words:
                base_word_score = score_function(base_word, quote_idx)
                self.vector[base_word] = base_word_score

    def len(self):
        length = sum(value ** 2 for value in self.vector.values())
        return math.sqrt(length)

    def __getitem__(self, item):
        return self.vector[item]

    def __matmul__(self, other):
        dot_product = sum(self[word] * other[word]
                          for word in set.union(set(self.vector.keys()), set(other.vector.keys())))
        return dot_product

    def __str__(self):
        return str(self.vector)


if __name__ == "__main__":
    os.chdir("..")
    spellcheck.init("typos")
    talker = MCRTalker(quotes_path="data/wikiquote_polish_dialogs.txt",
                       # filter_rare_results=True,
                       morphosyntactic_path="big_data/polimorfologik-2.1.txt")
    print(talker.my_name(), talker._get_answer("Dzień dobry!"))
    talker.test()
