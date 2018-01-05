# -*- coding: utf-8 -*-
import cPickle
import os.path
import platform
import random
import time


class TalkerGrade:
    GRADES_FILE = 'big_data/grades.pkl'

    def __init__(self):
        self.run_id = '{dts}_{host}'.format(
            dts=time.strftime('%S%M%H_%d%m%y'),
            host=platform.node(),
        )
        self.session = []
        self.grades = {}

    def grade(self, query, answers):
        assert len(answers) < 24
        # we only have 26 letters, we need to find better solution

        talker_answers = answers.items()
        random.shuffle(talker_answers)
        ans_dict = {chr(97 + i): ans for i, ans in enumerate(talker_answers)}

        for i in sorted(ans_dict.keys()):
            print '{let} {ans}'.format(let=i, ans=ans_dict[i][1]['answer'])

        while True:
            print 'G>',
            q = raw_input()

            grades = {k: 0 for k in answers.keys()}
            good_answers = {}

            for let in q:
                if let in [' ', '\n']:
                    continue
                elif ord(let) >= 97 and ord(let) < 97 + len(answers):
                    talker, answer = ans_dict[let]
                    grades[talker] = 1
                    good_answers[talker] = answer
                elif ord(let) >= 65 and ord(let) < 65 + len(answers):
                    talker, answer = ans_dict[let.lower()]
                    grades[talker] = 2
                    good_answers[talker] = answer
                else:
                    print(
                        'Niepoprawna ocena, spróbuj ponownie lub wpisz \h '
                        'aby uzyskać więcej informacji'
                    )
                    break
            else:
                break

            if q == '\h':
                print (
                    'Aby ocenić wpisz ciąg znaków. Dla wypowiedzi pasujących '
                    'do rozmowy napisz małą literę poprzedzającą wypowiedź, '
                    'dla wypowiedzi szczególnie dobrze pasującej do kontekstu '
                    'napisz wielką literę. \nPrzykład: \nG> Bc  <- oznacza, '
                    'że wypowiedź B bardzo pasowała jako odpowiedź, wypowiedź '
                    'c także pasowała, pozostałe wypowiedzi (w tym a) nie '
                    'pasowały wcale'
                )

        for k in grades:
            self.grades[k] = self.grades.get(k, 0) + grades[k]

        self.session.append((query, answers, grades))
        return good_answers if good_answers else answers

    def finalize(self):
        if os.path.exists(self.GRADES_FILE):
            grades_log, grades_per_talker = cPickle.load(
                open(self.GRADES_FILE, 'rb'),
            )
        else:
            grades_log, grades_per_talker = {}, {}

        grades_log[self.run_id] = self.session

        for k in self.grades:
            grades_per_talker[k] = grades_per_talker.get(k, 0) + self.grades[k]

        cPickle.dump(
            (grades_log, grades_per_talker),
            open(self.GRADES_FILE, 'wb'),
        )
