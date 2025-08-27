import os
import json
from typing import Optional, Tuple
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_logger import get_logger
from openai import OpenAI

# 2. assess the text on scale from 1 to 10 for the following categories: confident, assertive, inspirational, informative, direct.

logger = get_logger(__name__)

API_KEY = os.getenv("OPENAI_API_KEY")
logger.info(f"OPENAI_API_KEY: {'Set' if API_KEY else 'Not set'}")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY) if API_KEY else None

# Use GPT-4o-mini as the default model
default_model = "gpt-4o-mini"
nano = "gpt-5-nano"

def send_api_request(prompt, text, model=default_model, temperature=0.3, max_tokens=500):
    if not client:
        logger.error("OpenAI client not initialized - API key not set")
        return None
    
    logger.info(f"Sending request to OpenAI API with prompt: {prompt}, text: {text}, model: {model}, temperature: {temperature}, max_tokens: {max_tokens}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"OpenAI response received successfully")
        content = response.choices[0].message.content
        return content
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def get_ielts(text, model=nano, temperature=0.3, max_tokens=500) -> Optional[str]:
    prompt = \
"""You are an IELTS and CEFR scorer.
You will be given a text. Your task is to output the CEFR score for the text.
In addition to that give me the IELTS score for the text. Evaluate the text's English level based on words and grammatical structures.
Make sure that IELTS scores are consistent with the text and represent the true score. Format the output like this: "7.5" or "8.0". Do not output anything else and just stop at this.
Do not output the scores below 4.0 and just output "4.0" if the score is below 4.0."""
    return send_api_request(prompt, text, model, temperature, max_tokens)

def fix_punctuation_and_paragraphs(text, model=nano, temperature=0.3, max_tokens=500) -> Optional[str]:
    # return send_api_request(text, model, temperature, max_tokens)
    prompt = \
"""You are a professional text editor. 
Your job is to fix all the punctuation mistakes and separate the text into paragraphs so that it can be published. 
You will be given a public speech and you should output the corrected text. Do not output anything else or change the content of the text."""
    return send_api_request(prompt, text, model, temperature, max_tokens)

def fix_grammar(text, model=default_model, temperature=0.3, max_tokens=500) -> Optional[str]:
    prompt = \
"""You are a professional public speaking assessor. You will be given a part of a public speech transcript. Your task is to:
    1. Correct all the grammar mistakes, excluding punctuation mistakes.
    2. Correct all the semantic mistakes (fix misused words and transitions).
    3. Correct malapropisms and misused words.

IMPORTANT: You must provide the actual corrections, not just a header. For each mistake you find:
    - Format it as: "<incorrect_phrase> should be <correct_phrase>"
    - List each correction on a new line
    - If no mistakes are found, say "No corrections needed"
    - Only output the corrected mistakes and the corrected text.

After you listed all the mistakes, output the corrected text itself.


Example output:
    "I go to Tashkent metro yesterday" should be "I went to Tashkent metro yesterday"
    "it would be wonderful beautiful" should be "it was wonderfully beautiful"
    "escavators" should be "escalators" """

    return send_api_request(prompt, text, model, temperature, max_tokens)

def get_ielts_and_cefr(text_to_check) -> Tuple[str, str] | None:
    ielts = get_ielts(text_to_check)
    if ielts in ["4.0", "4.5", "5.0"]:
        return ielts, "B1"
    elif ielts in ["5.5", "6.0", "6.5"]:
        return ielts, "B2"
    elif ielts in ["7.0", "7.5", "8.0"]:
        return ielts, "C1"
    elif ielts in ["8.5", "9.0"]:
        return ielts, "C2"
    else: 
        return None


def get_mistakes_and_text(text_to_check):
    if not client:
        return [], text_to_check, []

    # EDIT!
    corrected_unparsed = fix_grammar(text_to_check)

    if corrected_unparsed is None:
        return [], text_to_check, []

    corrected_unparsed = corrected_unparsed.strip()

    # corrected_unparsed = "\"despite this being a math -weighted technical major\" should be \"despite this being a math-heavy technical major\"\n\"it's called Nostrum of the Underground and it tells about Nostrum of the Underground\" should be \"it's called Notes from the Underground and it's about the Underground Man\"\n\nCorrected text:\nHello, my major is software engineering but despite this being a math-heavy technical major, I love reading. I have a lot of books right over here and my favorite author is Fyodor Dostoevsky. It's a very dark Russian author and here's a really nice book from him. Why I really like this book? It's called Notes from the Underground and it's about the Underground Man."

    mistakes_lines = []
    corrected_text = text_to_check

    lines = corrected_unparsed.splitlines()
    correction_spans = []

    # Find where the corrected text starts
    corrected_text_start_idx = -1
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if line_lower.startswith("corrected text:") or line_lower == "corrected text":
            corrected_text_start_idx = i
            break

    # Process only the correction lines (before "Corrected text:")
    lines_to_process = lines[:corrected_text_start_idx] if corrected_text_start_idx != -1 else lines

    for line in lines_to_process:
        line = line.strip()
        if not line:
            continue
  
        # Only add lines that contain actual corrections
        if '"' in line and "should be" in line:
            mistakes_lines.append(line)
  
            first_quote = line.find('"')
            second_quote = line.find('"', first_quote + 1)
            incorrect_phrase = line[first_quote + 1:second_quote]

            should_be_idx = line.find("should be", second_quote)
            third_quote = line.find('"', should_be_idx)
            fourth_quote = line.find('"', third_quote + 1)
            correct_phrase = line[third_quote + 1:fourth_quote]

            # Find the first occurrence of incorrect_phrase in corrected_text
            idx = corrected_text.find(incorrect_phrase)
            if idx != -1:
                # Record the span as (start_index, end_index) in the original string
                # The end_index is exclusive
                correction_spans.append((idx, idx + len(correct_phrase)))
                # Replace only the first occurrence in corrected_text
                corrected_text = corrected_text[:idx] + correct_phrase + corrected_text[idx + len(incorrect_phrase):]

    # Extract the actual corrected text if it exists
    if corrected_text_start_idx != -1 and corrected_text_start_idx + 1 < len(lines):
        # Get all lines after "Corrected text:" and join them
        actual_corrected_text_lines = lines[corrected_text_start_idx + 1:]
        actual_corrected_text = '\n'.join(actual_corrected_text_lines).strip()
        if actual_corrected_text:
            corrected_text = actual_corrected_text

    return mistakes_lines, corrected_text, correction_spans

if __name__ == "__main__":
    t = "Hey! So yesterday I go to tashkent metro and it would be wonderful beautiful. The new trainers there are shiny and fast. And they also install new escavators - that's good because I don't need to climb the stairs anymore. it used to bee really tiring"
    # print(get_mistakes_and_text("Hello, my major is software engineering but despite this being a math -weighted technical major, I love reading. I have a lot of books right over here and my favorite author is Fedor Dostoevsky. It's a very dark Russian author and here's a really nice book from him. Why I really like this book? it's called Nostrum of the Underground and it tells about Nostrum of the Underground."))
    print(fix_grammar(t))