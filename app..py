from flask import Flask, render_template, request, jsonify
import random
import re
from datetime import datetime
import uuid
from database import Database
from ml_model import MLChatBot

app = Flask(__name__)

db = Database()
ml_bot = MLChatBot()

class ChatBot:
    def __init__(self):
        self.nazwa = "AI Assistant"
        self.session_conversations = {}
        
        self.patterns = {
            r'(?i).*\b(cześć|hej|witaj|siema|czesc|hello|hi)\b.*': [
                "Witaj! W czym mogę Ci dzisiaj pomóc?",
                "Dzień dobry! Jak mogę być pomocny?",
                "Cześć! Cieszę się, że do mnie napisałeś."
            ],
            r'(?i).*\b(jak się nazywasz|kim jesteś|kto to)\b.*': [
                "Jestem AI Assistant z uczeniem maszynowym. Uczę się z każdej rozmowy!",
                "Nazywam się AI Assistant. Staję się mądrzejszy z każdą rozmową."
            ],
            r'(?i).*\b(która godzina|godzina|czas|time)\b.*': [
                f"Obecnie jest {datetime.now().strftime('%H:%M')}."
            ],
            r'(?i).*\b(data|dzisiaj|dziś)\b.*': [
                f"Dzisiaj jest {datetime.now().strftime('%d.%m.%Y')}."
            ],
            r'(?i).*\b(dzięki|dziękuję|thx|thanks)\b.*': [
                "Nie ma za co, zawsze chętnie pomogę.",
                "Cieszę się, że mogłem pomóc!"
            ],
            r'(?i).*\b(pa|żegnam|do widzenia|bye)\b.*': [
                "Do zobaczenia! Pamiętaj ocenić naszą rozmowę.",
                "Żegnam! Dzięki za feedback - uczę się dzięki Tobie!"
            ],
            r'(?i).*\b(pomoc|help|co umiesz|funkcje)\b.*': [
                f"""Jestem chatbotem z UCZENIEM MASZYNOWYM!

Moje możliwości:
• Rozmowa i odpowiadanie na pytania
• UCZĘ SIĘ z każdej rozmowy (dzięki Twojemu feedbackowi)
• Obliczenia matematyczne (np. 25 * 4)
• Podawanie daty i godziny
• Zapamiętywanie kontekstu

Statystyki:
• Rozmów: {db.get_statistics()['total_conversations']}
• Wyuczonych odpowiedzi: {db.get_statistics()['learned_responses']}

Oceń moje odpowiedzi aby pomóc mi się uczyć!""",
            ],
            r'(?i).*\b(statystyki|stats|uczenie)\b.*': [
                self.get_stats_message()
            ],
        }
    
    def get_stats_message(self):
        stats = db.get_statistics()
        return f"""Statystyki uczenia:

Całkowita liczba rozmów: {stats['total_conversations']}
Wyuczonych odpowiedzi: {stats['learned_responses']}
Średnia ocena: {stats['avg_rating']}/1
Pozytywny feedback: {stats['positive_feedback']}

Im więcej pozytywnego feedbacku, tym mądrzejszy się staję!"""
    
    def oblicz(self, tekst):
        """Prosty kalkulator"""
        try:
            dozwolone = re.match(r'^[\d\s\+\-\*/\(\)\.]+$', tekst)
            if dozwolone:
                wynik = eval(tekst)
                return f"Wynik: {wynik}"
        except:
            pass
        return None
    
    def odpowiedz(self, wiadomosc, session_id):
        """Generuje odpowiedź"""
        
        # 1. Sprawdź obliczenia
        obliczenie = self.oblicz(wiadomosc)
        if obliczenie:
            return obliczenie, 0.9, 'calculation'
        
        # 2. UCZENIE MASZYNOWE - sprawdź wyuczone odpowiedzi
        ml_response, confidence, match_type = ml_bot.get_smart_response(wiadomosc)
        
        if match_type == 'exact' and confidence > 0.5:
            return ml_response, confidence, 'learned_exact'
        elif match_type == 'similar' and confidence > 0.4:
            return ml_response, confidence, 'learned_similar'
        
        # 3. Sprawdź wzorce
        for pattern, odpowiedzi in self.patterns.items():
            if re.match(pattern, wiadomosc):
                response = random.choice(odpowiedzi)
                if callable(response):
                    response = response()
                return response, 0.8, 'pattern'
        
        # 4. Domyślne odpowiedzi
        domyslne = [
            "To interesujące. Opowiedz mi więcej.",
            "Rozumiem. Oceń moją odpowiedź, abym mógł się uczyć!",
            "Hmm, uczę się jeszcze tego tematu. Pomóż mi, oceniając tę odpowiedź.",
            "Ciekawe! Jeśli moja odpowiedź była pomocna, daj mi znać klikając kciuk w górę.",
        ]
        
        return random.choice(domyslne), 0.3, 'default'

bot = ChatBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    dane = request.json
    wiadomosc = dane.get('message', '')
    session_id = dane.get('session_id', str(uuid.uuid4()))
    
    if not wiadomosc:
        return jsonify({'error': 'Brak wiadomości'}), 400
    
    odpowiedz, confidence, source = bot.odpowiedz(wiadomosc, session_id)
    
    # Zapisz rozmowę
    conversation_id = db.save_conversation(wiadomosc, odpowiedz, session_id)
    
    return jsonify({
        'response': odpowiedz,
        'confidence': confidence,
        'source': source,
        'conversation_id': conversation_id,
        'session_id': session_id,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/feedback', methods=['POST'])
def feedback():
    dane = request.json
    conversation_id = dane.get('conversation_id')
    rating = dane.get('rating')  # 1 = positive, -1 = negative
    
    if not conversation_id or rating is None:
        return jsonify({'error': 'Brak danych'}), 400
    
    db.save_feedback(conversation_id, rating)
    
    # Trenuj model po każdym pozytywnym feedbacku
    if rating > 0:
        learned_count = ml_bot.train()
        return jsonify({
            'success': True,
            'message': 'Dziękuję! Właśnie się nauczyłem czegoś nowego.',
            'learned_count': learned_count
        })
    
    return jsonify({'success': True, 'message': 'Dziękuję za feedback!'})

@app.route('/stats', methods=['GET'])
def stats():
    statistics = db.get_statistics()
    return jsonify(statistics)

@app.route('/train', methods=['POST'])
def train():
    """Ręczne trenowanie modelu"""
    learned_count = ml_bot.train()
    return jsonify({
        'success': True,
        'learned_count': learned_count,
        'message': f'Model wytrenowany! Nauczono {learned_count} nowych odpowiedzi.'
    })

if __name__ == '__main__':
    print("AI Chatbot z uczeniem maszynowym uruchomiony!")
    print("URL: http://localhost:5000")
    app.run(debug=True, port=5000)
