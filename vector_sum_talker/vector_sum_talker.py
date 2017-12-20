# -*- coding: utf-8 -*-

from talker import Talker
import w2v_util.loader
import numpy as np
import traceback

class VectorSumTalker(Talker):
    W2V_PATH = 'big_data/word2vec-jarek/vec.bin'
    
    @staticmethod
    def n_max(vec, n):
        return sorted(np.argpartition(vec, -n)[-n:], key=lambda x: -vec[x])
    
    def preprocess(self, l):
        l = l.lower()
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
            else: final.append(w)
        return ' '.join(final)
    
    def load_sentences(self, file, sep):
        print 'loading sentences from', file
        with open(file) as f:
            added = False
            for l in f.readlines():
                last_added = added
                added = False
                try:
                    l = l.decode('utf-8').strip()
                    if l.startswith('#') or len(l) == 0: continue
                    l = l.split(sep, 1)[1]
                    if last_added:
                        self.responses[-1] = l
                    l = self.preprocess(l)
                    vec = self.get_vector(l)
                    if vec is None: continue
                    self.sentences.append(l)
                    self.vectors.append(vec)
                    self.responses.append('')
                    added = True
                except:
                    #traceback.print_exc()
                    pass
    
    def get_vector(self, s):
        vec = []
        for w in s.split():
            if w in self.w2v.vocab_hash:
                vec.append(self.w2v.get_vector(w))
        if len(vec) == 0: return
        vec = np.mean(vec, axis=0)
        if np.linalg.norm(vec) < 1e-7:
            return
        vec = vec / np.linalg.norm(vec)
        return vec
    
    def __init__(self, source):
        self.w2v = w2v_util.loader.get(self.W2V_PATH)
        self.sentences = []
        self.responses = []
        self.vectors = []

        self.load_sentences(source, ' ' if source == 'data/subtitles.txt' else ':')
        print 'successfully loaded %d sentences from %s' % (len(self.sentences), source)

    def get_answer(self, question):
        q = question['question'].decode('utf-8')
        sentence = self.preprocess(question['question'])
        print sentence
        vec = self.get_vector(sentence)
        if vec is None:
            return {
                "answer": "nic nie zrozumiałem",
                "score": 0
            }
        cosine = (self.vectors * vec.reshape(1, -1)).sum(axis=1)
        best = self.n_max(cosine, 1)[0]
        print self.responses[best]
        print 'most similar question', self.sentences[best]
        return {
            "answer": self.responses[best],
            "score": cosine[best],
            "state_update": {}
        }
