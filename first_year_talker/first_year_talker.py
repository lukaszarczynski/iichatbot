# -*- coding: utf-8 -*-
import json
import io
import re

from talker import Talker

class FirstYearTalker(Talker):

    def __init__(self):
        phrases = {}
        with io.open('pierwszaki.txt',mode="r", encoding="utf-8") as f:
            for line in f:
                jsonline = json.loads(line)
                phrases[re.compile(jsonline["q"])] = [jsonline["a"],jsonline["score"]]
        f.closed
        self.answers = phrases

    def get_answer(self, question):
        q = question["processedstring"]
        temp = unicode(q, "utf-8", errors="ignore")
        for key in self.answers:
            if re.match(key, temp):
                try:
                    if question["info"]["year"] == 1:
                        score = self.answers[key][1]
                    elif question["info"]["year"] == None:
                        score = 0.4
                    else:
                        score = 0.1
                except KeyError:
                    score = 0.4
                return {"answer": self.answers[key][0],
                        "score" : score
                    }
        return {
            "answer": "Nie umiem odpowiedzieć.",
            "score": 0
        }



#talk = FirstYearTalker()
#answ = talk.get_answer({"processedstring":"WYBRAĆ C CZY MOŻE PYTHON", "info" : {"semeser":None}})
#print answ["answer"]
#print answ["score"]




