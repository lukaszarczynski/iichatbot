# coding=utf-8

from __future__ import print_function, unicode_literals, division
from codecs import open

import sys
import time
import re

from edit_distance import edit_distance
from typos_utils import (
    remove_polish_symbols_and_duplicates,
    get_unigrams,
    normalized_morphosyntactic,
    generate_near_words,
    additional_search,
    polish_morphosyntactic,
)

MAX_EDIT_DISTANCE = 1

if sys.version_info.major < 3:
    global input

    def input(*args, **kwargs):
        """input function similar to one from Python 3"""
        return raw_input(*args, **kwargs).decode("utf8")


class Typos(object):
    """
    Attempts to fix typos

    :param unigrams_path: path to text file with unigrams (default: ./1grams)
    :type unigrams_path: str
    :param morph_dictionary_path: path to text file with morphosyntactic
        dictionary (default: ./polimorfologik-2.1.txt)
    :type morph_dictionary_path: str
    """
    def __init__(
        self,
        unigrams_path="./1grams",
        morph_dictionary_path="./polimorfologik-2.1.txt",
    ):
        self.unigrams = get_unigrams(unigrams_path)
        self.polish_morphosyntactic = polish_morphosyntactic(
            morph_dictionary_path,
        )
        self.normalized_morphosyntactic = normalized_morphosyntactic(
            self.polish_morphosyntactic,
        )

    def _select_correct_word(
        self,
        possibly_corrected_polish,
        wrong,
        near_words,
    ):
        if len(possibly_corrected_polish) > 0:
            min_edit_distance = edit_distance(
                min(
                    possibly_corrected_polish,
                    key=lambda x: edit_distance(x[0], wrong)
                )[0],
                wrong,
            )
            corrected = max(
                possibly_corrected_polish,
                key=lambda x: (
                    x[1] / (edit_distance(x[0], wrong) - min_edit_distance + 1)
                ),
            )[0]
        else:
            more_distant_words = []
            more_distant_word = additional_search(
                near_words[MAX_EDIT_DISTANCE],
                self.normalized_morphosyntactic,
            )
            if more_distant_word is None:
                corrected = None
            else:
                for polish_word in self.normalized_morphosyntactic[
                    more_distant_word
                ]:
                    more_distant_words.append(
                        (polish_word, self.unigrams[polish_word]),
                    )

                if more_distant_words == []:
                    corrected = None
                else:
                    min_edit_distance = edit_distance(
                        min(
                            more_distant_words,
                            key=lambda x: edit_distance(x[0], wrong)
                        )[0],
                        wrong,
                    )
                    corrected = max(
                        more_distant_words,
                        key=lambda x: (
                            x[1] / (
                                edit_distance(x[0], wrong) -
                                min_edit_distance + 1
                            )
                        ),
                    )[0]
        return corrected

    def _find_possible_corrections(self, word_with_typo):
        possible_corrections_without_polish_chars = []
        possible_corrections = []
        k = 0
        near_words = generate_near_words(
            remove_polish_symbols_and_duplicates(word_with_typo),
            MAX_EDIT_DISTANCE,
        )
        for i in range(MAX_EDIT_DISTANCE + 1):
            for w in near_words[i]:
                if w in self.normalized_morphosyntactic:
                    k += 1
                    possible_corrections_without_polish_chars.append(w)
            if k > 0:
                break

        for word in possible_corrections_without_polish_chars:
            for polish_word in self.normalized_morphosyntactic[word]:
                possible_corrections.append(
                    (polish_word, self.unigrams.get(polish_word, 0)),
                )

        return possible_corrections, near_words

    def _correct(self, word_with_typo):
        def contains_letter(word):
            for char in word:
                if char.isalpha():
                    return True
            return False

        if not contains_letter(word_with_typo):
            return word_with_typo, None
        possible_corrections, near_words = self._find_possible_corrections(
            word_with_typo,
        )
        corrected = self._select_correct_word(
            possible_corrections,
            word_with_typo,
            near_words,
        )
        return corrected, possible_corrections

    def correct(self, word_with_typo):
        """
        :param word_with_typo: Word to correct
        :type word_with_typo: unicode
        :return: Corrected word or word with typo if word shouldn't or
            couldn't be corrected
        :rtype: unicode
        """
        if not isinstance(word_with_typo, unicode):
            word_with_typo = word_with_typo.decode("utf-8")
        if word_with_typo in self.polish_morphosyntactic:
            return word_with_typo
        corrected, _ = self._correct(word_with_typo.lower())
        if corrected is None:
            corrected = word_with_typo
        return corrected

    def correct_line(self, line):
        """
        :param line: Line to correct
        :type line: str, unicode
        :return: Line with corrected words unless word shouldn't or couldn't
            be corrected
        :rtype: str, unicode
        """
        if not isinstance(line, unicode):
            line = line.decode("utf-8")
        print("line: ", line)
        tokenized = re.split('([ęóąśłżźćń\w]+)', line.lower())
        corrected = []
        for token in tokenized:
            corrected.append(self.correct(token))
        print("corrected: ", "".join(corrected), file=sys.stderr)
        return "".join(corrected)


def print_results(
    line,
    correct_word,
    word_with_typo,
    corrected,
    possible_corrections,
    output,
):
    print(
        line.split(),
        edit_distance(correct_word, word_with_typo),
        file=output,
    )
    print("\n".join([str(p) for p in possible_corrections]), file=output)
    print("Corrected: ", corrected, file=output)
    print("\n\n\n", file=output)


def test_correction_with_typos_file(
    typos_path="./literowki_dev1.txt",
    unigrams_path="./1grams",
    morph_dictionary_path="./polimorfologik-2.1.txt",
):
    typos = Typos(unigrams_path, morph_dictionary_path)

    with open(typos_path, encoding="utf8") as file:
        max_time = 0
        t1 = time.time()
        number_of_good_corrections = 0
        line_number = -1
        for line_number, line in enumerate(file):
            t0 = time.time()

            correct_word, word_with_typo = line.split()

            corrected, possible_corrections = typos._correct(word_with_typo)

            if corrected == correct_word:
                number_of_good_corrections += 1
                output = sys.stdout
            else:
                output = sys.stderr

            print_results(
                line,
                correct_word,
                word_with_typo,
                corrected,
                possible_corrections,
                output,
            )

            max_time = max(max_time, time.time() - t0)

        print("Max time: ", max_time)
        print("Average time: ", (time.time() - t1) / line_number, line_number)
        print("Accuracy: ", number_of_good_corrections / (line_number + 1))
    return typos


if __name__ == "__main__":
    kwargs = {}

    filenames = (
        "literówkami (domyślnie ./literowki_dev1.txt)",
        "unigramami (domyślnie ./1grams)",
        "słownikiem morfosyntaktycznym (domyślnie ./polimorfologik-2.1.txt)",
    )

    typos_path, unigrams_path, morph_dictionary_path = "", "", ""
    file_paths = (typos_path, unigrams_path, morph_dictionary_path)
    variable_names = ("typos_path", "unigrams_path", "morph_dictionary_path")

    for name, path, variable_name in zip(
        filenames,
        file_paths,
        variable_names,
    ):
        print("Wprowadź ścieżkę do pliku z ", name)
        path = input().strip()
        if path != "":
            kwargs[variable_name] = path

    typos = test_correction_with_typos_file(**kwargs)
    line_with_typos = input("> ").strip()
    while line_with_typos != "":
        corrected = typos.correct_line(line_with_typos)
        print(corrected)
        line_with_typos = input("> ").strip()
