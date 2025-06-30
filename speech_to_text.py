from faster_whisper import WhisperModel
from typing import Dict
from custom_types import TimeStamp
import logging

# audio_path = "SoliyevShort.wav"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


def speech_to_words(audio_path: str) -> Dict[TimeStamp, str]:
    logger.info(f"speech_to_words called with audio_path: {audio_path}")
    try:
        segments, _ = model.transcribe(audio_path, language="en", beam_size=5, word_timestamps=True)

        output = {}

        for segment in segments:
            for word in segment.words or []:
                start = round(word.start, 2)
                end = round(word.end, 2)
                text = word.word.strip()
                # Only add if text is not empty
                if text:
                    output[(start, end)] = text

        # for k, v in output.items():
        #     print(k, v)
        logger.info("Successfully transcribed speech to words.")
        return output
    except Exception as e:
        logger.error(f"Error in speech_to_words: {e}", exc_info=True)
        raise
