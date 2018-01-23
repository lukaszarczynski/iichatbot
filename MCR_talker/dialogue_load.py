# coding=utf-8
from __future__ import print_function, unicode_literals, division
from codecs import open

from tokenization import tokenize_list, remove_authors_from_dialogues


def load_dialogues_from_file(document_path,
                             do_tokenization=True,
                             remove_authors=False):
    with open(document_path, encoding="utf8") as file:
        lines = file.readlines()
        dialogues_list = [line.replace("\r\n", "\n") for line in lines if not line.startswith("#")]
        dialogues_list = "".join(dialogues_list)
        dialogues_list = dialogues_list.split("\n\n")
        if remove_authors:
            dialogues_list = remove_authors_from_dialogues(dialogues_list)
        if do_tokenization:
            dialogues_list = tokenize_list(dialogues_list)
    return dialogues_list


def split_dialogue(dialogue):
    dialogue_list = [":".join(line.split(":")[1:]) for line in dialogue.split("\n") if line.strip() != ""]
    dialogue_list = [line for line in dialogue_list if line.strip() != ""]
    return dialogue_list


if __name__ == "__main__":
    dialogues = load_dialogues_from_file("data/drama_quotes_longer.txt")
    print(dialogues[:10])
    dialogues = load_dialogues_from_file("data/drama_quotes_longer.txt",
                                         do_tokenization=False)
    print(dialogues[:10])
    dialogues = load_dialogues_from_file("data/drama_quotes_longer.txt",
                                         remove_authors=True)
    print(dialogues[:10])
    dialogues = load_dialogues_from_file("data/drama_quotes_longer.txt",
                                         do_tokenization=False, remove_authors=True)
    print(dialogues[:10])
