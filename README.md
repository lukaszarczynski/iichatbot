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

Uruchomienie chatbota (bot potrzebuje ~ 2 minut żeby się załadować):
```
python chatbot.py
```

Uruchomienie chatbota z wypisywaniem logów do terminala
```
python chatbot.py --debug
```
