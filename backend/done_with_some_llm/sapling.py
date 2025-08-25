import os
import requests
from pprint import pprint

key = os.getenv("SAPLING_KEY")

def get_tone(text):
    response = requests.post(
    "https://api.sapling.ai/api/v1/tone",
    json={
        "key": key,
        "text": text
    }
    )

    if 200 <= response.status_code < 300:
        # print("success")
        return response.json()["overall"]
    else:
        # print("fail")
        return([[42, '42', '😐']])

if __name__ == "__main__":
    print(get_tone("We are bad at this. What if it dies??? It is your responsibility to look after it"))
    print(get_tone("Wow—what a time to be alive! Every day brings new possibilities, unexpected opportunities, and the thrill of building something meaningful. The energy in the air is electric. We’re on the edge of something big, and it feels like anything is possible. Challenges? Sure—but they’re just stepping stones. The future is bright, and we’re racing toward it full speed, eyes wide open, hearts on fire. Let’s go!"))
