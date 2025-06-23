import requests
from pprint import pprint

def get_tone(text):
    response = requests.post(
        "https://api.sapling.ai/api/v1/tone",
        json={
            "key": "X79YRF8YWEAVO59SK8LATWT5CY15XDR0",
            "text": text
        }
    )

    # pprint(response.json())
    # print("-"*100)
    # pprint(parse_tone_detailed(response=response.json()["results"]))
    # print(response.json()["overall"])

    oval = response.json()["overall"]
    plus = parse_tone_detailed(response=response.json()["results"], oval=oval)

    return {"overall tones:":oval, "other detected tones:":plus}

def parse_tone_detailed(response, oval):
    r_tones = {
    'admiring': 0,
    'amused': 0,
    'angry': 0,
    'annoyed': 0,
    'approving': 0,
    'aware': 0,
    'confident': 0,
    'confused': 0,
    'curious': 0,
    'eager': 0,
    'disappointed': 0,
    'disapproving': 0,
    'embarrassed': 0,
    'excited': 0,
    'fearful': 0,
    'grateful': 0,
    'joyful': 0,
    'loving': 0,
    'mournful': 0,
    'neutral': 0,
    'optimistic': 0,
    'relieved': 0,
    'remorseful': 0,
    'repulsed': 0,
    'sad': 0,
    'worried': 0,
    'surprised': 0,
    'sympathetic': 0
    }
    for sentence_result_3 in response:
        i = 3
        for number_tone_emoji in sentence_result_3:
            r_tones[number_tone_emoji[1]] += i
            i -= 1

    ret = dict()
    ovals = []
    for i in oval:
        ovals.append(i[1])
    for k, v in r_tones.items():
        if v > 0 and k not in ovals:
            ret[k]=v

    return ret      # ret = tones and values of those that are not 0. number of those tones occurances (3 for each sentence) 


def fix_grammar(text):
    try:
        response = requests.post(
            "https://api.sapling.ai/api/v1/edits",
            json={
                "key": "X79YRF8YWEAVO59SK8LATWT5CY15XDR0",
                "text": text,
                "session_id": "test session",
                "auto_apply": True,
                "ignore_edit_types": ["capitalization", "hyphens", "punctuation"]
            }
        )
        resp_json = response.json()
        if 200 <= response.status_code < 300:
            edits = resp_json['edits']
            # pprint(edits)
            pprint(resp_json)

            edits_to_return = []

            for obj in edits:
                temp = list()
                temp.append(obj["start"])
                temp.append(obj["end"])
                temp.append(obj["replacement"])
                edits_to_return.append(temp)
            return edits_to_return          # returns start and end index in the sentence, NOT THE WHOLE SPEECH TRANSCRIPT
            
        else:
            print("Error: ", resp_json)
    except Exception as e:
        print("Error: ", e)


t = """
I just don't understand you. How can you do that? It is just so astonishing how dumb some people are. You keep working, trying hard, doing your best - and what then? You get nothing. You are still a loser.
"""
# f = get_tone(t)
print(get_tone(t))
# print("+"*50)
# print(f)