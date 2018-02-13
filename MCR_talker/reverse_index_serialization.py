import os.path
import cPickle as pickle

from enum import Enum


class IndexType(Enum):
    REVERSE = 1
    POSITIONAL = 2
    POSITIONAL_WITHOUT_LEMATIZATION = 3
    POSITIONAL_ENCODED = 4
    TITLE_4GRAM = 5
    DIALOGUE = 6


EXTENSIONS = {
    IndexType.REVERSE: ".rvi",
    IndexType.POSITIONAL: ".pos",
    IndexType.POSITIONAL_WITHOUT_LEMATIZATION: ".pwl",
    IndexType.POSITIONAL_ENCODED: ".enc",
    IndexType.TITLE_4GRAM: ".4gr",
    IndexType.DIALOGUE: ".drvi"
}


def store_reverse_index(collection_path, create_reverse_index_function, index_creation_arguments=(),
                        index_type=IndexType.REVERSE):
    index = dict(create_reverse_index_function(collection_path, *index_creation_arguments)[0])
    with open(collection_path + EXTENSIONS[index_type], "wb") as file:
        pickle.dump(index, file)
    return index


def load_reverse_index(collection_path, index_type=IndexType.REVERSE):
    with open(collection_path + EXTENSIONS[index_type], "rb") as file:
        stored_index = pickle.load(file)
    return stored_index


def reverse_index_created(collection_path, index_type=IndexType.REVERSE):
    return os.path.isfile(collection_path + EXTENSIONS[index_type])
