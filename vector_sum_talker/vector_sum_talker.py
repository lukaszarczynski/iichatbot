# -*- coding: utf-8 -*-
import idf
import logging
import numpy as np
# import traceback
import w2v_util.loader

from talker import Talker
from helpers.str_utils import to_unicode


class VectorSumTalker(Talker):
    W2V_PATH = 'big_data/word2vec-jarek/vec.bin'

    @staticmethod
    def n_max(vec, n):
        return sorted(np.argpartition(vec, -n)[-n:], key=lambda x: -vec[x])

    def preprocess(self, l):
        l = l.lower()  # noqa
        sentence = ''
        for c in l:
            if c == ' ' or c.isalnum():
                sentence += c
            elif c in '.?!':
                sentence += ' ' + c
        words = sentence.split()
        final = []
        for w in words:
            if len(final) > 0 and final[-1] + '_' + w in self.w2v.vocab_hash:
                final[-1] += '_' + w
            else:
                final.append(w)
        return ' '.join(final)

    def load_sentences(self, file, sep):
        logging.info('loading sentences from %s', file)
        with open(file) as f:
            added = False
            for l in f.readlines():
                last_added = added
                added = False
                try:
                    l = to_unicode(l).strip()  # noqa
                    if l.startswith('#') or len(l) == 0:
                        continue
                    l = l.split(sep, 1)[1]  # noqa
                    if last_added:
                        self.responses[-1] = l
                    l = self.preprocess(l)  # noqa
                    if not self.has_vector(l):
                        continue
                    self.idf.add_document(l)
                    self.sentences.append(l)
                    self.responses.append('')
                    added = True
                except Exception:
                    # traceback.print_exc()
                    pass

    def has_vector(self, s):
        return any(w in self.w2v.vocab_hash for w in s.split())

    def get_vector(self, s):
        vec = []
        all_words = s.split()
        words = filter(lambda w: w in self.w2v.vocab_hash, all_words)
        if len(words) == 0:
            return None
        vec = [self.w2v.get_vector(w) for w in words]
        vec = np.mean(vec * self.idf.idf(words)[:, None], axis=0)
        if np.linalg.norm(vec) > 1e-7:
            vec = vec / np.linalg.norm(vec)
        unknown_penalty = 0.9 ** (len(all_words) - len(words))
        length_penalty = 0.99 ** len(words)
        return vec * unknown_penalty * length_penalty

    def __init__(self, source):
        reload(idf)
        self.w2v = w2v_util.loader.get(self.W2V_PATH)
        self.sentences = []
        self.responses = []
        self.vectors = []
        self.responses_vectors = []
        self.idf = idf.IDF()

        self.load_sentences(source, ':')
        self.vectors = np.array(map(self.get_vector, self.sentences))

        self.name = 'VectorSumTalker (%s)' % source

    def my_name(self):
        return self.name
    
    def choose_average(self, weights, sentences):
        vectors = [self.get_vector(self.preprocess(s)) for s in sentences]
        avg = np.sum(filter(lambda x: x is not None, vectors), axis=0)
        avg = avg / np.linalg.norm(avg)
        results = [w * (v * avg).sum() if v is not None else 0 for w, v in zip(weights, vectors)]
        best = np.argmax(results)
        return sentences[best], results[best]

    def get_answer(self, question, *args, **kwargs):
        q = to_unicode(question['fixed_typos'])
        sentence = self.preprocess(q)
        vec = self.get_vector(sentence)
        if vec is None:
            return {
                "answer": "nic nie zrozumiałem",
                "score": 0
            }
        cosine = (self.vectors * vec.reshape(1, -1)).sum(axis=1)
        best = sorted(range(len(cosine)), key=lambda x: -cosine[x])
        best = filter(lambda i: self.responses[i] != '', best)
        if len(best) == 0:
            return {
                "answer": "nic nie zrozumiałem",
                "score": 0
            }
        
        best = best[:5]
        answer, score = self.choose_average(cosine[best], [self.responses[i] for i in best])
        return {
            "answer": answer,
            "score": score ** 0.7
        }