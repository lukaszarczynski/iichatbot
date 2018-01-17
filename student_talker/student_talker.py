# -*- coding: utf-8 -*-
import io
import os
import json
import operator
from difflib import SequenceMatcher
from talker import Talker

class StudentTalker(Talker):
    def __init__(self):
	with io.open(os.path.join(os.path.dirname(__file__), "data.json"), mode="r", encoding="utf-8") as f:
	    self.db = json.load(f)['data']

    def get_answer(self, question, state):
	""" A dictionary where key is an answer and the value is a distance between asked question and the one connected to answer from database"""
        question_dist = {}
        for item in self.db:
	    question_dist[item['a']] = SequenceMatcher(None, question, item['q']).ratio()
	max_ans = max(question_dist.iteritems(), key=operator.itemgetter(1))[0]
	return {
	    "answer": max_ans,
	    "score": question_dist[max_ans],
	    "state_update": {}
	}