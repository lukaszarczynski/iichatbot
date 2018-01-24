# coding=utf-8
from __future__ import print_function, unicode_literals, division
from helpers.fix_input import fix_input

import re

input = fix_input()


def tokenize(text):
    """Split text into list of alphanumeric words and other characters"""
    polish_chars = "ęóąśłżźćń"
    pattern = '([{0}{1}\w]+)'.format(polish_chars, polish_chars.upper())
    tokenized = re.split(pattern, text)
    return [word for word in tokenized if word != '']


def tokenize_list(dialogues_list):
    return [tokenize(line) for line in dialogues_list]


def remove_authors_from_dialogues(dialogues_list):
    return ["\n".join([":".join(line.split(":")[1:])
                       for line in dialogue.split("\n")])
            for dialogue in dialogues_list]


def tokenize_dialogue(dialogue_text):
    dialogue_list = [":".join(line.split(":")[1:])
                     for line in dialogue_text.split("\n") if line != ""]
    dialogue_list = [tokenize(line.lower()) for line in dialogue_list if line.strip() != ""]
    return dialogue_list


if __name__ == "__main__":
    print(tokenize("lorem, ipsum"))
    assert tokenize("lorem, ipsum") == ['lorem', ', ', 'ipsum']
    test_text = input()
    print(tokenize(test_text))
    print(tokenize_dialogue("Dzień dobry?\n"))
