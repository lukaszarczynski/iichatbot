#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from talker import Talker
questions = {
    'kierun': 'kierunki',
    'co.*isim': 'co isim',
    'czym .* isim': 'co isim',
    'ile.*studentów .* isim': 'ile isim',
    'ile .* osób .* isim': 'ile isim',
    'ile.*trwają': 'dlugosc',
    'jak długie': 'dlugosc',
    'matur': 'matura',
    'mnożnik.*informatyk': 'mnoznik inf',
    'mnożnik.*mat': 'mnoznik mat',
    'mnożnik.*język': 'mnoznik jezyk',
    'mnożnik  .* angielsk': 'mnoznik jezyk',
    'mnożnik  .* niemieck': 'mnoznik jezyk',
    'mnożnik.*fizy': 'mnoznik dod',
    'mnożnik  .* dodatkow': 'mnoznik dod',
    'mnożnik  .* ścis': 'mnoznik dod',
    'trzeci.*przedmiot': 'przedmiot dodatkowy',
    'przedmiot .* dodatkowy': 'przedmiot dodatkowy',
    'mini.*infor': 'prog minimalny inf',
    'mini.*isim': 'prog minimalny isim',
    'progi': 'przeszle progi',
    'olimpia': 'olimpiady',
    'harmonogram': 'harmonogram',
    'daty': 'harmonogram',
    'stron': 'strona',
    'forum': 'forum',
    'aceboo': 'fb',
    'fb': 'fb',
    'przedmioty': 'przedmioty',
    'zaję': 'przedmioty',
}

tagToAnswer = {
    'kierunki': (
        'Na naszym wydziale oferujemy trzy kierunki: matematyka, informatyka '
        'i isim.'
    ),
    'co isim': (
        'ISIM to indywidualne studia Indywidualne Studia '
        'Informatyczno-Matematyczne.'
    ),
    'ile isim': 'Na ISIM przyjmowanych jest co najwyżej 25 studentów.',
    'dlugosc': (
        'Studia pierwszego stopnia trwają 3 lata (licencjackie) lub 3,5 roku '
        '(inżynierskie).'
    ),
    'matura': (
        'Na Twój wynik punktowy składać się będą odpowiednio przemnożone '
        'wyniki z matur z informatyki, matematyki, języka nowożytniego i '
        'przedmiotu ścisłego.'
    ),
    'mnoznik inf': 'Poziom postawowy: 0.5 Poziom rozszerzony: 1.0',
    'mnoznik mat': 'Poziom postawowy: 0.5 Poziom rozszerzony: 2.0',
    'mnoznik jezyk': 'Poziom postawowy: 0.2 Poziom rozszerzony: 0.4',
    'mnoznik dod': 'Poziom postawowy: 0.25 Poziom rozszerzony: 0.5',
    'przedmiot dodatkowy': (
        'Jako trzeci liczący się do rekrutacji przedmiot możesz wybrać '
        'matematykę, fizykę albo informatykę'
    ),
    'prog minimalny inf': (
        'Na studia kwalifikowani są wyłącznie kandydaci, którzy uzyskali co '
        'najmniej 115 punktów rekrutacyjnych oraz co najmniej 30 procent '
        'punktów z egzaminu maturalnego z matematyki na poziomie rozszerzonym '
        'lub co najmniej 70 procent punktów z egzaminu maturalnego z '
        'matematyki na poziomie podstawowym.'
    ),
    'prog minimalny isim': (
        'Aby zostać zakwalifikowanym na ISIM trzeba zdobyć co najmniej 210 '
        'punktów rekrutacyjnych.'
    ),
    'przeszle progi': (
        'Próg przyjęcia w roku 2017 wynosił 204 punkty, w 2016 150 punktów, a '
        'w 2015 120 punktów.'
    ),
    'olimpiady': (
        'Laureaci i finaliści Olimpiady Informatycznej, Olimpiady Fizycznej '
        'oraz Olimpiady Matematycznej są przyjmowani na podstawie dokumentu '
        'wydanego przez komitet organizacyjny danej olimpiady oraz złożonych '
        'dokumentów. Uprawnienia przyznawane są kandydatowi w roku zdania '
        'matury.'
    ),
    'harmonogram': (
        'Dokładny harmonogram rekrutacji możesz sprawdzić na stronie '
        'http://www.rekrutacja.uni.wroc.pl./kierunek.html?id=7920#harmonogram'
    ),
    'dokumenty': (
        'Musisz złożyć podpisane podanie o przyjęcie na studia, kserokopię '
        'świadectwa dojrzałości, kserokopię dokumentu tożsamości oraz jedną '
        'fotografię '
    ),
    'zdjecie wymogi': (
        'Zdjęcie które dołączasz w sytemie IRK powinno być aktualne, '
        'kolorowe, w rozdzielczości 400x500 pikseli w formacie JPG, spełniać '
        'wymogi zdjęcia do dowodu osobistego. Zdjęcie dostarczone z innymi '
        'wymaganymi dokumentami powino być identyczne z tym w systemie IRK'
    ),
    'skladanie dokumentow': (
        'Nie trzeba składać dokumentów ososbiście jednak muszą być one '
        'poświadczone notarialnie lub osoba składająca powinna posiadać '
        'pełnomocnictwo.'
    ),
    'termin dokumentow': (
        'Decydująca jest data dostarczenia dokumentów, a nie data stempla '
        'pocztowego czy termin nadania przesyłki'
    ),
    'konto': (
        'Opłatę wnosi się na indywidualny numer rachunku bankowego, widoczny '
        'w systemie IRK.',
    ),
    'wypisywanie': (
        'Wyniki matur zostaną uzupełnione automatycznie i nie należy wpisywać '
        'ich ręcznie'
    ),
    'strona': 'http://www.ii.uni.wroc.pl/',
    'forum': 'https://forum.iiuwr.me/',
    'fb': (
        'Na Facebooku są obecnie dwie działające grupy - jedna dla pierwszego '
        'roku, a druga dla reszty studentów: '
        'https://www.facebook.com/groups/1509427755955548/ '
        'https://www.facebook.com/groups/1458898207762366/'
    ),
    'przedmioty': 'https://zapisy.ii.uni.wroc.pl/courses/'
}


class CandidatesTalker(Talker):

    def __init__(self, answer="Przepraszam ale nie mogę Ci pomóc.", score=0.7):
        self.answer = answer
        self.score = score

    def get_answer(self, question, status):
        self.answer = self.ask(question)
        if(self.answer == "Przepraszam ale nie mogę Ci pomóc."):
        	self.score = 0.01
        return {
            "answer": self.answer,
            "score": self.score
        }

    def match(self, q, pattern):
        pat = re.compile(pattern)
        return (pat.search(q) is not None)

    def ask(self, q):
        for possibility in questions:
            if self.match(q['question'], possibility):
                tag = questions[possibility]
                return tagToAnswer[tag]
        return "Przepraszam ale nie mogę Ci pomóc."

# while(True):
#     user=raw_input()
#     if user == 'akubik':
#         break
#     print ask(user)
