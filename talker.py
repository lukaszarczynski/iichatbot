import logging
from helpers.spellcheck import spellcheck

class Talker(object):

    def get_answer(self, question):
        """
        Return a dictionary with an answer to a given question.
        Args:
            question: dict with question and preprocessed question field
        Returns:
            dict with answer, score (between 0 and 1), and state_update field
        """
        raise NotImplementedError

    def get_answer_helper(self, question_raw, status):
        question = {
            "question": question_raw,
            "preprocessed": spellcheck(question_raw)
        }
        answer = self.get_answer(question, status)
        if "answer" not in answer.keys():
            raise Exception("answer not found")
        if "score" not in answer.keys():
            raise Exception("score not found")
        if "state_update" not in answer.keys():
            raise Exception("state update not found")
        if not (0.0 <= answer["score"] <= 1.0):
            raise Exception("invalid score")
        logging.info("%s answered: %s [%f]" % (self.__class__.__name__,
                                               answer["answer"],
                                               answer["score"]))
        return answer

