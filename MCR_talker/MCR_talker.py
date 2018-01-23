# coding=utf-8
from __future__ import print_function, unicode_literals, division
from codecs import open

from helpers.fix_input import fix_input

import sys
import os
import random
import math
from collections import defaultdict
import cPickle as pickle

from helpers.progress_bar import progress_bar
from talker import Talker
from tf_idf import TF_IDF
from tokenization import tokenize, tokenize_dialogue
from dialogue_load import load_dialogues_from_file, split_dialogue
from reverse_index_serialization import load_reverse_index, reverse_index_created, store_reverse_index, IndexType
from helpers import spellcheck, morphosyntactic as morph

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
            base_tokens = morphosyntactic.get_dictionary().get(token.lower(), [])
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
                 quotes_path="../data/drama_quotes_longer.txt",
                 morphosyntactic_path="big_data/polimorfologik-2.1.txt",
                 stopwords_path="../data/stopwords.txt",
                 filter_rare_results=True,
                 default_quote="Jeden rabin powie tak, a inny powie nie.",
                 randomized=False,
                 filter_stopwords=False,
                 nonexistent_words_penalty=1,  # TODO: check default value
                 stopwords_penalty=.1,
                 select_answer_threshold=.99):
        self.morphosyntactic = morph.Morphosyntactic(morphosyntactic_path)
        self.morphosyntactic.get_dictionary()
        self.stopwords = MCRTalker.load_stopwords(stopwords_path)
        self.index = self.load_index(quotes_path)
        self.quotes = load_dialogues_from_file(quotes_path,
                                               do_tokenization=False, remove_authors=False)  # type: list[str]
        tf_idf_generator = TF_IDF(quotes_path, self.morphosyntactic)
        self.idf, self.term_frequency = tf_idf_generator.load()
        self.filter_rare_results = filter_rare_results
        self.default_quote = default_quote
        self.randomized = randomized
        self.used_quotes = {""}
        quotes_source = quotes_path.split("/")[-1].split("\\")[-1]
        self.name = "{0} ({1})".format(self.__class__.__name__, quotes_source)
        self.filter_stopwords = filter_stopwords
        self.default_tfidf_value = nonexistent_words_penalty
        self.stopword_tfidf_value = stopwords_penalty
        self.line_tf = None
        self.vector_file_extension = ".vec"
        self.vector_serialization = VectorSerialization(quotes_path, self.quotes,
                                                        self.morphologocal_bases, self._score_function,
                                                        vector_file_extension=self.vector_file_extension)
        self.vector_serialization.load()
        self.select_answer_threshold = select_answer_threshold

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
        selected_quote, score = self.select_quote(results, line, question)
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
                # line = spellcheck.spellcheck(line)
                tokenized_line = self.tokenize_input(line)
                results = self.find_matching_quotes(tokenized_line)
                selected_quote, score = self.select_quote(results, tokenized_line, line)
                # self.used_quotes.add(selected_quote)
                print(selected_quote, score)
        except KeyboardInterrupt:
            return
        except EOFError:
            return

    def tokenize_input(self, line):
        if len(line) > 0 and line[0].upper():
            line = line[0].lower() + line[1:]

        line = tokenize(line)
        if self.filter_stopwords:
            for word_idx, word in enumerate(line):
                if word in self.stopwords:
                    line[word_idx] = "__" + word

        tokenized_line = []
        for token in line:
            if token.isalpha():
                token = self.morphosyntactic.get_dictionary().get(token, [token])
                tokenized_line.append(token)
        return tokenized_line

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

    def select_quote(self, results, line, raw_question):
        # type: (MCRTalker, dict[int, set[int]], list[list[str]], str) -> tuple[unicode, float]
        if len(results) == 0:
            return self.default_quote, 0.
        if self.filter_rare_results:  # TODO: Test impact on speed and correctness
            if any((len(k) > 1 for k in results.values())):
                results = {k: v for k, v in results.items() if len(v) > 1}

        self.line_tf = TF_IDF("__temp", self.morphosyntactic).compute_dialogue_tf([raw_question])
        possible_quotes = self._get_quotes_from_indices(results)
        question_vector = WordVector(line, self._question_score_function)
        for possible_quote in possible_quotes:
            possible_quote[0], possible_quote[1] = self.evaluate_quote(possible_quote, question_vector)  # TODO: Select best quote, to powinno być bez tego for, za każdym razem tworzy wektor dla pytania
        self.line_tf = None
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

    def _base_score_function(self, word, line_idx, term_frequency):
        if word not in self.idf:
            if "".startswith("__"):
                return self.stopword_tfidf_value
            else:
                return self.default_tfidf_value
        else:
            word_frequency = 0
            for idx in range(line_idx + 1):
                word_frequency += term_frequency[idx].get(word, 0)
            if word_frequency == 0:
                word_frequency = 1
            return word_frequency * self.idf[word]

    def _score_function(self, word, quote_idx, line_idx):
        return self._base_score_function(word, line_idx, self.term_frequency[quote_idx])

    def _question_score_function(self, word, *args):
        return self._base_score_function(word, 0, self.line_tf[0])

    def morphologocal_bases(self, quote):
        for dialogue_idx, dialogue in enumerate(quote):
            _quote_text = []
            for token in dialogue:
                if token.isalpha():
                    _quote_text.append(self.morphosyntactic.get_dictionary().get(token, [token]))
            quote[dialogue_idx] = _quote_text
        return quote

    def evaluate_quote(self, quote, question_vector, choose_answer=False):
        quote_idx = quote[1]
        raw_quote_text = split_dialogue(quote[0])
        quote_text = tokenize_dialogue(quote[0])
        quote_text = self.morphologocal_bases(quote_text)
        best_quote = raw_quote_text[0]
        cosine = 0

        for dialogue_idx in range(len(quote_text)):
            quote_vector = self.vector_serialization.word_vectors[quote_idx][dialogue_idx]
            if quote_vector.len() == 0 or question_vector.len() == 0:
                new_cosine = 0
            else:
                new_cosine = quote_vector.__matmul__(question_vector)
                new_cosine /= quote_vector.len() * question_vector.len()
            if new_cosine >= self.select_answer_threshold:
                choose_answer = True
            if new_cosine > cosine and (not choose_answer or len(quote_text) > dialogue_idx + 1):
                cosine = new_cosine
                best_quote = raw_quote_text[dialogue_idx + choose_answer]
        return best_quote, cosine


