from __future__ import print_function

import argparse
import time
import logging
import traceback
import sys

import helpers.spellcheck

from MCR_talker.MCR_talker import MCRTalker, WordVector
from candidates_talker.candidates_talker import CandidatesTalker
from first_year_talker.first_year_talker import FirstYearTalker
from interview_talker.interview_talker import InterviewTalker
# from stupid_talker.stupid_talker import StupidTalker
from vector_sum_talker.vector_sum_proxy import VectorSumProxy
from talker_grade import TalkerGrade
from helpers.progress_bar import progress_bar


def get_talkers(exclude=()):
    talkers_args = [
        # (talker_class, args, kwargs)
        (VectorSumProxy, ['data/more_subtitles.txt'], {}),
        (VectorSumProxy, ['data/yebood.txt'], {}),
        (
            VectorSumProxy,
            ['data/dialogi_z_prozy.txt'],
            {},
        ),
        (
            VectorSumProxy,
            ['data/drama_quotes.txt'],
            {},
        ),
        (FirstYearTalker, [], {}),
        (CandidatesTalker, [], {}),
        (MCRTalker, ["data/wikiquote_polish_dialogs.txt"], {"select_answer_threshold": 0.6}),
        (MCRTalker, ["data/drama_quotes_longer.txt"], {"select_answer_threshold": 0.75}),
        (MCRTalker, ["data/dialogi_z_prozy_fixed.txt"], {"select_answer_threshold": 0.8,
                                                         "filter_stopwords": False}),
        (MCRTalker, ["data/przyslowia_formatted.txt"], {"select_answer_threshold": 0.95}),
        (MCRTalker, ["data/subtitles_fixed.txt"], {"select_answer_threshold": 0.8}),
    ]
    talkers = []
    print_progress = progress_bar()
    print("Loading talkers", file=sys.stderr)
    sys.stderr.flush()
    time.sleep(0.05)
    for talker_idx, (talker_class, args, kwargs) in enumerate(talkers_args):
        if talker_class.__name__ not in exclude:
            try:
                talkers.append(talker_class(*args, **kwargs))
            except Exception:
                print(talker_class.__name__, "has crashed", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
        print_progress((talker_idx+1.) / len(talkers_args))
    print("\n", file=sys.stderr)
    sys.stderr.flush()
    time.sleep(0.05)
    return {talker.my_name(): talker for talker in talkers}


def get_answers(talkers, question, state):
    answers = {}
    for t_name in talkers:
        try:
            answer = talkers[t_name].get_answer_helper(question, state)
        except Exception:
            print(t_name, "has encounterred error", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
        else:
            answers[t_name] = answer
    return answers


def update_state(state, update):
    for info in update:
        state[info] = update[info]
    # TO DO
    return state

def doubts(answers):
    res = {}
    for key in answers:
        state = answers[key]["state_update"]
        for info in state:
            if state[info] == '?':
                res[info] = '?'
    return res

def loop(talkers, grader):
    state = {}
    interview = False
    interviewTalker = InterviewTalker()
    while True:
        try:
            print(">", end=" ")
            question = raw_input()
            logging.info("Question asked: %s" % question)
            answers = get_answers(talkers, question, state)
            to_ask = doubts(answers)
            if to_ask != {}:
                interview=True
            if interview:
                answer = interviewTalker.get_answer_helper(question, to_ask)
                answers= {interviewTalker.my_name(): answer}
                if answer["score"]<0.1:
                    interview=False

            if grader:
                answers = grader.grade(question, answers)

            answers = sorted(
                answers.values(),
                key=lambda answer: -answer["score"],
            )
            
            
            answer = answers[0]
            print("<", answer["answer"])
            logging.info("Answered: %s" % answer["answer"])
            state = update_state(state, answer["state_update"])

        except KeyboardInterrupt:
            print('\nDo widzenia!')
            return
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Chatbot',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        dest='debug',
        help='write logs to the console',
    )
    parser.add_argument(
        '-ex',
        '--exclude',
        nargs='+',
        dest='exclude',
        default=[],
        help="don't use bots with specified class names",
    )
    parser.add_argument(
        '-sp',
        '--spellcheck',
        dest='spellcheck',
        default='typos',
        help='spellchecker type (typos or none)',
    )
    parser.add_argument(
        '-gt',
        '--grade_talkers',
        action='store_true',
        dest='grade',
        help='grade talkers to assign weights further on'
    )

    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        logging.info('Debug mode is ON')
    else:
        logging.basicConfig(
            filename='chatbot.log', level=logging.INFO,
            format='%(asctime)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
    grader = TalkerGrade() if args.grade else None
    helpers.spellcheck.init(args.spellcheck)

    loop(get_talkers(args.exclude), grader)

    if args.grade:
        grader.finalize()
