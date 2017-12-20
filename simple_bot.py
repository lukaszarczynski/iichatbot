# -*- coding: utf-8 -*-

import numpy as np
import word2vec
import glob

print 'loading word vectors'
w2v = word2vec.load('big_data/word2vec-jarek/vec.bin')

sentences = []
responses = []
vectors = []

def n_max(vec, n):
    return sorted(np.argpartition(vec, -n)[-n:], key=lambda x: -vec[x])

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

def get_vector(s):
    vec = []
    for w in s.split():
        if w in w2v.vocab_hash:
            vec.append(w2v.get_vector(w))
    if len(vec) == 0: return
    vec = np.mean(vec, axis=0)
    if np.linalg.norm(vec) < 1e-7:
        return
    vec = vec / np.linalg.norm(vec)
    return vec

def load_sentences(file, sep):
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
                    responses[-1] = l
                l = preprocess(l)
                vec = get_vector(l)
                if vec is None: continue
                sentences.append(l)
                vectors.append(vec)
                responses.append('')
                added = True
            except:
                pass

for f, sep in [('data/subtitles.txt', ' '), ('data/drama_quotes.txt', ':'),
     ('data/dialogi_z_prozy.txt', ':'), ('data/yebood.txt', ':')]:
    prev = len(sentences)
    load_sentences(f, sep)
    print 'successfully loaded %d sentences from %s' % (len(sentences) - prev, f)

vectors = np.asarray(vectors)

while True:
    sentence = raw_input('>> ').decode('utf-8')
    sentence = preprocess(sentence)
    print 'po preprocessingu:', sentence
    vec = get_vector(sentence)
    if vec is None:
        print 'coś nie wyszło'
        continue
    cosine = (vectors * vec.reshape(1, -1)).sum(axis=1)
    for i in n_max(cosine, 10):
        print 'podobieństwo:', cosine[i]
        print 'zdanie:', sentences[i]
        print 'odpowiedź:', responses[i]
