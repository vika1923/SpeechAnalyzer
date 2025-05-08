from nltk.tokenize import word_tokenize
from nltk import pos_tag
from typing import Dict, List

POS_MARKINGS = {
    'VERB' : 'Verbs',
    'NOUN' : 'Nouns',
    'PRON' : 'Pronouns',
    'ADJ' : 'Adjectives',
    'ADV' : 'Adverbs',
    'ADP' : 'Adpositions',
    'CONJ' : 'Conjunctions',
    'DET' : 'Determiners',
    'NUM' : 'Cardinal',
    'PRT' : 'Particles',
    'X' : 'Other',
}

def parts_of_speech(text: str) -> Dict[str, List[str]]:
    words = word_tokenize(text, "english")
    tagged = pos_tag(words, tagset='universal')
    result = {}

    for word, tag in tagged:
        if tag == '.':
            continue 
        else:
            normal_tag = POS_MARKINGS[tag]
        result.setdefault(normal_tag, []).append(word)
    return result


