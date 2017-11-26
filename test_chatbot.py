import chatbot
import unittest

from stupid_talker.stupid_talker import StupidTalker


class TestChatbot(unittest.TestCase):

    def test_one_stupid_talker(self):
        talkers = [StupidTalker()]
        self.assertEqual(chatbot.get_answer(talkers, "Question?"),
                         "Sorry, I don't know.")

    def test_two_stupid_talkers(self):
        talkers = []
        talkers.append(StupidTalker("#1", 0.4))
        talkers.append(StupidTalker("#2", 0.6))
        self.assertEqual(chatbot.get_answer(talkers, "Question?"), "#2")


if __name__ == '__main__':
    unittest.main()
