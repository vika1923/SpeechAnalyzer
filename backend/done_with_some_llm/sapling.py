import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

key = os.getenv("SAPLING_KEY")
key="015DQLX8TMB98ZT4L39YZT1Y735MOGOG"

def get_tone(text: str) -> list:
    logger.info("get_tone called")
    try:
        response = requests.post(
            "https://api.sapling.ai/api/v1/tone",
            json={
                "key": key,
                "text": text
            }
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        logger.debug(f"Response from Sapling: {data}")

        oval = data.get("overall", []) # Safely get 'overall', default to empty list
        if not oval:
            logger.warning("Sapling API returned an empty 'overall' analysis.")
        
        logger.info("Successfully retrieved tone from Sapling.")
        return oval

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Sapling API: {e}", exc_info=True)
        return [] # Return empty list on network/HTTP error
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_tone: {e}", exc_info=True)
        return [] # Return empty list on other errors

# print(get_tone("We are bad at this. What if it dies??? It is your responsibility to look after it"))
# print(get_tone("Wow—what a time to be alive! Every day brings new possibilities, unexpected opportunities, and the thrill of building something meaningful. The energy in the air is electric. We’re on the edge of something big, and it feels like anything is possible. Challenges? Sure—but they’re just stepping stones. The future is bright, and we’re racing toward it full speed, eyes wide open, hearts on fire. Let’s go!"))
