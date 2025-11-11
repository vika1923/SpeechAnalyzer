def separate_to_sentences(text):
    """
    Separate text into sentences.
    
    Args:
        text (str): The text to be separated into sentences.
        
    Returns:
        list: A list of sentences.
    """
    sentence_enders = [".", "!", "?"]
    sentences = []
    current_sentence = ""
    for char in text:
        if char in sentence_enders:
            sentences.append(current_sentence)
            current_sentence = ""
        else:
            current_sentence += char
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

def separate_to_paragraphs(text):
    """
    Separate text into paragraphs.
    
    Args:
        text (str): The text to be separated into paragraphs.
        
    Returns:
        list: A list of paragraphs.
    """
    paragraphs = []
    current_paragraph = ""
    for char in text:
        if char == "\n":
            paragraphs.append(current_paragraph)
            current_paragraph = ""
        else:
            current_paragraph += char
    if current_paragraph:
        paragraphs.append(current_paragraph)
    return paragraphs

def count_sentences(text):
    """
    Count the number of sentences in a given text.
    
    Args:
        text (str): The text to count the number of sentences.
        
    Returns:
        int: The number of sentences in the text.
    """
    sentences = separate_to_sentences(text)
    return len(sentences)

def count_paragraphs(text):
    """
    Count the number of paragraphs in a given text.
    
    Args:
        text (str): The text to count the number of paragraphs.
        
    Returns:
        int: The number of paragraphs in the text.
    """
    paragraphs = separate_to_paragraphs(text)
    return min(len(paragraphs), count_sentences(text))

def count_letters(text):
    """
    Count the number of letters (only upper and lower case letters) in a given text.
    
    Args:
        text (str): The text to count the number of letters.
        
    Returns:
        int: The number of letters in the text.
    """
    count = 0
    for char in text:
        if char.isalpha():
            count += 1
    return count



