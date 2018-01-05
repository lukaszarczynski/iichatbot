from talker import Talker


class StupidTalker(Talker):
    def __init__(self, answer="Sorry, I don't know.", score=0.5):
        self.answer = answer
        self.score = score

    def get_answer(self, question):
        return {
            "answer": self.answer,
            "score": self.score,
        }
