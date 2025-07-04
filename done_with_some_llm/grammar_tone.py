import requests
import os
import json
# import rotateapikeys

# 2. assess the text on scale from 1 to 10 for the following categories: confident, assertive, inspirational, informative, direct.

API_KEY = os.getenv("OR_API_KEY")


almaz = "meta-llama/llama-4-maverick:free"

def fix_grammar(prompt, model=almaz):
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
    - Only output the corrected mistakes and the corrected text. Do not add your comments, reasoning chains or assumptions. If you about whether something is a mistake, assume it is correct and skip it.

After You listed all the mistakes, output the corrected text itself.


Example output:
    "I go to tashkent metro" should be "I went to Tashkent metro"
    "it would be wonderful beautiful" should be "it was wonderfully beautiful"
    "escavators" should be "escalators" """},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=payload)
    
    data = response.json()
    print("RESPONSE", data)

    print("corrected with llama in grammar_tone")

    try:
        content = data["choices"][0]["message"]["content"]
        print("Raw content:", content)
        return content
    except Exception as e:
        print(f"Error when asking ai to fix grammar: {e}")
        print(data)
        return None

t = "Hey! So yesterday I go to tashkent metro and it would be wonderful beautiful. The new trainers there are shiny and fast. And they also install new escavators - that's good because I don't need to climb the stairs anymore. it used to bee really tiring"

def get_mistakes_and_text(text_to_check):
    corrected_unparsed = fix_grammar(text_to_check)
    if corrected_unparsed is None:
        print("Grammar correction failed - API error or no response")
        return None, None
    
    corrected_unparsed = corrected_unparsed.strip()
    
    mistakes_lines = []
    corrected_text = text_to_check

    lines = corrected_unparsed.splitlines()
    correction_spans = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        mistakes_lines.append(line)

        if '"' in line and "should be" in line:
            try:
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
            except Exception as e:
                print(f"Error parsing line: {line} ({e})")
                continue

    return mistakes_lines, corrected_text, correction_spans

print(get_mistakes_and_text(t))