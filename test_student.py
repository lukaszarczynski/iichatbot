# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

import unittest

from student_talker.student_talker import StudentTalker


class TestChatbot(unittest.TestCase):

    state = {}


    def test_initialization(self):
	st = StudentTalker();


    def test_get_answer(self):
	st = StudentTalker();
	ans = st.get_answer("Czego nauczę się na algebrze", {})
	print(ans['score'])

"""
    def test_valid_answer(self):
        st = StupidTalker("Answer.", 0.3)
        answer = st.get_answer_helper("Question")
        self.assertEqual(answer["answer"], "Answer.")
        self.assertEqual(answer["score"], 0.3)

    def test_invalid_score(self):
        st = StupidTalker("Answer.", 1.1)
        with self.assertRaises(Exception) as exp:
            st.get_answer_helper("Question")
        self.assertEqual(str(exp.exception), "invalid score")
"""

if __name__ == '__main__':
    unittest.main()
