# -*- coding: utf-8 -*-

import re
import os
from helpers.str_utils import to_unicode
from talker import Talker

my_path = os.path.dirname(__file__)

que = {
    "sex": "A tak odbiegając od tematu, jesteś kobietą?",
    "age": "Powiedz mi, ile masz lat?"
}
answ = {
    "sex": { "tak" : "female",
             "nie": "male",
             ".* nie jestem kobietą": "male",
             ".* nie jestem mężczyzną" : "female",
             ".* nie jestem dziewczyną" : "male",
             ".* nie jestem chłopakiem" : "female",
             ".* jestem kobietą": "female",
             ".* jestem mężczyzną" : "male",
             ".* jestem dziewczyną" : "female",
             ".* jestem chłopakiem" : "male",
             ".* jestem dziewczynką" : "female",
             ".* jestem chłopczkiem" : "male"
        }

    }
class InterviewTalker(Talker):
    def __init__(self):
        self.questions = que
        self.answers = answ
        self.q_asked = False
        self.keynow = "" 

    def get_answer(self, question, state):
        if self.q_asked:
            q = question["question"]
            temp = to_unicode(q)
            for key in self.answers:
                if re.match(key, temp):
                    self.q_asked = None
                    return {
                        "answer": "",
                        "score": 0,
                        "state_update": {self.keynow: (self.answers[key])}}
            return {
                "answer": "",
                "score": 0
            }
        for key in state:
            if (state[key] == "?"):
                try:
                    question = self.questions[key]
                    self.q_asked = True
                    return { "answer":question,
                             "score" : 1.0
                        }
                except KeyError:
                    return {
                        "answer": "",
                        "score": 0
                    }
                
        return {
            "answer": "",
            "score": 0
        }

