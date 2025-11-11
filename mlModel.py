import re
import math
from collections import Counter
from database import Database

class MLChatBot:
    def __init__(self):
        self.db = Database()
        self.stopwords = set(['i', 'a', 'o', 'w', 'z', 'na', 'do', 'się', 'jest', 'to', 'że'])
        self.vocabulary = set()
        self.documents = []
        self.load_training_data()
    
    def preprocess(self, text):
        """Przetwarzanie tekstu"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        words = [w for w in words if w not in self.stopwords and len(w) > 2]
        return words
    
    def load_training_data(self):
        """Załaduj dane treningowe z bazy"""
        conversations = self.db.get_positive_conversations()
        
        for user_msg, bot_response, rating in conversations:
            words = self.preprocess(user_msg)
            self.vocabulary.update(words)
            self.documents.append({
                'words': words,
                'question': user_msg,
                'answer': bot_response,
                'rating': rating
            })
    
    def calculate_tf(self, word, document_words):
        """Term Frequency"""
        word_count = document_words.count(word)
        return word_count / len(document_words) if document_words else 0
    
    def calculate_idf(self, word):
        """Inverse Document Frequency"""
        docs_with_word = sum(1 for doc in self.documents if word in doc['words'])
        if docs_with_word == 0:
            return 0
        return math.log(len(self.documents) / docs_with_word)
    
    def calculate_tfidf(self, words):
        """TF-IDF dla dokumentu"""
        tfidf = {}
        for word in set(words):
            tf = self.calculate_tf(word, words)
            idf = self.calculate_idf(word)
            tfidf[word] = tf * idf
        return tfidf
    
    def cosine_similarity(self, vec1, vec2):
        """Oblicz podobieństwo cosinusowe"""
        # Wspólne słowa
        common_words = set(vec1.keys()) & set(vec2.keys())
        
        if not common_words:
            return 0.0
        
        # Iloczyn skalarny
        dot_product = sum(vec1[word] * vec2[word] for word in common_words)
        
        # Magnitude
        magnitude1 = math.sqrt(sum(val**2 for val in vec1.values()))
        magnitude2 = math.sqrt(sum(val**2 for val in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def find_similar_question(self, user_message, threshold=0.3):
        """Znajdź podobne pytanie w bazie"""
        if not self.documents:
            return None, 0.0
        
        user_words = self.preprocess(user_message)
        user_tfidf = self.calculate_tfidf(user_words)
        
        best_match = None
        best_similarity = 0.0
        
        for doc in self.documents:
            doc_tfidf = self.calculate_tfidf(doc['words'])
            similarity = self.cosine_similarity(user_tfidf, doc_tfidf)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = doc
        
        if best_similarity >= threshold:
            return best_match, best_similarity
        
        return None, 0.0
    
    def train(self):
        """Trenuj model na podstawie feedbacku"""
        learned_count = self.db.learn_from_feedback()
        self.load_training_data()  # Przeładuj dane
        return learned_count
    
    def get_smart_response(self, user_message):
        """Inteligentna odpowiedź z ML"""
        # Najpierw sprawdź dokładne dopasowanie
        learned = self.db.find_learned_response(user_message)
        if learned:
            return learned[0], learned[1], 'exact'
        
        # Jeśli nie ma dokładnego, znajdź podobne
        similar, similarity = self.find_similar_question(user_message)
        
        if similar:
            return similar['answer'], similarity, 'similar'
        
        return None, 0.0, 'none'
