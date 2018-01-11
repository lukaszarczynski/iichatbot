import word2vec
import logging

_loaded = {}


def get(path):
    if path not in _loaded:
        logging.info('loading word2vec word embeddings from %s', path)
        _loaded[path] = word2vec.load(path)
    return _loaded[path]
