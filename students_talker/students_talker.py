# coding=utf-8
import io
from talker import Talker
import os

class StudentsTalker(Talker):
    def __init__(self, module_path):
        self.db = {}
        dbfile = io.open(os.path.join(module_path, "database.txt"), mode="r", encoding="utf8")
        for entry in dbfile:
            e = entry.encode("utf-8").split(" *|* ")
            self.db[e[0]] = e[1]
        dbfile.close()

    def get_answer(self, question):
	import pdb; pdb.set_trace()
        if question.encode("utf-8") not in self.db:
            return {
                "answer": "Nie potrafię odpowiedzieć. Spróbuj zadać pytanie inaczej.",
                "score": 0
            }

        return {
            "answer": self.db[question],
            "score": 0.7,
        }
