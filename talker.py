import logging


class Talker(object):

    def get_answer(self, question):
        """
        Return a dictionary with an answer to a given question.
        Args:
            question: dict with question field
        Returns:
            dict with answer and score (between 0 and 1) field
        """
        raise NotImplementedError

    def get_answer_helper(self, question_raw):
        question = {
            "question": question_raw,
        }
        answer = self.get_answer(question)
        if "answer" not in answer.keys():
            raise Error("answer not found")
        if "score" not in answer.keys():
            raise Error("score not found")
        if not (0.0 <= answer["score"] <= 1.0):
            raise Error("invalid score")
        logging.info("%s answered: %s [%f]" % (self.__class__.__name__,
                                               answer["answer"],
                                               answer["score"]))
        return answer
