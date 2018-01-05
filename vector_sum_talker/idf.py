import numpy as np
from collections import Counter


class IDF:
    def __init__(self):
        self.df = Counter()
        self.doc = 0

    def add_document(self, doc):
        self.doc += 1
        self.df.update(set(doc.split()))

    def idf(self, words):
        eps = 1
        df = np.array([self.df[w] for w in words], dtype='float32')
        return np.log((self.doc + eps) / (df + eps))
