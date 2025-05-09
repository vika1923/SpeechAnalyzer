# import video_to_vaw
# import speech_to_text
import pdf

# audio_path = video_to_vaw.convert_video_to_wav("videos/speechtest.mp4")
# timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
# print(timestamped_transcript_by_words)

import numpy as np
from typing import Dict, List, Tuple

# Generate random suitable data
word_count = 847  # Random word count
parts_of_speech = {
    'nouns': 120,
    'verbs': 95,
    'adjectives': 78,
    'adverbs': 45,
    'pronouns': 62,
    'prepositions': 110,
    'conjunctions': 50
}

# Generate rate of speech data (time in seconds vs words per minute)
rate_of_speech_points = [
    (0.0, 0.0),
    (10.0, 120.0),
    (20.0, 135.0),
    (30.0, 125.0),
    (40.0, 140.0),
    (50.0, 130.0)
]

# Generate volume data (time in seconds vs decibel level)
volume_points = [
    (0.0, 50.0),
    (10.0, 55.0),
    (20.0, 60.0),
    (30.0, 58.0),
    (40.0, 62.0),
    (50.0, 59.0)
]

# Call the function
pdf.create_pdf(
    word_count=word_count,
    parts_of_speech=parts_of_speech,
    rate_of_speech_points=rate_of_speech_points,
    volume_points=volume_points
)
