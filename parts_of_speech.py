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
    words = word_tokenize(text)
    tagged = pos_tag(words)
    result = {}

    for word, tag in tagged:
        if tag == '.':
            continue 
        else:
            if tag.startswith('NN'):
                normal_tag = 'Nouns'
            elif tag.startswith('VB'):
                normal_tag = 'Verbs'
            elif tag.startswith('JJ'):
                normal_tag = 'Adjectives'
            elif tag.startswith('RB'):
                normal_tag = 'Adverbs'
            elif tag.startswith('PRP'):
                normal_tag = 'Pronouns'
            elif tag.startswith('IN'):
                normal_tag = 'Adpositions'
            elif tag.startswith('CC'):
                normal_tag = 'Conjunctions'
            elif tag.startswith('DT'):
                normal_tag = 'Determiners'
            elif tag.startswith('CD'):
                normal_tag = 'Cardinal'
            else:
                normal_tag = 'Other'
        result.setdefault(normal_tag, []).append(word)
    return result


