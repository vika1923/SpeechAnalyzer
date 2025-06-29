import requests
import os
import json
# import rotateapikeys

# 2. assess the text on scale from 1 to 10 for the following categories: confident, assertive, inspirational, informative, direct.

API_KEY = os.getenv("OR_API_KEY")
print(API_KEY)

API_KEY = "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" 

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
    - Only output the corrected mistakes and the corrected text. Do not add your comments.

After You listed all the mistakes, output the corrected text itself.


Example output:
{Mistakes:
    "I go to tashkent metro" should be "I went to Tashkent metro"
    "it would be wonderful beautiful" should be "it was wonderfully beautiful"
    "escavators" should be "escalators"
Corrected text: 
    Hello everyone! I will tell you a story that hapened to me yesterday. I went to Tashkent metro yesterday. It was wonderfully beautiful. They have installed new trains and new escalators.}"""
             },
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
    corrected_unparsed = fix_grammar(text_to_check).strip()
    print(corrected_unparsed)
    
    # Find the start of mistakes section
    mistakes_start = corrected_unparsed.find("Mistakes:")
    if mistakes_start == -1:
        return None, None
    
    # Find the start of corrected text section
    corrected_text_start = corrected_unparsed.find("Corrected text:")
    if corrected_text_start == -1:
        return None, None
    
    # Extract mistakes (from after "Mistakes:" up to "Corrected text:")
    mistakes_section_start = mistakes_start + len("Mistakes:")
    mistakes = corrected_unparsed[mistakes_section_start:corrected_text_start].strip()
    
    # Extract corrected text (everything after "Corrected text:")
    corrected_text_section_start = corrected_text_start + len("Corrected text:")
    corrected_text = corrected_unparsed[corrected_text_section_start:].strip()

    corrected_text = corrected_text.replace("\\'", "'")

    mistakes_lines = mistakes.split("\n")
    
    return mistakes_lines, corrected_text

print(get_mistakes_and_text(t))