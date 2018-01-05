from typos import Typos

class Spellchecker:
    @classmethod
    def __init__(cls, type_):
        cls.cache = {}
        if type_ == 'typos':
            typos = Typos(
                morph_dictionary_path="big_data/polimorfologik-2.1.txt",
                unigrams_path="big_data/1grams",
            )
            cls.SPELLCHECK_IMPL = typos.correct_line
        elif type_ == 'none':
            cls.SPELLCHECK_IMPL = staticmethod(lambda x: x)
        else:
            raise Exception('Invalid spellchecker type')

    @classmethod
    def fix(cls, s):
        if s not in cls.cache:
            cls.cache[s] = cls.SPELLCHECK_IMPL(s)
        return cls.cache[s]

    @classmethod
    def get(cls):
        return cls.SPELLCHECK_IMPL
