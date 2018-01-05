# iichatbot
Chatbot Instytutu Informatyki

# Uruchomienie bota

Zakładamy, że jesteście zalogowani przez ssh na któryś z komputerów w sali **110** lub **137** i znajdujecie się w katalogu `iichatbot`.

Dodanie pythona do ścieżki uruchomieniowej (po każdym zalogowaniu):
```
source set-env.sh
```

Zainstalowanie zależności (wymagane tylko raz, chyba że dojdą kolejne zależności):
```
pip install --user -r requirements.txt
```

Uruchomienie chatbota (bot potrzebuje paru minutz żeby się załadować):
```
python chatbot.py
```

Jeśli nie chcecie tyle czekać, można dezaktywować vector sum talkery (w taki sam sposób można postąpić też z innymi talkerami) i/lub spellchecking
```
python chatbot.py --exclude VectorSumProxy
python chatbot.py --spellcheck none
python chatbot.py --spellcheck none --exclude VectorSumProxy
```

Uruchomienie chatbota z wypisywaniem logów do terminala
```
python chatbot.py --debug
```

Wyświetlenie listy dostępnych opcji
```
python chatbot.py --help
```
