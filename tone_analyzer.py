from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List, Tuple

def analyze_tone(text: str) -> Dict[str, float]:
    """
    Analyze the tone of the given text using VADER sentiment analysis.
    Returns a dictionary containing the compound score and individual scores for negative, neutral, and positive tones.
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores

def get_tone_description(compound_score: float) -> str:
    """
    Convert the compound score to a human-readable tone description.
    """
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def analyze_text_segments(text: str, segment_length: int = 100) -> List[Tuple[str, Dict[str, float]]]:
    """
    Analyze the tone of text in segments to track tone changes throughout the text.
    """
    words = text.split()
    segments = []
    
    for i in range(0, len(words), segment_length):
        segment = ' '.join(words[i:i + segment_length])
        tone_scores = analyze_tone(segment)
        segments.append((segment, tone_scores))
    
    return segments 