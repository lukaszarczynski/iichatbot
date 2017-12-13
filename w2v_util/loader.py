import word2vec

_loaded = {}

def get(path):
    if path not in _loaded:
        print 'loading word2vec word embeddings from', path
        _loaded[path] = word2vec.load(path)
    return _loaded[path]