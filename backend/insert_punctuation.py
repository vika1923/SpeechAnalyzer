from deepmultilingualpunctuation import PunctuationModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

model = PunctuationModel()

def get_punctuated_text(unpunctuated_text: str) -> str:
    logger.info("get_punctuated_text called")
    try:
        result = model.restore_punctuation(unpunctuated_text)
        logger.info("Successfully punctuated text.")
        return result
    except Exception as e:
        logger.error(f"Error in get_punctuated_text: {e}", exc_info=True)
        raise
