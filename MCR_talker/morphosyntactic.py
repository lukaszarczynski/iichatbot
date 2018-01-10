# coding=utf-8
from __future__ import print_function, unicode_literals, division
from codecs import open

import sys

from helpers.progress_bar import progress_bar

DICT_LEN = 4811854


class Morphosyntactic:
    """Stores morphosyntactic dictionary"""
    def __init__(self, dictionary_file_path):
        self.morphosyntactic_dictionary = {}
        self.dictionary_file_path = dictionary_file_path

    def create_morphosyntactic_dictionary(self):
        """Creates dictionary representation from file"""
        with open(self.dictionary_file_path, 'r', encoding='utf-8') as file:
            print("Tworzenie słownika morfosyntaktycznego:", file=sys.stderr)
            print_progress = progress_bar()
            for line_number, line in enumerate(file.readlines()):
                if line_number % 1000 == 0:
                    progress = line_number / DICT_LEN
                    print_progress(progress)
                base_word, word, tags = line.rstrip("\n").split(";")
                if word.lower() in self.morphosyntactic_dictionary:
                    self.morphosyntactic_dictionary[word.lower()].append(base_word)
                else:
                    self.morphosyntactic_dictionary[word.lower()] = [base_word]
            print("\n", file=sys.stderr)
        return self.morphosyntactic_dictionary

    def get_dictionary(self):
        if len(self.morphosyntactic_dictionary) == 0:
            self.create_morphosyntactic_dictionary()
        return self.morphosyntactic_dictionary


if __name__ == "__main__":
    morph = Morphosyntactic("data/polimorfologik-2.1.txt")
    morph.create_morphosyntactic_dictionary()
    d = morph.morphosyntactic_dictionary
    print(d["pić"])
    print(d["piła"])
    print(d["picie"])
    assert d["pić"] == ['picie', 'pić']
    assert d["picie"] == ['PIT', 'picie', 'pita', 'pić']
