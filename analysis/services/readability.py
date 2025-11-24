from typing import List
import nltk

nltk.download("cmudict")
from nltk.corpus import cmudict
import re

cmu_dict = cmudict.dict()


def count_syllables(word: str) -> int:
    """
    Count syllables in a single word using cmudict if available.
    Falls back to a simple heuristic if word is not in cmudict.
    """
    word = word.lower()
    if word in cmu_dict:
        # cmudict can have multiple pronunciations → take first
        pronunciation = cmu_dict[word][0]
        return len([ph for ph in pronunciation if ph[-1].isdigit()])
    else:
        # Fallback: Count vowel groups as syllables
        return len(re.findall(r"[aeiouy]+", word))


def readibility(nsentences: int, words: List[str]):
    # separate the text into words without insert_punctuation
    syllables = 0
    for word in words:
        syllables += count_syllables(word)
    return (
        206.835
        - 1.015 * (max(1, len(words)) / nsentences)
        - 84.6 * (syllables / max(1, len(words)))
    )


def readibility_score(nsentences: int, words: List[str]):
    rsc = readibility(nsentences, words)
    if rsc < 10:
        return "Professional"
    elif rsc < 30:
        return "College Graduate"
    elif rsc < 50:
        return "College"
    elif rsc < 60:
        return "Grade 10 - 12"
    elif rsc < 70:
        return "Grade 8 - 9"
    elif rsc < 80:
        return "Grade 7"
    elif rsc < 90:
        return "Grade 6"
    elif rsc <= 100:
        return "Grade 5"
    else:
        return "42"
