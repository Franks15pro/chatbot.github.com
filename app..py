from flask import Flask, render_template, request, jsonify
import random
import re
from datetime import datetime

app = Flask(__name__)

# 🧠 Baza wiedzy chatbota
class ChatBot:
    def __init__(self):
        self.nazwa = "AsystentAI"
        self.kontekst = []
        
        # Wzorce odpowiedzi
        self.patterns = {
            r'(?i).*\b(cześć|hej|witaj|siema|czesc)\b.*': [
                "Cześć! 👋 Jak mogę Ci pomóc?",
                "Hej! Miło Cię widzieć! 😊",
                "Witaj! W czym mogę pomóc?"
            ],
            r'(?i).*\b(jak się nazywasz|kim jesteś|kto to)\b.*': [
                f"Jestem {self.nazwa}, Twój osobisty asystent AI! 🤖",
                f"Nazywam się {self.nazwa}. Jestem tutaj, żeby Ci pomóc! ✨"
            ],
            r'(?i).*\b(która godzina|godzina|czas)\b.*': [
                f"Aktualnie jest {datetime.now().strftime('%H:%M')} ⏰"
            ],
            r'(?i).*\b(pogoda|temperatura)\b.*': [
                "Niestety nie mam dostępu do danych o pogodzie 🌤️ Ale mogę pomóc w czymś innym!",
            ],
            r'(?i).*\b(dzięki|dziękuję|thx|thanks)\b.*': [
                "Nie ma za co! 😊",
                "Cieszę się, że mogłem pomóc! 🎉",
                "Zawsze do usług! 💪"
            ],
            r'(?i).*\b(pa|żegnam|do widzenia|nara)\b.*': [
                "Do zobaczenia! 👋",
                "Żegnam! Miło było porozmawiać! 😊",
                "Pa pa! Wracaj szybko! 🌟"
            ],
            r'(?i).*\b(pomoc|help|co umiesz)\b.*': [
                """Mogę Ci pomóc w:
                • Rozmowie i odpowiadaniu na pytania 💬
                • Podawaniu aktualnej godziny ⏰
                • Żartach i zagadkach 😄
                • I wielu innych rzeczach!""",
            ],
            r'(?i).*\b(żart|joke|dowcip|rozśmiesz)\b.*': [
                "Dlaczego programista poszedł na terapię? Bo miał za dużo problemów! 😄",
                "Co robi programista w ogrodzie? Zakłada branch! 🌳",
                "Ile programistów potrzeba do wymiany żarówki? Zero, to problem hardwarowy! 💡"
            ],
            r'(?i).*\b(tak|yes|ok|okej|dobrze)\b$': [
                "Super! 👍",
                "Rozumiem! ✅",
                "Okej! 😊"
            ],
            r'(?i).*\b(nie|no|nope)\b$': [
                "Rozumiem! 👌",
                "W porządku! ✅",
                "Okej, może innym razem! 😊"
            ],
            r'(?i).*\b(kocham cię|lubię cię)\b.*': [
                "Aww, też Cię lubię! ❤️",
                "To miłe! Dziękuję! 🥰"
            ],
            r'(?i).*\b(ile|liczba|oblicz|matematyka|policz)\b.*(\d+).*': [
                "Hmm, widzę tu liczby! Mogę pomóc z prostymi obliczeniami. Spróbuj: '5 + 3' lub '10 * 2' 🧮"
            ],
        }
        
    def oblicz(self, tekst):
        """Prosty kalkulator"""
        try:
            # Bezpieczne obliczenia (tylko podstawowe operacje)
            dozwolone = re.match(r'^[\d\s\+\-\*/\(\)\.]+$', tekst)
            if dozwolone:
                wynik = eval(tekst)
                return f"Wynik: {wynik} ✅"
        except:
            pass
        return None
    
    def odpowiedz(self, wiadomosc):
        """Generuje odpowiedź na podstawie wiadomości"""
        
        # Sprawdź czy to obliczenia
        obliczenie = self.oblicz(wiadomosc)
        if obliczenie:
            return obliczenie
        
        # Sprawdź wzorce
        for pattern, odpowiedzi in self.patterns.items():
            if re.match(pattern, wiadomosc):
                return random.choice(odpowiedzi)
        
        # Domyślne odpowiedzi
        domyslne = [
            "Ciekawe! Opowiedz mi więcej. 🤔",
            "Rozumiem. Mogę Ci w czymś pomóc? 😊",
            "To interesujące! Co jeszcze? 💭",
            "Hmm, nie jestem pewien jak na to odpowiedzieć. Spróbuj zadać inne pytanie! 🤷",
            "Jeszcze się uczę! Może zapytaj mnie o coś innego? 📚"
        ]
        
        return random.choice(domyslne)

# Inicjalizacja bota
bot = ChatBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    dane = request.json
    wiadomosc = dane.get('message', '')
    
    if not wiadomosc:
        return jsonify({'error': 'Brak wiadomości'}), 400
    
    odpowiedz = bot.odpowiedz(wiadomosc)
    
    return jsonify({
        'response': odpowiedz,
        'timestamp': datetime.now().strftime('%H:%M')
    })

if __name__ == '__main__':
    
app.run(debug=True, port=5000)