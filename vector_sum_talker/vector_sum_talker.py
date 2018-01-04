# -*- coding: utf-8 -*-

from talker import Talker
import w2v_util.loader
import numpy as np
import traceback
import idf
import logging

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
        logging.info('loading sentences from %s', file)
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
                    if not self.has_vector(l):
                        continue
                    self.idf.add_document(l)
                    self.sentences.append(l)
                    self.responses.append('')
                    added = True
                except:
                    #traceback.print_exc()
                    pass
    
    def has_vector(self, s):
        return any(w in self.w2v.vocab_hash for w in s.split())
   
    def get_vector(self, s):
        vec = []
        words = [w for w in s.split() if w in self.w2v.vocab_hash]
        if len(words) == 0:
            return None
        vec = [self.w2v.get_vector(w) for w in words]
        vec = np.mean(vec * self.idf.idf(words)[:, None], axis=0)
        if np.linalg.norm(vec) > 1e-7:
            vec = vec / np.linalg.norm(vec)
        return vec
    
    def __init__(self, source):
        reload(idf)
        self.w2v = w2v_util.loader.get(self.W2V_PATH)
        self.sentences = []
        self.responses = []
        self.vectors = []
        self.idf = idf.IDF()
        
        self.load_sentences(source, ' ' if source == 'data/subtitles.txt' else ':')
        self.vectors = np.array(map(self.get_vector, self.sentences))
        
        self.name = 'VectorSumTalker (%s)' % source
        
    def my_name(self):
        return self.name

    def get_answer(self, question, *args, **kwargs):
        q = question['fixed_typos']
        sentence = self.preprocess(q)
        vec = self.get_vector(sentence)
        if vec is None:
            return {
                "answer": "nic nie zrozumiałem",
                "score": 0
            }
        cosine = (self.vectors * vec.reshape(1, -1)).sum(axis=1)
        best = sorted(range(len(cosine)), key=lambda x: -cosine[x])
        for i in best:
            if self.responses[i] != '':
                return {
                    "answer": self.responses[i],
                    "score": max(0, min(cosine[i], 1)),
                    "state_update": {}
                }
        return {
            "answer": "nic nie zrozumiałem",
            "score": 0
        }