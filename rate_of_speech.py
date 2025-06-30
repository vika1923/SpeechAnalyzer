from typing import Tuple, Dict, List
from custom_types import TimeStamp
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def get_rate_of_speech(words: Dict[TimeStamp, str], interval: float = 10.) -> List[Tuple[float, float]]:
    logger.info("get_rate_of_speech called")
    try:
        result = []
        wordcount = 0
        current_time = 0

        sorted_words = sorted(words.items(), key=lambda x: x[0][0])

        for (_, end), _ in sorted_words:
            wordcount += 1
            if end > current_time + interval:
                # Calculate words per minute for this interval
                words_per_second = (wordcount / interval) 
                result.append((current_time, words_per_second))
                current_time += interval
                wordcount = 0
        if wordcount > 0:
            words_per_second = (wordcount / interval)
            result.append((current_time, words_per_second))
        logger.info("Successfully calculated rate of speech.")
        return result
    except Exception as e:
        logger.error(f"Error in get_rate_of_speech: {e}", exc_info=True)
        raise

def count_words(words: Dict[Tuple[float, float], str]) -> int:
    logger.info("count_words called")
    try:
        count = len(words)
        logger.info(f"Word count is {count}")
        return count
    except Exception as e:
        logger.error(f"Error in count_words: {e}", exc_info=True)
        raise
