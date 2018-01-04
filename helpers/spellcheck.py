from typos import Typos

typos = Typos(morph_dictionary_path="big_data/polimorfologik-2.1.txt",
                  unigrams_path="big_data/1grams")

def spellcheck(line):
    return typos.correct_line(line)