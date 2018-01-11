# coding=utf-8

from __future__ import unicode_literals, print_function

import sys

if sys.version_info.major < 3:
    global input

    def input(*args, **kwargs):
        """input function similar to one from Python 3"""
        return raw_input(*args, **kwargs).decode("utf8")


def edit_distance(
    word1,
    word2,
    insertion_cost=1,
    deletion_cost=1,
    substitution_cost=1,
    transposition_cost=1
):
    """
        Finds edit distance between two words with given costs
        (default: Damerau–Levenshtein distance)
    """
    word1 = ' ' + word1
    word2 = ' ' + word2
    length1 = len(word1)
    length2 = len(word2)
    prefix_edit_distances = [[0] * length2 for _ in range(length1)]
    for i in range(length1):
        prefix_edit_distances[i][0] = i * deletion_cost
    for j in range(length2):
        prefix_edit_distances[0][j] = j * insertion_cost
    for i in range(1, length1):
        for j in range(1, length2):
            if word1[i] == word2[j]:
                prefix_edit_distances[i][j] = prefix_edit_distances[i-1][j-1]
            else:
                prefix_edit_distances[i][j] = min(
                    prefix_edit_distances[i-1][j] + deletion_cost,
                    prefix_edit_distances[i][j-1] + insertion_cost,
                    prefix_edit_distances[i-1][j-1] + substitution_cost,
                )
                if (
                    i > 1 and
                    j > 1 and
                    word1[i] == word2[j - 1] and
                    word1[i - 1] == word2[j]
                ):
                    prefix_edit_distances[i][j] = min(
                        prefix_edit_distances[i][j],
                        prefix_edit_distances[i-2][j-2] + transposition_cost
                    )
    return prefix_edit_distances[length1-1][length2-1]


# if __name__ == "__main__":
#     print("qwertyź", "qwretzź", edit_distance("qwertyź", "qwretzź"))
#     w1 = input("> ")
#     w2 = input("> ")
#     print(edit_distance(w1, w2, 1, 1, 1, 1))
