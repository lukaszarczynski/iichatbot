# coding=utf-8
import unittest
import sys

from students_talker.students_talker import StudentsTalker


class TestChatbot(unittest.TestCase):
    def test_valid_answer(self):
        talker = StudentsTalker(sys.modules['students_talker'].__path__[0])
        answ = talker.get_answer("Czy muszę chodzić na WF")
        self.assertEqual(answ['answer'], "Bleh")


if __name__ == '__main__':
    unittest.main()
