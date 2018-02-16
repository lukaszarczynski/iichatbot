# -*- coding: utf-8 -*-
import helper
import numpy as np
import pickle
import seq2seq
import tensorflow as tf
from talker import Talker


class SeqTalker(Talker):
    def __init__(self, model_path="big_data/seq2seq"):
        self.params, self.data, self.lm_data, self.ans_data = pickle.load(
            open("{}/lm.pkl".format(model_path), "rb"),
        )
        self.model = seq2seq.model(
            dict_size=self.params.word_limit + self.params.suff_limit,
            unroll_len=self.params.unroll_len,
            depth=self.params.depth,
            hidden_size=self.params.hidden_size,
        )
        self.vocab = self.lm_data["vocab"]
        self.suffs = self.lm_data["suffs"]

        self.inv_vocab = {v: k for k, v in self.vocab.items()}
        self.inv_vocab[0] = "<end>"
        self.inv_vocab[1] = "<unk>"
        saver = tf.train.Saver()
        self.sess = tf.Session()
        saver.restore(self.sess, "{}/lm".format(model_path))

    def word_to_tok(self, w):
        if w in self.vocab:
            return self.vocab[w]

        for suff in helper.suffix_iterator(w):
            if suff in self.suffs:
                return self.suffs[suff] + len(self.vocab)

        return self.vocab["<unk>"]

    def my_name(self):
        return "seq_talker"

    def get_answer(self, question, status):
        words = question["fixed_typos"].strip().lower().split(" ")
        unroll_len = self.params.unroll_len
        X = [
            self.word_to_tok(word)
            for word in words
        ] + [0]*unroll_len
        mask = [1] * len(words) + [0] * unroll_len
        X, mask = np.array(X[:unroll_len]), np.array(mask[:unroll_len])
        X, mask = X.reshape([1, -1]), mask.reshape([1, -1])

        res, = self.sess.run(
            fetches=[
                self.model.lm_result,
            ],
            feed_dict={
                self.model.X: X,
                self.model.input_mask: mask,
            },
        )
        res = np.argmax(res[0], axis=-1)
        it = None
        for i, x in enumerate(res):
            if x == 0:
                it = i
                break
        if it is not None:
            res = res[:it]
        return {
            "answer": " ".join([self.inv_vocab[i] for i in res]),
            "score": 0.01,
        }
