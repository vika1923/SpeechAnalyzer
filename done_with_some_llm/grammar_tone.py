import requests
import os
# import rotateapikeys

# 2. assess the text on scale from 1 to 10 for the following categories: confident, assertive, inspirational, informative, direct.

API_KEY = os.getenv("OR_API_KEY")
print(API_KEY)

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
            {"role": "system", "content":"""
                You are a professional public speaking assesor. You will be given a part of a public speech transcript. You have to:
                1. correct all the grammar mistakes, excluding punctuation mistakes (output the corrected text without any grammar mistakes).
                2. correct all the semantic mistakes (output the corrected text with correctly used words and transitions).
                3. correct malapropisms and misused words. If a phrase does not fit the text and makes no sense, in the output text, just put "???" instead of that phrase to indicate

                First, find, correct, and explain the mistakes.
                Then, output **the CORRECTED TEXT ONLY**.
             """
             },
            {"role": "user", "content": prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "corrected text",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "mistakes and explanations": {
                            "type": "string",
                            "description": "Correct grammar and semantic mistakes and explain your reasoning"
                        },
                        "corrected text": {
                            "type": "string",
                            "description": "The corrected text itself"
                        }
                    },
                    "required": ["mistakes and explanations", "corrected text"],
                    "additionalProperties": False
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    print("corrected with llama in grammar_tone")

    try:
        return data["choices"][0]["message"]["content"]
    except:
        print("Хайюд when asking ai to fix grammar")
        print(data)
        return None

# def analyze_tone(prompt, model=almaz):
#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": model,
#         "messages": [
#             {"role": "system", "content":"""
#             **Task**:  
#                 Act as an expert in linguistics and rhetoric. Your goal is to analyze the speech transcript and determine its dominant characteristics:  

#                 1. **Confident** (assertive, bold, definitive)  
#                 2. **Inspirational** (emotional, visionary, motivating)  
#                 3. **Direct** (clear, concise, action-oriented)  
#                 4. **Informative** (fact-based, logical, explanatory)  

#                 **Steps**:  
#                 1. **Language Analysis**:  
#                 - Identify keywords/phrases that signal tone (e.g., "we must" → confident; "dream bigger" → inspirational).  
#                 - Check for rhetorical devices (repetition, metaphors, imperatives).  

#                 2. **Tone & Structure**:  
#                 - Assess sentence length/complexity (short = direct; flowing = inspirational).  
#                 - Evaluate use of data (stats = informative) vs. emotion (hope/unity = inspirational).  

#                 3. **Classification**:  
#                 - Provide a confidence score (1-10) for each label.
#               """
#              },
#             {"role": "user", "content": prompt}
#         ]
#         }
#     response = requests.post(url, headers=headers, json=payload)
#     data = response.json()

#     try:
#         return data["choices"][0]["message"]
#     except:
#         print("Хайюд when asking ai to fix grammar")
#         print(data)
#         return None


# fixed = fix_grammar("""
                    
#                     Close you eyes… and dream big. The future, it are bright—like a… uh, shiny star! We walks together, hand-in-hand, to the glory! No mountain are too tall, no river are too wide. Let’s us rise! Let’s us shine! Let’s us… uh, be the change
                    
#                     """)

# print("FIXED:",fixed)
# print("="*50)
# print("TONE:",analyze_tone(fixed))