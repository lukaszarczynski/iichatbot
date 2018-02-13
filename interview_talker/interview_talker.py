# -*- coding: utf-8 -*-

import re
import os
from helpers.str_utils import to_unicode
from talker import Talker
import datetime

my_path = os.path.dirname(__file__)

que = {
    "sex": "A tak odbiegając od tematu, jesteś kobietą?",
    "age": "Powiedz mi, ile masz lat?",
    "firstyear": "Czy jesteś na pierwszym roku?",
    "candidate": "Czy chcesz rozpocząć studia w instytucie informatyki?",
    "student": "Czy jesteś naszym studentem, dłuzej niż rok?"
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
        },
    "age": [ "mam (\d+) lat",
             "mam (\d+) lata",
             "Mam (\d+) lat",
             "urodziłem się w roku (\d+).*",
             "urodziłam się w roku (\d+).*",
             "urodziłam się w (\d+).*",
             "urodziłem się w (\d+).*"
             ],
    "firstyear" : { "tak": {"firstyear": True, "student": False, "candidate": False},
                    "tak, jestem.*": {"firstyear": True, "student": False, "candidate": False},
                    "jestem.*": {"firstyear": True, "student": False, "candidate": False},
                    "nie jestem.*": {"firstyear": False},
                    "nie" : {"firstyear": False}    
        },
    "candidate" : { "tak": {"firstyear": False, "student": False, "candidate": True},
                    "tak, jestem.*": {"firstyear": False, "student": False, "candidate": True},
                    "jestem.*": {"firstyear": False, "student": False, "candidate": True},
                    "nie jestem.*": {"candidate": False},
                    "nie" : {"candidate": False}    
        },
    "student": { "tak": {"firstyear": False, "student": True, "candidate": False},
                    "tak, jestem.*": {"firstyear": False, "student": True, "candidate": False},
                    "jestem studentem pierwszego roku.*": {"firstyear": True, "student": False, "candidate": False},
                    "jestem studentką pierwszego roku.*": {"firstyear": True, "student": False, "candidate": False},
                    "jestem na pierwszym roku.*": {"firstyear": True, "student": False, "candidate": False},
                    "jestem.*": {"firstyear": False, "student": True, "candidate": False},
                    "nie jestem.*": {"student": False},
                    "nie" : {"student": False}
        }    

    }

class InterviewTalker(Talker):
    def __init__(self):
        self.questions = que
        self.answers = answ
        self.q_asked = False
        self.understandfail = False
        self.keynow = ""
        
    def get_answer(self, question, status):
        if self.q_asked:                        
            temp = question["question"]
            q = to_unicode(temp)
            if self.keynow == "sex":
                return self.recsex(q)
            elif self.keynow == "age":
                return self.recage(q)
            elif self.keynow == "firstyear":
                return self.recfirst(q)
            elif self.keynow == "candidate":
                return self.reccand(q)
            elif self.keynow == "student":
                return self.recstudent
            else:
                return {
                    "answer": "Brak kategorii",
                    "score": 0
                }

             
        #zadanie pierwszego pytania
        for key in status:
            if (status[key] == "?"):
                try:
                    question = self.questions[key]
                    self.keynow = key
                    self.q_asked = True
                    return { "answer":question.decode('utf-8'),
                             "score" : 1.0
                        }
                except KeyError:
                    return {
                        "answer": "Nie wiem, o co mnie pytasz.",
                        "score": 0
                    }
        #nie ma nic do powiedzenia
        return {
            "answer": "Tu nie powinnismy dojsc nigdy",
            "score": 0
        }
    #zrozumienie odpowiedzi płci
    def recsex(self, question):
            for key in self.answers["sex"]:
                if re.match(key, question):
                    self.q_asked = None
                    sex = self.answers["sex"][key]
                    if sex == "female":
                        answ = "Dobrze. Rozumiem, że jesteś kobietą."
                    else:
                        answ = "Dobrze. Rozumiem, że jesteś mężczyzną."
                    return {
                        "answer": answ.decode('utf-8'),
                        "score": 0, #0 na zakończenie
                        "state_update": {"sex": sex}
                        }
            if self.understandfail:
                return {
                "answer": "Nie potrafię ci pomóc.".decode('utf-8'),
                "score": 0
            }
            else:
                self.understandfail= True    
            return {
                "answer": "Niestety nie zrozumiałem.".decode('utf-8'),
                "score": 1
            }
    def recage(self, question):
        for key in self.answers["age"]:
            match = re.match(key, question)
            if match:
                self.q_asked = None
                stringage = match.group(1)
                intage = int(stringage)
                if intage > 1000:
                    now = datetime.datetime.now()
                    intage = now.year - intage
                answ = "Rozumiem, że masz " + str(intage) + " lat"
                return {
                        "answer": answ.decode('utf-8'),
                        "score": 0, #0 na zakończenie
                        "state_update": {"age": intage}
                        }
        if self.understandfail:
                return {
                "answer": "Nie potrafię ci pomóc.".decode('utf-8'),
                "score": 0
            }
        else:
                self.understandfail= True  
        return {
                "answer": "Niestety nie zrozumiałem.".decode('utf-8'),
                "score": 1
            }
    def recfirst(self, question):
        for key in self.answers["firstyear"]:
            if re.match(key, question):
                ans = self.answers["firstyear"][key]
                self.q_asked = None
                if ans["firstyear"]:
                    answ = "Zrozumiałem, że jesteś studentem pierwszego roku ii."
                else:
                    answ = "Zrozumiałem, że nie jesteś studentem pierwszego roku ii."
                return {
                        "answer": answ.decode('utf-8'),
                        "score": 0, #0 na zakończenie
                        "state_update": ans
                        }
        if self.understandfail:
                return {
                "answer": "Nie potrafię ci pomóc.".decode('utf-8'),
                "score": 0
            }
        else:
                self.understandfail= True  
        return {
                "answer": "Niestety nie zrozumiałem.".decode('utf-8'),
                "score": 1
            }
    def reccand(self, question):
        for key in self.answers["candidate"]:
            if re.match(key, question):
                ans = self.answers["candidate"][key]
                self.q_asked = None
                if ans["candidate"]:
                    answ = "Zrozumiałem, że jesteś kandydatem na studia w ii."
                else:
                    answ = "Zrozumiałem, że nie jesteś kandydatem na studia w ii."
                return {
                        "answer": answ.decode('utf-8'),
                        "score": 0, #0 na zakończenie
                        "state_update": ans
                        }
        if self.understandfail:
                return {
                "answer": "Nie potrafię ci pomóc..decode('utf-8')",
                "score": 0
            }
        else:
                self.understandfail= True  
        return {
                "answer": "Niestety nie zrozumiałem.".decode('utf-8'),
                "score": 1
            }
    def recstudent(self, question):
        for key in self.answers["student"]:
            if re.match(key, question):
                ans = self.answers["student"][key]
                self.q_asked = None
                if ans["student"]:
                    answ = "Zrozumiałem, że jesteś studentem ii."
                else:
                    answ = "Zrozumiałem, że nie jesteś studentem ii."
                return {
                        "answer": answ.decode('utf-8'),
                        "score": 0, #0 na zakończenie
                        "state_update": ans
                        }
        if self.understandfail:
                return {
                "answer": "Nie potrafię ci pomóc..decode('utf-8')",
                "score": 0
            }
        else:
                self.understandfail= True  
        return {
                "answer": "Niestety nie zrozumiałem.".decode('utf-8'),
                "score": 1
            }
