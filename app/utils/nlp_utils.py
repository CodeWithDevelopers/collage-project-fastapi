import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.text import TextCollection

def clean_text(text: str) -> str:
    return re.sub(r'[^\w\s.,!?]', '', text.replace('\n', '. ')).strip()

def split_into_sentences(text: str):
    return re.findall(r'[^.!?]+[.!?]+', text)

def get_word_count(text: str) -> int:
    return len(text.strip().split())

def get_reading_time(word_count: int) -> int:
    return max(1, word_count // 200)

def get_main_topics(text: str):
    words = word_tokenize(text.lower())
    freq = {}
    for word in words:
        if len(word) > 3:
            freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:5]]

def get_sentence_score(sentence, tfidf, index):
    words = word_tokenize(sentence.lower())
    return sum(tfidf.tf_idf(word, tfidf.docs[index]) for word in words) / max(1, len(words))
