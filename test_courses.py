# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

import unittest

from courses_talker.coursesDataFetcher import DataFetcher


class TestChatbot(unittest.TestCase):

    def test_downloader_initialization(self):
	down = DataFetcher();

'''    def test_description_fetcher(self):
	down = DataFetcher();
	down.fetch_course_description(down.co
'''
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
