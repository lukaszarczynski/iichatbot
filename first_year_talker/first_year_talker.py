# -*- coding: utf-8 -*-
import json
import io
import os
import re

from helpers.str_utils import to_unicode
from talker import Talker

my_path = os.path.dirname(__file__)


class FirstYearTalker(Talker):
    def __init__(self):
        phrases = {}
        with io.open(
            os.path.join(my_path, 'pierwszaki.txt'),
            mode="r",
            encoding="utf-8"
        ) as f:
            for line in f:
                jsonline = json.loads(line)
                phrases[re.compile(jsonline["q"])] = [
                    jsonline["a"],
                    jsonline["score"]
                ]
        f.closed
        self.answers = phrases

    def get_answer(self, question, **kwargs):
        q = question["question"]
        temp = to_unicode(q)
        for key in self.answers:
            if re.match(key, temp):
                try:
                    if question["info"]["year"] == 1:
                        score = self.answers[key][1]
                    else:
                        score = 0.2
                except KeyError:
                    score = self.answers[key][1]
                return {
                    "answer": self.answers[key][0],
                    "score": score,
                }
        return {
            "answer": "Nie umiem odpowiedzieć.",
            "score": 0,
        }


# talk = FirstYearTalker()
# answ = talk.get_answer(
#     {
#         "processedstring": "WYBRAĆ C CZY MOŻE PYTHON",
#         "info": {"semeser": None},
#     },
# )
# print answ["answer"]
# print answ["score"]