class WordVector:  # TODO: faster!
    def __init__(self, quote, score_function, quote_idx=None, line_idx=None):
        self.vector = defaultdict(lambda: 0)
        for possible_words in quote:
            for base_word in possible_words:
                base_word_score = score_function(base_word, quote_idx, line_idx)
                self.vector[base_word] = base_word_score
        self.vector = dict(self.vector)
        length = sum(value ** 2 for value in self.vector.values())
        self._len = math.sqrt(length)

    def len(self):
        return self._len

    def __getitem__(self, item):
        return self.vector[item]

    def __matmul__(self, other):
        dot_product = sum(self[word] * other[word]
                          for word in set.intersection(set(self.vector.keys()), set(other.vector.keys())))
        return dot_product

    def __str__(self):
        return str(self.vector)


class VectorSerialization(object):
    def __init__(self, collection_path, dialogues,
                 morphologocal_bases_function, score_function,
                 vector_file_extension=".vec",):
        self.dialogues = dialogues
        self.collection_path = collection_path
        self.vector_file_extension = vector_file_extension
        self.vector_path = self.collection_path + self.vector_file_extension
        self.word_vectors = []
        self.morphologocal_bases = morphologocal_bases_function
        self.score_function = score_function

    def compute_vectors(self):
        print("Creating vector representation", file=sys.stderr)
        print_progress = progress_bar()
        dialogues_size = len(self.dialogues)
        for quote_idx, quote in enumerate(self.dialogues):
            if quote_idx % 200 == 0:
                print_progress(quote_idx / dialogues_size)
            self.word_vectors.append(self.create_vector(quote, quote_idx))

    def create_vector(self, quote, quote_idx):
        quote_text = tokenize_dialogue(quote)
        quote_text = self.morphologocal_bases(quote_text)
        slice_vectors = []

        for dialogue_idx, dialogue in enumerate(quote_text):
            quote_slice = quote_text[:dialogue_idx + 1]
            quote_slice = [item for sublist in quote_slice for item in sublist]
            quote_vector = WordVector(quote_slice, self.score_function, quote_idx, dialogue_idx)
            slice_vectors.append(quote_vector)
        return slice_vectors

    def save(self):
        if len(self.word_vectors) == 0:
            self.compute_vectors()
        with open(self.vector_path, "wb") as vector_file:
            pickle.dump(self.word_vectors, vector_file)
        return self.vector_path

    def load(self):
        if self.vector_file_created():
            with open(self.vector_path, "rb") as vector_file:
                self.word_vectors = pickle.load(vector_file)
        else:
            self.compute_vectors()
            self.save()
        return self.word_vectors

    def vector_file_created(self):
        return os.path.isfile(self.collection_path + self.vector_file_extension)


if __name__ == "__main__":
    os.chdir("..")
    talker = MCRTalker(quotes_path="data/wikiquote_polish_dialogs.txt",
                       morphosyntactic_path="big_data/polimorfologik-2.1.txt",
                       filter_rare_results=True)
    print(talker.my_name(), talker._get_answer("Dzień dobry!"))
    talker.test()