import argparse
import logging
import traceback
import sys

from helpers.typos import Typos
from stupid_talker.stupid_talker import StupidTalker
from vector_sum_talker.vector_sum_proxy import VectorSumProxy
#from candidates_talker.candidates_talker import CandidatesTalker
#from first_year_talker.first_year_talker import FirstYearTalker

def get_talkers(spellchecker):
    talkers = []
    #talkers.append(StupidTalker(spellchecker))
    talkers.append(VectorSumProxy('data/subtitles.txt', spellchecker))
    talkers.append(VectorSumProxy('data/yebood.txt', spellchecker))
    talkers.append(VectorSumProxy('data/dialogi_z_prozy.txt', spellchecker))
    talkers.append(VectorSumProxy('data/drama_quotes.txt', spellchecker))
    #talkers.append(CandidatesTalker(spellchecker))
    #talkers.append(FirstYearTalker(spellchecker))

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
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', action='store_true', dest='debug', help='write logs to the console')
    args = parser.parse_args(sys.argv[1:])
    
    if args.debug:
        logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    typos = Typos(morph_dictionary_path="big_data/polimorfologik-2.1.txt",
                  unigrams_path="big_data/1grams")
    loop(get_talkers(typos))
