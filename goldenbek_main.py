# import video_to_vaw
from typing import List, Tuple
import insert_punctuation
# import speech_to_text
import pdf
import video_to_vaw
import speech_to_text
import nltk
import parts_of_speech
import read_volume
import rate_of_speech

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('averaged_perceptron_tagger_eng')

# Convert video to WAV
audio_path = video_to_vaw.convert_video_to_wav("videos/IMG_1551.mp4")
print(f"Audio path: {audio_path}")
if audio_path is None:
    raise ValueError()

# Transcribe speech to text
timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
print(f"Number of words transcribed: {len(timestamped_transcript_by_words)}")
print("First few words:", list(timestamped_transcript_by_words.items())[:5])

# Calculate actual data for PDF generation
word_count = rate_of_speech.count_words(timestamped_transcript_by_words)
print(f"Word count: {word_count}")

# Combine all words into a single text for POS analysis
full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
full_text = insert_punctuation.get_punctuated_text(full_unpunctuated_text)
parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
print("Parts of speech:", parts_of_speech_dict)

# Calculate rate of speech and volume data
rate_of_speech_points: List[Tuple[float, float]] = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
print("Rate of speech points:", rate_of_speech_points)
if not rate_of_speech_points:
    raise Exception("No rate of speech points generated!")

volume_points = read_volume.get_rms_per_segment(audio_path)
print("Volume points:", volume_points[:5])

# Call the function
pdf.create_pdf(
    word_count=word_count,
    parts_of_speech=parts_of_speech_dict,
    rate_of_speech_points=rate_of_speech_points,
    volume_points=volume_points
)
