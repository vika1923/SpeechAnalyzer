from deepmultilingualpunctuation import PunctuationModel

def get_punctuated_text(unpunctuated_text: str) -> str:
    model = PunctuationModel()
    return(model.restore_punctuation(unpunctuated_text))
