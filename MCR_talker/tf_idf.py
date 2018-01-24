# coding=utf-8
from __future__ import unicode_literals, print_function, division

import sys
import cPickle as pickle
from collections import defaultdict
from math import log
from os.path import isfile

import math

from dialogue_load import load_dialogues_from_file
from helpers.morphosyntactic import Morphosyntactic
from tokenization import tokenize, remove_authors_from_dialogues, tokenize_list
from helpers.progress_bar import progress_bar


class TF_IDF:
    def __init__(self, document_path, morphosyntactic=None):
        self.document_path = document_path
        self.idf_file_extension = ".idf"
        self.tf_file_extension = ".tf"
        self.morphosyntactic = morphosyntactic
        self.dialogues_bag_of_words = None
        self.dialogues_lines = None
        self.idf = {}
        self.dialogue_term_frequency = []  # type: list[list[dict[str, float]]]
        self.document_frequency = defaultdict(lambda: 0)

    def get_dialogues_bag_of_words(self):
        if self.dialogues_bag_of_words is None:
            self.dialogues_bag_of_words = load_dialogues_from_file(self.document_path,
                                                                   remove_authors=True)
        return self.dialogues_bag_of_words

    def get_dialogues_lines(self):
        if self.dialogues_lines is None:
            self.dialogues_lines = load_dialogues_from_file(self.document_path,
                                                            remove_authors=True, do_tokenization=False)
            self.dialogues_lines = [dialogue.split("\n") for dialogue in self.dialogues_lines]
        return self.dialogues_lines

    def save(self):
        if len(self.idf) == 0:
            self.compute_idf()
        if len(self.dialogue_term_frequency) == 0:
            self.compute_dialogue_tf()
        idf_path = self.document_path + self.idf_file_extension
        tf_path = self.document_path + self.tf_file_extension
        with open(idf_path, "wb") as idf_file:
            pickle.dump(self.idf, idf_file)
        with open(tf_path, "wb") as tf_file:
            pickle.dump(self.dialogue_term_frequency, tf_file)
        return idf_path

    def load(self):
        idf_path = self.document_path + self.idf_file_extension
        tf_path = self.document_path + self.tf_file_extension
        if isfile(idf_path) and isfile(tf_path):
            with open(self.document_path + self.idf_file_extension, "rb") as idf_file:
                self.idf = pickle.load(idf_file)
            with open(self.document_path + self.tf_file_extension, "rb") as tf_file:
                self.dialogue_term_frequency = pickle.load(tf_file)
        else:
            self.compute_idf()
            self.compute_dialogue_tf()
            self.save()
        return self.idf, self.dialogue_term_frequency

    def _increase_dialogue_tf(self, term, line_idx, document_idx):
        while len(self.dialogue_term_frequency) <= document_idx:
            self.dialogue_term_frequency.append([])
        while len(self.dialogue_term_frequency[document_idx]) <= line_idx:
            self.dialogue_term_frequency[document_idx].append({})
        if term in self.morphosyntactic.get_dictionary():
            base_forms = self.morphosyntactic.get_dictionary()[term]
            for base_form in base_forms:
                if base_form not in self.dialogue_term_frequency[document_idx][line_idx]:
                    self.dialogue_term_frequency[document_idx][line_idx][base_form] = 0
                self.dialogue_term_frequency[document_idx][line_idx][base_form] += 1 / math.sqrt(len(base_forms))

    def _df_increaser(self):
        def increase_df_once(term):
            if term in self.morphosyntactic.get_dictionary():
                base_forms = self.morphosyntactic.get_dictionary()[term]
                for base_form in base_forms:
                    if base_form not in increase_df_once.used_terms:
                        self.document_frequency[base_form] += 1
                        increase_df_once.used_terms.append(base_form)

        increase_df_once.used_terms = []

        return increase_df_once

    def compute_dialogue_tf(self, text=None):
        if text is not None:
            dialogues = [dialogue.split("\n") for dialogue in text]
        else:
            dialogues = self.get_dialogues_lines()

        self.dialogue_term_frequency = []
        for document_idx, document in enumerate(dialogues):
            for line_idx, line in enumerate(document):
                for term in tokenize(line):
                    term = term.lower()
                    if term.isalpha():
                        self._increase_dialogue_tf(term, line_idx, document_idx)
        return self.dialogue_term_frequency

    def compute_idf(self, text=None):
        if text is not None:
            dialogues = text
        else:
            dialogues = self.get_dialogues_bag_of_words()

        print("Computing idf", file=sys.stderr)
        print_progress = progress_bar()
        dialogues_size = len(dialogues)
        for document_idx, document in enumerate(dialogues):
            if document_idx % 200 == 0:
                print_progress(document_idx / dialogues_size)
            increase_df = self._df_increaser()
            for term in document:
                term = term.lower()
                if term.isalpha():
                    increase_df(term)

        self.idf = {term: log(len(dialogues) / frequency, 2)
                    for term, frequency in self.document_frequency.items()}
        print("\n", file=sys.stderr)
        return self.idf


if __name__ == "__main__":
    text = ["Ktoś:Witajcie, ludzie!",
            "Ktoś:Przybywamy do Was w pokoju i dobrej woli!",
            "Ktoś:Robot(człowiek) nie może skrzywdzić człowieka, ani przez zaniechanie dopuścić, by doznał on (człowiek) krzywdy.",
            "Ktoś:Roboty widziały rzeczy, o których Wam, ludziom, się nie śniło.",
            "Ktoś:Roboty to Twoi plastikowi kumple, z którymi fajnie jest przebywać.",
            "Ktoś:Roboty mają lśniące, metalowe tyłki, których nie należy gryźć.",
            "Ktoś:I mają \nKtoś inny:plan."]

    tokenized_text = tokenize_list(text)
    text_without_authors = remove_authors_from_dialogues(text)

    morph = Morphosyntactic("../big_data/polimorfologik-2.1.txt")
    tfidf = TF_IDF("../data/tf_idf_test", morph)
    tfidf.compute_idf(tokenized_text)
    tfidf.compute_dialogue_tf(text_without_authors)

    print("dialogue_term_frequency", tfidf.dialogue_term_frequency)
    print("document_frequency", tfidf.document_frequency)
    print("idf", tfidf.idf, "\n")

    saved_path = tfidf.save()
    del tfidf
    tf_idf = TF_IDF("../data/tf_idf_test", morph).load()
    print(tf_idf)

    tf_idf = TF_IDF("../data/dzien_dobry.txt", morph)
    tf_idf.compute_idf()
    tf_idf.compute_dialogue_tf()

    print("dialogue_term_frequency", tf_idf.dialogue_term_frequency)
    print("document_frequency", tf_idf.document_frequency)
    print("tf_idf", tf_idf.idf)
