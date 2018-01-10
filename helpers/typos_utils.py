# coding=utf-8

from __future__ import unicode_literals, print_function, division
from codecs import open

from collections import defaultdict
import string
import sys

from helpers.progress_bar import progress_bar

MORPHOSYNTACTIC_DICT_LEN = 4811854


def remove_polish_symbols(word):
    latin_equivalents = {
        "ę": "e",
        "ó": "o",
        "ą": "a",
        "ś": "s",
        "ł": "l",
        "ż": "z",
        "ź": "z",
        "ć": "c",
        "ń": "n"
    }
    return "".join([latin_equivalents.get(char, char) for char in word])


def remove_duplicates(word):
    return "".join(
        [
            char if i == 0 or word[i - 1] != char else ""
            for i, char in enumerate(word)
        ],
    )


def remove_polish_symbols_and_duplicates(word):
    return remove_duplicates(remove_polish_symbols(word))


def get_unigrams(path="1grams", cutoff=1):
    print("loading unigrams", file=sys.stderr)
    unigrams = defaultdict(lambda: 0)
    with open(path, encoding="utf8") as file:
        for line in file:
            line = line.replace(".", "").replace(",", "").replace("?", ""). \
                replace("-", "").replace(":", "").replace("\"", "").split()
            if len(line) != 2:
                continue
            occurrences, word = line
            unigrams[word] += int(occurrences)
            if int(occurrences) <= cutoff:
                break
    print("unigrams loaded", file=sys.stderr)
    return unigrams


def normalized_morphosyntactic(polish_morphosyntactic_dictionary):
    morphosyntactic_dictionary = defaultdict(lambda: set())

    print("creating normalized morphosyntactic dictionary",
          file=sys.stderr)
    print_progress = progress_bar()
    polish_dictionary_size = len(polish_morphosyntactic_dictionary)
    for word_idx, word in enumerate(polish_morphosyntactic_dictionary):
        if word_idx % 10000 == 0:
            print_progress(word_idx / polish_dictionary_size)
        normalized_word = remove_polish_symbols_and_duplicates(word)
        morphosyntactic_dictionary[normalized_word].add(word)
    print("\nnormalized dictionary created", file=sys.stderr)
    return morphosyntactic_dictionary


def polish_morphosyntactic(path="./polimorfologik-2.1.txt"):
    morphosyntactic_dictionary = set()
    with open(path, 'r', encoding='utf-8') as file:
        print("loading morphosyntactic dictionary",
              file=sys.stderr)
        print_progress = progress_bar()
        for line_number, line in enumerate(file):
            if line_number % 10000 == 0:
                print_progress(line_number / MORPHOSYNTACTIC_DICT_LEN)
            _, word, _ = line.split(";")
            word = word.lower()
            morphosyntactic_dictionary.add(word)
        print("\nmorphosyntactic dictionary loaded", file=sys.stderr)
    return morphosyntactic_dictionary


def generate_near_words(word, edit_distance):
    if edit_distance == 0:
        return {word}
    alphabet = list(string.ascii_lowercase)
    alphabet.append("")
    near_words = {0: {word}}

    def one_step(partial_solution, distance):
        new_partial_solution = set()
        for current_word in partial_solution[distance - 1]:
            for char_index in range(len(current_word)):
                new_partial_solution.add(
                    current_word[:char_index] + current_word[char_index+1:],
                )
                for letter in alphabet:
                    new_partial_solution.add(
                        current_word[:char_index] + letter +
                        current_word[char_index:],
                    )
                    new_partial_solution.add(
                        current_word[:char_index] + letter +
                        current_word[char_index + 1:],
                    )
                if char_index + 1 < len(current_word):
                    new_partial_solution.add(
                        current_word[:char_index] +
                        current_word[char_index+1] +
                        current_word[char_index] +
                        current_word[char_index+2:])
                if char_index + 2 < len(current_word):
                    new_partial_solution.add(
                        current_word[:char_index] +
                        current_word[char_index+2] +
                        current_word[char_index+1] +
                        current_word[char_index] +
                        current_word[char_index+3:],
                    )
        return new_partial_solution

    for i in range(edit_distance):
        near_words[i+1] = one_step(near_words, i+1)
    return near_words


def additional_search(near_words, morphosyntactic):
    """Finds more words only with omitting characters"""
    min_length = len(min(near_words, key=lambda x: len(x)))
    for word in near_words:
        if len(word) <= min_length + 3:
            for char_index in range(len(word), 0, -1):
                if word[:char_index] + word[char_index+1:] in morphosyntactic:
                    return word[:char_index] + word[char_index+1:]
    return None


# if __name__ == "__main__":
#     print(generate_near_words("nauczycielka", 1))
#     assert "nauyzccielka" in generate_near_words("nauczycielka", 1)[1]
#     print(remove_duplicates(remove_polish_symbols("łóożko")))
#     d = {
#         "lorem": 0,
#         "lorem ipsum": 0,
#         "lorem1": 0,
#         "lorem12": 0,
#         "lorem13": 0,
#     }
