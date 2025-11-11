import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name='chatbot.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicjalizacja tabel w bazie danych"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabela rozmów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rating INTEGER DEFAULT 0,
                session_id TEXT
            )
        ''')
        
        # Tabela wyuczonych odpowiedzi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL UNIQUE,
                answer TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela feedbacku
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                rating INTEGER,
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        # Tabela słów kluczowych
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                category TEXT,
                weight REAL DEFAULT 1.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_message, bot_response, session_id=None):
        """Zapisz rozmowę"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, session_id)
            VALUES (?, ?, ?)
        ''', (user_message, bot_response, session_id))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def save_feedback(self, conversation_id, rating, comment=None):
        """Zapisz feedback użytkownika"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (conversation_id, rating, comment)
            VALUES (?, ?, ?)
        ''', (conversation_id, rating, comment))
        
        # Aktualizuj rating w conversations
        cursor.execute('''
            UPDATE conversations
            SET rating = ?
            WHERE id = ?
        ''', (rating, conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_all_conversations(self):
        """Pobierz wszystkie rozmowy"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, rating
            FROM conversations
            ORDER BY timestamp DESC
        ''')
        
        conversations = cursor.fetchall()
        conn.close()
        
        return conversations
    
    def get_positive_conversations(self, min_rating=1):
        """Pobierz dobrze ocenione rozmowy do uczenia"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, rating
            FROM conversations
            WHERE rating >= ?
            ORDER BY rating DESC, timestamp DESC
        ''', (min_rating,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return conversations
    
    def learn_from_feedback(self):
        """Ucz się z pozytywnego feedbacku"""
        positive_convs = self.get_positive_conversations()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        learned_count = 0
        
        for user_msg, bot_response, rating in positive_convs:
            # Sprawdź czy już istnieje
            cursor.execute('''
                SELECT id, confidence, usage_count
                FROM learned_responses
                WHERE question = ?
            ''', (user_msg,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Zwiększ confidence i usage_count
                new_confidence = min(existing[1] + 0.1, 1.0)
                cursor.execute('''
                    UPDATE learned_responses
                    SET confidence = ?,
                        usage_count = usage_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_confidence, existing[0]))
            else:
                # Dodaj nową wyuczoną odpowiedź
                confidence = 0.6 if rating >= 1 else 0.4
                cursor.execute('''
                    INSERT INTO learned_responses (question, answer, confidence)
                    VALUES (?, ?, ?)
                ''', (user_msg, bot_response, confidence))
                learned_count += 1
        
        conn.commit()
        conn.close()
        
        return learned_count
    
    def find_learned_response(self, question):
        """Znajdź wyuczoną odpowiedź"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT answer, confidence
            FROM learned_responses
            WHERE question = ?
            ORDER BY confidence DESC
            LIMIT 1
        ''', (question,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def get_statistics(self):
        """Pobierz statystyki"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Liczba rozmów
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Liczba wyuczonych odpowiedzi
        cursor.execute('SELECT COUNT(*) FROM learned_responses')
        learned_responses = cursor.fetchone()[0]
        
        # Średnia ocena
        cursor.execute('SELECT AVG(rating) FROM conversations WHERE rating != 0')
        avg_rating = cursor.fetchone()[0] or 0
        
        # Pozytywny feedback
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE rating > 0')
        positive_feedback = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'learned_responses': learned_responses,
            'avg_rating': round(avg_rating, 2),
            'positive_feedback': positive_feedback
        }
