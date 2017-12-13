import logging
from stupid_talker.stupid_talker import StupidTalker
from vector_sum_talker.vector_sum_talker import VectorSumTalker

def get_talkers():
    talkers = []
    talkers.append(StupidTalker())
    talkers.append(VectorSumTalker())
    return talkers


def get_answer(talkers, question):
    answers = []
    for talker in talkers:
        answers.append(talker.get_answer_helper(question))
    answers = sorted(answers, key=lambda answer: -answer["score"])
    return answers[0]["answer"]


def loop(talkers):
    while True:
        print ">",
        question = raw_input()
        logging.info("Question asked: %s" % question)
        answer = get_answer(talkers, question)
        print "<", answer
        logging.info("Answered: %s" % answer)


if __name__ == "__main__":
    logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    loop(get_talkers())
