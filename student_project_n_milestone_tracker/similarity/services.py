"""
Similarity detection service using NLP techniques
"""
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class SimilarityDetector:
    """Detects similar project titles using multiple NLP techniques"""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )

    def preprocess_text(self, text):
        """Preprocess text for similarity analysis"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Tokenize and remove stop words
        tokens = text.split()
        tokens = [token for token in tokens if token not in self.stop_words]

        # Stem words
        tokens = [self.stemmer.stem(token) for token in tokens]

        return ' '.join(tokens)

    def calculate_tfidf_similarity(self, text1, text2):
        """Calculate TF-IDF based similarity"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0

            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)
        except:
            return 0.0

    def calculate_phrase_overlap(self, text1, text2):
        """Calculate phrase overlap similarity"""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def calculate_keyword_match(self, text1, text2):
        """Calculate keyword matching similarity"""
        if not text1 or not text2:
            return 0.0

        # Extract keywords (nouns, proper nouns - simplified)
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)

        if not keywords1 or not keywords2:
            return 0.0

        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)

        return len(intersection) / len(union) if union else 0.0

    def _extract_keywords(self, text):
        """Extract potential keywords from text"""
        if not text:
            return set()

        # Simple keyword extraction - words longer than 3 chars
        words = re.findall(r'\b\w{4,}\b', text.lower())
        return set(words)

    def calculate_overall_similarity(self, title1, title2):
        """Calculate overall similarity score using weighted formula"""
        # Preprocess texts
        processed1 = self.preprocess_text(title1)
        processed2 = self.preprocess_text(title2)

        # Calculate individual scores
        tfidf_score = self.calculate_tfidf_similarity(processed1, processed2)
        phrase_score = self.calculate_phrase_overlap(title1, title2)
        keyword_score = self.calculate_keyword_match(title1, title2)

        # Weighted formula: 0.5 * TF-IDF + 0.3 * Phrase Overlap + 0.2 * Keyword Match
        overall_score = 0.5 * tfidf_score + 0.3 * phrase_score + 0.2 * keyword_score

        # Explain the match
        reasons = []
        if tfidf_score > 0.3:
            reasons.append("Similar word patterns detected")
        if phrase_score > 0.4:
            reasons.append("Common phrases found")
        if keyword_score > 0.5:
            reasons.append("Matching technical keywords")

        return {
            'score': round(overall_score, 3),
            'tfidf': round(tfidf_score, 3),
            'phrase_overlap': round(phrase_score, 3),
            'keyword_match': round(keyword_score, 3),
            'reasons': reasons
        }

    def check_title_similarity(self, new_title, existing_titles):
        """Check similarity of new title against existing titles"""
        if not new_title or not existing_titles:
            return []

        results = []
        for existing_title in existing_titles:
            if existing_title and existing_title.lower().strip() == new_title.lower().strip():
                # Exact duplicate
                results.append({
                    'title': existing_title,
                    'score': 1.0,
                    'tfidf': 1.0,
                    'phrase_overlap': 1.0,
                    'keyword_match': 1.0,
                    'reasons': ['Exact duplicate title'],
                    'is_exact_duplicate': True
                })
            else:
                similarity = self.calculate_overall_similarity(new_title, existing_title)
                similarity['title'] = existing_title
                similarity['is_exact_duplicate'] = False
                results.append(similarity)

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def get_similarity_flag(self, score):
        """Determine warning level based on similarity score"""
        if score >= 0.8:
            return 'STRONG'
        elif score >= 0.6:
            return 'MEDIUM'
        else:
            return 'NONE'