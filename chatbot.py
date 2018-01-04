import argparse
import logging
import traceback
import sys

import helpers.spellcheck
from helpers.typos import Typos
from stupid_talker.stupid_talker import StupidTalker
from vector_sum_talker.vector_sum_proxy import VectorSumProxy
from candidates_talker.candidates_talker import CandidatesTalker
from first_year_talker.first_year_talker import FirstYearTalker

def get_talkers(exclude=[]):
    talkers = []
    def add_talker(constructor, *args, **kwargs):
        if constructor.__name__ not in exclude:
            talkers.append(constructor(*args, **kwargs))
    add_talker(VectorSumProxy, 'data/subtitles.txt')
    add_talker(VectorSumProxy, 'data/yebood.txt')
    add_talker(VectorSumProxy, 'data/dialogi_z_prozy.txt')
    add_talker(VectorSumProxy, 'data/drama_quotes.txt')
    add_talker(FirstYearTalker)
    add_talker(CandidatesTalker)
    return talkers


def get_answer(talkers, question, state):
    answers = []
    for talker in talkers:
        answers.append(talker.get_answer_helper(question, state))
    answers = sorted(answers, key=lambda answer: -answer["score"])
    return answers[0]

def update_state(state, update):
    for info in update:
        state[info] = update[info]
    #TO DO
    return state



def loop(talkers):
    state = {}
    while True:
        try:
            print ">",
            question = raw_input()
            logging.info("Question asked: %s" % question)
            answer = get_answer(talkers, question, state)
            print "<", answer["answer"]
            logging.info("Answered: %s" % answer["answer"])
            state = update_state(state, answer["state_update"])
        except KeyboardInterrupt:
            print '\nDo widzenia!'
            return
        except:
            traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chatbot',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', action='store_true', dest='debug', help='write logs to the console')
    parser.add_argument('--exclude', nargs='+', dest='exclude', default=[], help="don't use bots with specified class names")
    parser.add_argument('--spellcheck', dest='spellcheck', default='typos', help='spellchecker type (typos or none)')
    args = parser.parse_args(sys.argv[1:])
    
    if args.debug:
        logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
        logging.info('Debug mode is ON')
    else:
        logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
        
    helpers.spellcheck.init(args.spellcheck)
    loop(get_talkers(args.exclude))
