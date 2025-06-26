import requests
from pprint import pprint
import os

key = os.getenv("SAPLING_KEY")

def get_tone(text):
    response = requests.post(
        "https://api.sapling.ai/api/v1/tone",
        json={
            "key": key,
            "text": text
        }
    )

    oval = response.json()["overall"]

    return oval
