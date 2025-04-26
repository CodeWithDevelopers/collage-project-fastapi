from app.core.gemini import get_gemini_model
from app.schemas.summary import SummaryResponse, Analysis
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.text import TextCollection
import re
import math

nltk.download('punkt')
nltk.download('stopwords')

def clean_text(text: str):
    return re.sub(r"[^\w\s.,!?]", "", text.replace("\n", " ")).strip()

def split_sentences(text: str):
    return re.findall(r'[^.!?]+[.!?]+', text)

def word_count(text: str):
    return len(text.strip().split())

def reading_time(words: int):
    return math.ceil(words / 200)

def get_main_topics(text: str):
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    freq = {}
    for word in words:
        if word.isalpha() and word not in stop_words:
            freq[word] = freq.get(word, 0) + 1
    return [word for word, _ in sorted(freq.items(), key=lambda item: item[1], reverse=True)[:5]]

async def generate_extractive_summary(text: str, summary_ratio: float = 0.3) -> SummaryResponse:
    cleaned = clean_text(text)
    sentences = split_sentences(cleaned)

    if not sentences:
        return SummaryResponse(
            topics=[], summary="Text too short or no complete sentences.",
            conclusion="", analysis=Analysis(**{k: 0 for k in Analysis.__fields__})
        )

    corpus = TextCollection(sentences)
    scored = [(s, sum([corpus.tf_idf(w, s) for w in word_tokenize(s.lower()) if w.isalpha()])/len(word_tokenize(s)) if len(word_tokenize(s)) else 0, i)
              for i, s in enumerate(sentences)]
    
    scored.sort(key=lambda x: x[1], reverse=True)
    top_n = max(3, int(len(sentences) * summary_ratio))
    selected = sorted(scored[:top_n], key=lambda x: x[2])
    summary = " ".join([s[0].strip() for s in selected])

    last_sentence = sentences[-1]
    conclusion_keywords = ["conclusion", "finally", "therefore", "thus", "in summary"]
    conclusion = last_sentence if any(word in last_sentence.lower() for word in conclusion_keywords) else ""

    topics = get_main_topics(cleaned)

    return SummaryResponse(
        topics=topics,
        summary=summary,
        conclusion=conclusion,
        analysis=Analysis(
            originalWords=word_count(text),
            summaryWords=word_count(summary),
            originalChars=len(text),
            summaryChars=len(summary),
            readingTime=reading_time(word_count(text)),
            summaryReadingTime=reading_time(word_count(summary)),
        )
    )

async def generate_abstractive_summary(text: str) -> SummaryResponse:
    model = get_gemini_model()
    prompt = f"""Please summarize the following text in 25-30% length, covering main ideas and structure clearly:

{text}

Format:
1. List 3-5 main topics
2. Provide summary
3. Include any conclusion if present
4. No extra commentary."""

    result = model.generate_content(prompt)
    summary = result.text

    # Basic parsing
    parts = summary.split('\n\n')
    topics = get_main_topics(summary)
    summary_body = next((p for p in parts if "main" not in p.lower() and "topic" not in p.lower()), summary)
    conclusion = next((p for p in parts if "conclusion" in p.lower()), "")

    return SummaryResponse(
        topics=topics,
        summary=summary_body.strip(),
        conclusion=conclusion.strip(),
        analysis=Analysis(
            originalWords=word_count(text),
            summaryWords=word_count(summary_body),
            originalChars=len(text),
            summaryChars=len(summary_body),
            readingTime=reading_time(word_count(text)),
            summaryReadingTime=reading_time(word_count(summary_body)),
        )
    )
