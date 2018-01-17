# -*- coding: utf-8 -*-
import json
import io
import os
import re

from helpers.str_utils import to_unicode
from talker import Talker

my_path = os.path.dirname(__file__)

answ = {
    ".* c czy .* pythona": [ "Jeśli masz doświadczenie z programowaniem, wybierz C. Jeśli nie czujesz się pewnie, lub zaczynasz, lepszy będzie Python." , 0.9 ],
    ".* c czy .* python": [ "Jeśli masz doświadczenie z programowaniem, wybierz C. Jeśli nie czujesz się pewnie, lub zaczynasz, lepszy będzie Python.", 0.9 ],
    ".* c albo .* python": [ "Jeśli masz doświadczenie z programowaniem, wybierz C. Jeśli nie czujesz się pewnie, lub zaczynasz, lepszy będzie Python." , 0.9],
    ".* c albo .* pythona": [ "Jeśli masz doświadczenie z programowaniem, wybierz C. Jeśli nie czujesz się pewnie, lub zaczynasz, lepszy będzie Python." , 0.9],
    "co to jest skos": [ "SKOS to system komunikacji na odległość ze studentami. Gdy zapiszesz się na przedmiot zostaniesz zapisany na odpowiadający mu kurs na SKOSie." , 0.9],
    "co to skos": [ "SKOS to system komunikacji na odległość ze studentami. Gdy zapiszesz się na przedmiot zostaniesz zapisany na odpowiadający mu kurs na SKOSie.", 0.9],
    "czym jest skos": [ "SKOS to system komunikacji na odległość ze studentami. Gdy zapiszesz się na przedmiot zostaniesz zapisany na odpowiadający mu kurs na SKOSie.", 0.9],
    "co wziąć na pierwszym semestrze": [ "Na pierszym semestrze dobrze jest wziąć Wstęp do Programowania, Wstęp do Informatyki i Podstawowy Warsztat Informatyka. Oprócz tego na pierwszym semestrze są obowiązkowe Logika i Analiza Matematyczna", 0.9],
    "czego uczyć się na pierwszym semestrze": [ "Na pierszym semestrze dobrze jest wziąć Wstęp do Programowania, Wstęp do Informatyki i Podstawowy Warsztat Informatyka. Oprócz tego na pierwszym semestrze są obowiązkowe Logika i Analiza Matematyczna" , 0.9],
    "co jest najtrudniejsze na pierwszym semestrze": [ "Na pierwszym semestrze najtrudniejsza jest Logika.", 0.9 ],
    "co sprawi mi trudność na pierwszym semestrze": [ "Na pierwszym semestrze najtrudniejsza jest Logika." , 0.9],
    "jaki przedmiot jest trudny na pierwszym semestrze": [ "Na pierwszym semestrze najtrudniejsza jest Logika.", 0.9 ],
    "co jest ciężkie na pierwszym semestrze": [ "Na pierwszym semestrze najtrudniejsza jest Logika." , 0.9],
    "co może być ciężkie na pierwszym semestrze": [ "Na pierwszym semestrze najtrudniejsza jest Logika." , 0.9],
    "co .* na kursie na skosie": [ "Na konkretnym kursie na SKOSie znajdziesz informacje o punktacji, listy zadań i, w większości przypadków, slajdy z wykładu." , 0.8],
    "co .* na kursie na skos": [ "Na konkretnym kursie na SKOSie znajdziesz informacje o punktacji, listy zadań i, w większości przypadków, slajdy z wykładu." , 0.8],
    "co .* na kursach na skos": [ "Na konkretnym kursie na SKOSie znajdziesz informacje o punktacji, listy zadań i, w większości przypadków, slajdy z wykładu.", 0.8 ],
    "co .* na kursach na skosie": [ "Na konkretnym kursie na SKOSie znajdziesz informacje o punktacji, listy zadań i, w większości przypadków, slajdy z wykładu." , 0.8],
    "z czego uczyć się do analizy matematycznej": [ "Dobrymi książkami do Analizy Matematycznej są podręczniki z PWr Skoczylasa.", 0.9 ],
    "z czego uczyć się do anmat": [ "Dobrymi książkami do Analizy Matematycznej są podręczniki z PWr Skoczylasa." , 0.9],
    ".* książki do analizy matematycznej": [ "Dobrymi książkami do Analizy Matematycznej są podręczniki z PWr Skoczylasa.", 0.9 ],
    ".* książki do anmat": [ "Dobrymi książkami do Analizy Matematycznej są podręczniki z PWr Skoczylasa." , 0.9],
    "kiedy będą zapisy": [ "Zapisy będą odbywać się na dniach adaptacyjnych. Wtedy też pokazane będą informacje na temat przedmiotów." , 0.7],
    "kiedy rozpoczną się zapisy": [ "Zapisy będą odbywać się na dniach adaptacyjnych. Wtedy też pokazane będą informacje na temat przedmiotów." , 0.7],
    "na jakiej stronie są zapisy": [ "Zapisy odbywają się przez serwis zapisy.ii.uni.wroc.pl. Dane do logowania rozdawane są na dniach adaptacyjnych.", 0.7 ],
    "przez jaką stronę zapisujemy się na zajęcia": [ "Zapisy odbywają się przez serwis zapisy.ii.uni.wroc.pl. Dane do logowania rozdawane są na dniach adaptacyjnych.", 0.8 ],
    "przez jaką stronę się zapisujemy": [ "Zapisy odbywają się przez serwis zapisy.ii.uni.wroc.pl. Dane do logowania będą rozdawane na dniach adaptacyjnych." , 0.8],
    "co .* zrobić żeby zaliczyć pierwszy semestr": [ "Aby zaliczyć pierwszy semestr należy zaliczyć co najmniej jeden z przedmiotów Analiza matematyczna i Logika dla informatyków. Ponadto deficyt ECTS nie może przekroczyć 10 punktów.", 0.9 ],
    "co zrobić na zaliczenie pierwszego semestru": [ "Aby zaliczyć pierwszy semestr należy zaliczyć co najmniej jeden z przedmiotów Analiza matematyczna i Logika dla informatyków. Ponadto deficyt ECTS nie może przekroczyć 10 punktów.", 0.9 ],
    "co .* zrobić żeby zaliczyć 1 semestr": [ "Aby zaliczyć pierwszy semestr należy zaliczyć co najmniej jeden z przedmiotów Analiza matematyczna i Logika dla informatyków. Ponadto deficyt ECTS nie może przekroczyć 10 punktów." , 0.9],
    "co zrobić na zaliczenie 1 semestru": [ "Aby zaliczyć pierwszy semestr należy zaliczyć co najmniej jeden z przedmiotów Analiza matematyczna i Logika dla informatyków. Ponadto deficyt ECTS nie może przekroczyć 10 punktów." , 0.9]
    }

class FirstYearTalker(Talker):
    def __init__(self):
        self.answers = answ

    def get_answer(self, question, **kwargs):
        q = question["question"]
        temp = to_unicode(q)
        for key in self.answers:
            if re.match(key, temp):
                try:
                    if question["info"]["year"] == 1:
                        score = self.answers[key][1]
                    else:
                        score = 0.2
                except KeyError:
                    score = self.answers[key][1]
                return {
                    "answer": (self.answers[key][0]).decode('utf-8'),
                    "score": score,
                }
        return {
            "answer": "Nie umiem odpowiedzieć.",
            "score": 0,
        }
