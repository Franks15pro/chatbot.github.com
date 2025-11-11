from flask import Flask, render_template, request, jsonify
import random
import re
from datetime import datetime

app = Flask(__name__)

class ChatBot:
    def __init__(self):
        self.nazwa = "AI Assistant"
        self.kontekst = []
        
        self.patterns = {
            r'(?i).*\b(cześć|hej|witaj|siema|czesc|hello|hi)\b.*': [
                "Witaj! W czym mogę Ci dzisiaj pomóc?",
                "Dzień dobry! Jak mogę być pomocny?",
                "Cześć! Cieszę się, że do mnie napisałeś."
            ],
            r'(?i).*\b(jak się nazywasz|kim jesteś|kto to)\b.*': [
                "Jestem AI Assistant, zaawansowany chatbot stworzony, aby Ci pomagać.",
                "Nazywam się AI Assistant. Jestem Twoim wirtualnym asystentem."
            ],
            r'(?i).*\b(która godzina|godzina|czas|time)\b.*': [
                f"Obecnie jest {datetime.now().strftime('%H:%M')}.",
                f"Godzina: {datetime.now().strftime('%H:%M:%S')}"
            ],
            r'(?i).*\b(data|dzisiaj|dziś)\b.*': [
                f"Dzisiaj jest {datetime.now().strftime('%d.%m.%Y')}.",
            ],
            r'(?i).*\b(dzięki|dziękuję|thx|thanks|thank you)\b.*': [
                "Nie ma za co, zawsze chętnie pomogę.",
                "Cieszę się, że mogłem pomóc!",
                "Do usług!"
            ],
            r'(?i).*\b(pa|żegnam|do widzenia|nara|bye)\b.*': [
                "Do zobaczenia! Wróć, gdy będziesz czegoś potrzebować.",
                "Żegnam! Miło było porozmawiać.",
                "Do widzenia! Powodzenia!"
            ],
            r'(?i).*\b(pomoc|help|co umiesz|funkcje)\b.*': [
                """Oto lista moich możliwości:

• Rozmowa i odpowiadanie na pytania
• Proste obliczenia matematyczne (np. 15 * 3)
• Podawanie aktualnej daty i godziny
• Udzielanie informacji i wsparcia
• Zapamiętywanie kontekstu rozmowy

Czym mogę Ci pomóc?""",
            ],
            r'(?i).*\b(żart|joke|dowcip|rozśmiesz)\b.*': [
                "Dlaczego programiści preferują tryb ciemny? Bo światło przyciąga błędy.",
                "Ile czasu zajmuje nauczenie się programowania? 10 lat albo całe życie, w zależności kogo zapytasz.",
                "Najlepsze w byciu programistą? Możesz płakać w pracy i wszyscy myślą, że debugujesz."
            ],
            r'(?i).*\b(tak|yes|ok|okej|dobrze|zgoda)\b$': [
                "Rozumiem.",
                "Świetnie!",
                "W porządku."
            ],
            r'(?i).*\b(nie|no|nope)\b$': [
                "Jasne, w takim razie w czym mogę pomóc?",
                "Rozumiem.",
                "W porządku."
            ],
            r'(?i).*\b(ile|liczba|oblicz|matematyka|policz|calculate)\b.*(\d+).*': [
                "Widzę liczby w Twojej wiadomości. Mogę wykonać obliczenia - wystarczy napisać np. '25 + 17' lub '144 / 12'"
            ],
            r'(?i).*\b(pogoda|temperatura|weather)\b.*': [
                "Nie mam dostępu do aktualnych danych pogodowych, ale mogę pomóc Ci w innych kwestiach.",
            ],
            r'(?i).*\b(kto cię stworzył|autor|creator)\b.*': [
                "Zostałem stworzony jako zaawansowany chatbot przy użyciu Pythona i Flask.",
            ],
        }
        
    def oblicz(self, tekst):
        """Prosty kalkulator matematyczny"""
        try:
            dozwolone = re.match(r'^[\d\s\+\-\*/\(\)\.]+$', tekst)
            if dozwolone:
                wynik = eval(tekst)
                return f"Wynik: {wynik}"
        except:
            pass
        return None
    
    def odpowiedz(self, wiadomosc):
        """Generuje odpowiedź na podstawie wiadomości użytkownika"""
        
        obliczenie = self.oblicz(wiadomosc)
        if obliczenie:
            return obliczenie
        
        for pattern, odpowiedzi in self.patterns.items():
            if re.match(pattern, wiadomosc):
                return random.choice(odpowiedzi)
        
        domyslne = [
            "To interesujące. Opowiedz mi więcej.",
            "Rozumiem. W czym mogę Ci pomóc?",
            "Hmm, nie jestem pewien jak najlepiej na to odpowiedzieć. Może spróbuj przeformułować pytanie?",
            "Ciekawe spostrzeżenie. Co jeszcze chciałbyś wiedzieć?",
            "Wciąż się uczę. Czy mogę pomóc Ci w czymś innym?"
        ]
        
        return random.choice(domyslne)

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
