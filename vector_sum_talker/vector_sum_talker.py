from talker import Talker
import w2v_util

class VectorSumTalker(Talker):
    W2V_PATH = '../vec.bin'
    
    @staticmethod
    def n_max(vec, n):
        return sorted(np.argpartition(vec, -n)[-n:], key=lambda x: -vec[x])
    
    @staticmethod
    def preprocess(l):
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
            if len(final) > 0 and final[-1] + '_' + w in w2v.vocab_hash:
                final[-1] += '_' + w
            else: final.append(w)
        return ' '.join(final)
    
    def get_vector(self, s):
        vec = []
        for w in s.split():
            if w in w2v.vocab_hash:
                vec.append(self.w2v.get_vector(w))
        if len(vec) == 0: return
        vec = np.mean(vec, axis=0)
        if np.linalg.norm(vec) < 1e-7:
            return
        vec = vec / np.linalg.norm(vec)
        return vec
    
    def __init__(self):
        self.w2v = w2v_util.loader.get(W2V_PATH)

    def get_answer(self, question):
        return {
            "answer": self.answer,
            "score": self.score,
        }
