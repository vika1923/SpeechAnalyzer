import requests
from pprint import pprint

def get_tone(text):
    response = requests.post(
        "https://api.sapling.ai/api/v1/tone",
        json={
            "key": "015DQLX8TMB98ZT4L39YZT1Y735MOGOG",
            "text": text
        }
    )

    oval = response.json()["overall"]


    return oval
