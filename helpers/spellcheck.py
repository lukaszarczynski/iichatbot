from typos import Typos

cache = {}

def spellcheck_impl(_):
    raise Exception('spellcheck not initialized')

def spellcheck(x):
    if x not in cache:
        cache[x] = spellcheck_impl(x)
    return cache[x]

def init(spellcheck_type):
    global spellcheck_impl
    if spellcheck_type == 'none':
        spellcheck_impl = lambda x: x
    elif spellcheck_type == 'typos':
        typos = Typos(morph_dictionary_path="big_data/polimorfologik-2.1.txt",
                      unigrams_path="big_data/1grams")
        spellcheck_impl = typos.correct_line