import requests
import os
import json
import logging
# import rotateapikeys

# 2. assess the text on scale from 1 to 10 for the following categories: confident, assertive, inspirational, informative, direct.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("OR_API_KEY")
logger.info(f"OR_API_KEY: {'Set' if API_KEY else 'Not set'}")

# almaz = "meta-llama/llama-4-maverick:free"
almaz = "deepseek/deepseek-chat-v3-0324:free"

def fix_grammar(prompt, model=almaz):
    if not API_KEY:
        return None
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content":"""You are a professional public speaking assessor. You will be given a part of a public speech transcript. Your task is to:
    1. correct all the grammar mistakes, excluding punctuation mistakes.
    2. correct all the semantic mistakes (fix misused words and transitions).
    3. correct malapropisms and misused words.

IMPORTANT: You must provide the actual corrections, not just a header. For each mistake you find:
    - Format it as: "<incorrect_phrase> should be <correct_phrase>"
    - List each correction on a new line
    - If no mistakes are found, say "No corrections needed"
    - Only output the corrected mistakes and the corrected text.

After You listed all the mistakes, output the corrected text itself.


Example output:
    "I go to Tashkent metro yesterday" should be "I went to Tashkent metro yesterday"
    "it would be wonderful beautiful" should be "it was wonderfully beautiful"
    "escavators" should be "escalators" """},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    logger.info(f"Raw response text from OpenRouter: {response.text}")
    
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content


def get_mistakes_and_text(text_to_check):
    if not API_KEY:
        return [], text_to_check, []
    
    # EDIT!
    corrected_unparsed = fix_grammar(text_to_check)
    
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

# t = "Hey! So yesterday I go to tashkent metro and it would be wonderful beautiful. The new trainers there are shiny and fast. And they also install new escavators - that's good because I don't need to climb the stairs anymore. it used to bee really tiring"

# print(get_mistakes_and_text("Hello, my major is software engineering but despite this being a math -weighted technical major, I love reading. I have a lot of books right over here and my favorite author is Fedor Dostoevsky. It's a very dark Russian author and here's a really nice book from him. Why I really like this book? it's called Nostrum of the Underground and it tells about Nostrum of the Underground."))
