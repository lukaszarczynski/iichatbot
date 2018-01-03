import logging


class Talker(object):
    def __init__(self, spellchecker):
        self.spellchecker = spellchecker

    def get_answer(self, question, *args, **kwargs):
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
            "question": question_raw.decode('utf-8'),
            "fixed_typos": self.spellchecker.correct_line(question_raw)
        }
        question["preprocessed"] = question["fixed_typos"].split(" ")

        answer = self.get_answer(question, status)
        if "answer" not in answer.keys():
            raise Exception("answer not found")
        if "score" not in answer.keys():
            raise Exception("score not found")
        if "state_update" not in answer.keys():
            answer["state_update"] = {}
        if not (0.0 <= answer["score"] <= 1.0):
            raise Exception("invalid score")
        logging.info("%s answered: %s [%f]" % (self.__class__.__name__,
                                               answer["answer"],
                                               answer["score"]))
        return answer
