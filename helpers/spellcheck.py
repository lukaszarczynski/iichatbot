from typos import Typos


class Spellchecker:
    SPELLCHECK_IMPL = staticmethod(lambda x: x) # noqa

    @classmethod
    def init(cls, type_):
        if type_ == 'typos':
            typos = Typos(
                morph_dictionary_path="big_data/polimorfologik-2.1.txt",
                unigrams_path="big_data/1grams",
            )
            cls.SPELLCHECK_IMPL = typos.correct_line
        else:
            raise Exception('niepoprawny typ spellcheckera')

    @classmethod
    def fix(cls, s):
        return cls.SPELLCHECK_IMPL(s)

    @classmethod
    def get(cls):
        return cls.SPELLCHECK_IMPL
