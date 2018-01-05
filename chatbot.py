import argparse
import helpers.spellcheck
import logging
import traceback
import sys

from candidates_talker.candidates_talker import CandidatesTalker
from first_year_talker.first_year_talker import FirstYearTalker
# from stupid_talker.stupid_talker import StupidTalker
from vector_sum_talker.vector_sum_proxy import VectorSumProxy
from talker_grade import TalkerGrade


def get_talkers(exclude=None):
    talkers = [
        # (name, fun, args, kwargs)
        ('vector_subtitles', VectorSumProxy, ['data/subtitles.txt'], {}),
        ('vector_yebood', VectorSumProxy, ['data/yebood.txt'], {}),
        (
            'vector_dialogi_proza',
            VectorSumProxy,
            ['data/dialogi_z_prozy.txt'],
            {},
        ),
        (
            'vector_dialogi_dramat',
            VectorSumProxy,
            ['data/drama_quotes.txt'],
            {},
        ),
        ('first_year', FirstYearTalker, [], {}),
        ('candidate', CandidatesTalker, [], {}),
    ]
    return {
        name: fun(*args, **kwargs)
        for name, fun, args, kwargs in talkers
        if fun.__name__ not in (exclude or [])
    }


def get_answers(talkers, question, state):
    return {
        t_name: talkers[t_name].get_answer_helper(question, state)
        for t_name in talkers
    }


def update_state(state, update):
    for info in update:
        state[info] = update[info]
    # TO DO
    return state


def loop(talkers, grader):
    state = {}
    while True:
        try:
            print ">",
            question = raw_input()
            logging.info("Question asked: %s" % question)
            answers = get_answers(talkers, question, state)

            if grader:
                answers = grader.grade(question, answers)

            answers = sorted(
                answers.values(),
                key=lambda answer: -answer["score"],
            )
            answer = answers[0]
            print "<", answer["answer"]
            logging.info("Answered: %s" % answer["answer"])
            state = update_state(state, answer["state_update"])

        except KeyboardInterrupt:
            print '\nDo widzenia!'
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
    helpers.spellcheck.Spellchecker.init(args.spellcheck)

    loop(get_talkers(args.exclude), grader)

    if args.grade:
        grader.finalize()
