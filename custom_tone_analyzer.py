import re
from typing import Dict, List
import nltk

def split_sentences(text: str) -> List[str]:
    # Use nltk's sentence tokenizer for better accuracy
    from nltk.tokenize import sent_tokenize
    return sent_tokenize(text)

def analyze_tones(text: str) -> Dict[str, float]:
    sentences = [s.strip() for s in split_sentences(text) if s.strip()]
    total = len(sentences)
    if total == 0:
        return {tone: 0.0 for tone in TONE_KEYWORDS}
    tone_counts = {tone: 0 for tone in TONE_KEYWORDS}
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for tone, keywords in TONE_KEYWORDS.items():
            if any(word.lower() in sentence_lower for word in keywords):
                tone_counts[tone] += 1
    return {tone: round(100 * count / total) for tone, count in tone_counts.items()}

TONE_KEYWORDS = {
    'Confident': [
        'certainly', 'definitely', 'undoubtedly', 'confident', 'sure', 'absolutely', 'clearly', 'will', 'guaranteed',
        "no doubt", "without question", "I am sure", "I am confident", "thrilled", "outstanding", "proud"
    ],
    'Formal': [
        'regarding', 'therefore', 'hence', 'thus', 'respectfully', 'sincerely', 'please find', 'enclosed', 'attached',
        'to whom it may concern', 'hereby', 'herewith', 'pursuant', 'in accordance', 'kindly', 'shall', 'would', 'may',
        'accomplished', 'successfully'
    ],
    'Informative': [
        'for your information', 'note that', 'it is important', 'the data shows', 'statistics', 'research', 'study',
        'according to', 'as shown', 'demonstrates', 'reveals', 'indicates', 'explains', 'describes', 'informs', 'details',
        'results', 'news', 'expectations'
    ],
    'Direct': [
        'do this', 'must', 'need to', 'should', 'have to', 'immediately', 'now', 'directly', 'clearly', 'simply',
        'just', 'stop', 'start', 'go', 'come', 'leave', 'take', 'give', 'send', 'tell', 'show', 'make', 'get',
        'face', 'overcome'
    ],
    'Friendly': [
        'hello', 'hi', 'hey', 'thanks', 'thank you', 'appreciate', 'glad', 'happy', 'pleased', 'welcome', 'enjoy',
        'hope', 'wish', 'cheer', 'smile', 'friendly', 'nice', 'great', 'wonderful', 'awesome', 'delight', 'fun',
        'together', 'share', 'everyone'
    ],
    'Inspirational': [
        'believe', 'inspire', 'motivate', 'encourage', 'dream', 'achieve', 'success', 'goal', 'vision', 'future',
        'can', 'will', 'aspire', 'strive', 'overcome', 'rise', 'shine', 'potential', 'possibility', 'opportunity',
        'remarkable', 'managed'
    ],
    'Assertive': [
        'I think', 'I believe', 'I want', 'I need', 'I will', 'I expect', 'I require', 'must', 'should', 'have to',
        'let me', 'allow me', 'permit me', 'I insist', 'I am certain', 'I am sure', 'I am confident', 'couldn\'t be more proud'
    ]
}

def print_tone_results(tone_percentages: Dict[str, float]):
    print("\nDetected Tones:")
    for tone, percent in tone_percentages.items():
        print(f"{tone:14}: {percent}%") 