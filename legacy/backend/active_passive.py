import spacy
from typing import List, Tuple
import sys

nlp = spacy.load("en_core_web_sm")


def get_active_passive(senteces: List[str]) -> Tuple[int, int]:
    """
    This function takes a list of sentences and returns the number of active and passive voices in the text.
    :param senteces: A list of sentences to analyze.
    :return: A tuple containing the number of active and passive voices in the text.
    """
    active_voice = 0
    passive_voice = 0
    for sentence in senteces:
        doc = nlp(sentence)
        for token in doc:
            if token.dep_ == "nsubjpass":
                passive_voice += 1
            elif token.dep_ == "nsubj":
                active_voice += 1
    return active_voice, passive_voice


if __name__ == "__main__":
    if len(sys.argv) == 2:
        text = sys.argv[1]
    else:
        text = input("Enter text: ")
    sentences = text.split(".")
    print(sentences)
    active, passive = get_active_passive(sentences)
    print(f"Active Voices: {active}")
    print(f"Passive Voices: {passive}")
