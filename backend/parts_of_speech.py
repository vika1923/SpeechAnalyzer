from nltk.tokenize import word_tokenize
from nltk import pos_tag
from typing import Dict, List
from custom_types import PartOfSpeech
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

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
}

def parts_of_speech(text: str) -> Dict[PartOfSpeech, int]:
    logger.info("parts_of_speech called")
    try:
        words = word_tokenize(text, "english")
        tagged = pos_tag(words, tagset='universal')
        tag_words: Dict[str, List[str]]= {}

        for word, tag in tagged:
            if tag in ['.', 'X']:
                continue 
            else:
                normal_tag = POS_MARKINGS[tag]
            tag_words.setdefault(normal_tag, []).append(word)

        result = {pos: len(words) for pos, words in tag_words.items()} # type: ignore
        logger.info("Successfully analyzed parts of speech.")
        return result
    except Exception as e:
        logger.error(f"Error in parts_of_speech: {e}", exc_info=True)
        raise


