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
if key:
    logger.info(f"Sapling API key loaded: {key[:4]}...{'*' * (len(key)-8) if key and len(key) > 8 else ''}{key[-4:] if key and len(key) > 8 else ''}")
else:
    logger.error("Sapling API key is missing! Set the SAPLING_KEY environment variable.")

def get_tone(text: str) -> list:
    logger.info("get_tone called")
    if not key:
        logger.error("No Sapling API key provided. Aborting get_tone.")
        return []
    if not text or not isinstance(text, str):
        logger.warning("No text provided or text is not a string. Aborting get_tone.")
        return []
    payload = {
        "key": key,
        "text": text
    }
    logger.debug(f"Payload to Sapling: {payload}")
    try:
        response = requests.post(
            "https://api.sapling.ai/api/v1/tone",
            json=payload
        )
        if response.status_code != 200:
            logger.error(f"Sapling API returned status {response.status_code}: {response.text}")
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
# print(get_tone("Wow—what a time to be alive! Every day brings new possibilities, unexpected opportunities, and the thrill of building something meaningful. The energy in the air is electric. We're on the edge of something big, and it feels like anything is possible. Challenges? Sure—but they're just stepping stones. The future is bright, and we're racing toward it full speed, eyes wide open, hearts on fire. Let's go!"))
