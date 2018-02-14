# import numpy as np
# import os
# import os.path
# import pickle
# import platform
# import tensorflow as tf
# import time
# from logger import log

# __SESSION_DIR = None


# def get_session_dir():
#     global __SESSION_DIR
#     if __SESSION_DIR:
#         return __SESSION_DIR
#     for _ in range(3):
#         try:
#             __SESSION_DIR = (
#                 "model_out/{}_{}/".format(
#                     platform.node(),
#                     int(time.time() % 1e6),
#                 )
#             )
#             os.makedirs(__SESSION_DIR)
#             break
#         except Exception:
#             pass
#     if os.path.isdir(__SESSION_DIR):
#         return __SESSION_DIR
#     raise Exception("Couldn't create session dir.")


# def save_model(
#     sess_,
#     args,
#     feeders,
#     lm_data,
#     ans_data=None,
#     path=None,
#     name="",
# ):
#     saver = tf.train.Saver()
#     save_path = saver.save(
#         sess_,
#         path or get_session_dir() + name,
#     )
#     _pickle.dump(
#         (args, feeders, lm_data, ans_data or {}),
#         open(save_path + ".pkl", "wb"),
#         protocol=2,
#     )
#     log("Model saved in file: {}".format(save_path))


# def report(epoch, loss, acc):
#     log("epoch: {}".format(epoch))
#     log("validation loss: {}".format(loss))
#     log("accuracy: {}".format(acc))


def pair_iterator(x, overlap=False):
    res = []
    for el in x:
        res.append(el)
        if len(res) == 2:
            yield res
            if overlap:
                res = res[1:]
            else:
                res = []


def suffix_iterator(x, min_len=1, max_len=float("inf")):
    for i in range(max(len(x) - max_len, 1), min(len(x), len(x)+1 - min_len)):
        yield x[i:]
