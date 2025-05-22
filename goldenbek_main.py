# import video_to_vaw
from pdf import create_plot
from typing import List, Tuple
import insert_punctuation
# import speech_to_text
import pdf
from predict_flaws import floss
from timestamped_punctuation import timestamp_punctuation_to_index
import video_to_vaw
import speech_to_text
import nltk
import parts_of_speech
import read_volume
import rate_of_speech
import tone_analyzer
import custom_tone_analyzer
import os
import sys

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('averaged_perceptron_tagger_eng')

# Sample text for tone analysis (now with real sentence boundaries)
sample_text = """
Hey there! So, I just wanted to get this off my chest because, honestly, it's been bugging me for a while now. You know how sometimes things just don't go your way, no matter how hard you try? Well, that's pretty much been my week in a nutshell. I mean, I tried to stay positive, but wow, it's like the universe had other plans. 

First off, my phone decided to die on me right when I needed it most. I was supposed to meet up with some friends, but of course, I got lost because my maps wouldn't load. By the time I finally found the place, everyone was already leaving. They were nice about it, but I could tell they were annoyed. I felt like such a flake, even though it wasn't really my fault. 

Then, to top it all off, I spilled coffee all over my favorite shirt right before a video call for work. I tried to laugh it off, but honestly, I just wanted to crawl back into bed and pretend the day hadn't started. My boss noticed, and while she tried to be understanding, I could tell she wasn't impressed. It's just one of those weeks where nothing seems to go right, you know?

I even tried to cheer myself up by ordering my favorite takeout, but they got my order wrong and forgot the fries. Like, come on! Fries are the best part! I called to let them know, and they said they'd give me a discount next time, but it still felt like a letdown. 

I know it's not the end of the world, and I'm trying to keep things in perspective, but it's hard not to feel a little down when everything just keeps piling up. I guess I just needed to vent. Thanks for listening, even if it's just through a screen. Here's hoping next week is a little less of a disaster. Fingers crossed!
"""

# Analyze tone of the sample text (VADER)
tone_scores = tone_analyzer.analyze_tone(sample_text)
tone_description = tone_analyzer.get_tone_description(tone_scores['compound'])
print("\nTone Analysis Results (VADER):")
print(f"Overall Tone: {tone_description}")
print(f"Compound Score: {tone_scores['compound']:.2f}")
print(f"Positive Score: {tone_scores['pos']:.2f}")
print(f"Neutral Score: {tone_scores['neu']:.2f}")
print(f"Negative Score: {tone_scores['neg']:.2f}")

# Analyze tone changes throughout the text (VADER)
segments = tone_analyzer.analyze_text_segments(sample_text)
print("\nTone Analysis by Segments (VADER):")
for i, (segment, scores) in enumerate(segments, 1):
    print(f"\nSegment {i}:")
    print(f"Text: {segment[:100]}...")
    print(f"Tone: {tone_analyzer.get_tone_description(scores['compound'])}")
    print(f"Compound Score: {scores['compound']:.2f}")

# Analyze tones using custom rule-based analyzer (Grammarly-like)
custom_tone_results = custom_tone_analyzer.analyze_tones(sample_text)
print("\nGrammarly-like Tone Analysis:")
custom_tone_analyzer.print_tone_results(custom_tone_results)

# Convert video to WAV
audio_path = video_to_vaw.convert_video_to_wav("videos/IMG_1551.mp4")
print(f"Audio path: {audio_path}")
if audio_path is None:
    raise ValueError()
# Video processing section
video_path = "uploaded_videos/video1880222787.mp4"
if not os.path.exists(video_path):
    print(f"\nError: No video file found at {video_path}")
    print("Please place a video file in the uploaded_videos directory before running this script.")
    sys.exit(1)

# Convert video to WAV
audio_path = video_to_vaw.convert_video_to_wav(video_path)
print(f"Audio path: {audio_path}")
if audio_path is None:
    print("Error: Failed to convert video to audio")
    sys.exit(1)

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

tp2i = timestamp_punctuation_to_index(timestamped_transcript_by_words, full_text)
floss_mistakes = floss(tp2i)

# TODO: change the text to grammar text and fix the indices

os.makedirs("graphs/", exist_ok=True)
create_plot(rate_of_speech_points, "Rate of speech", "Time", "Rate of speech (per second)", "graphs/ros.png")
create_plot(volume_points, "Volume", "Time", "dB", "graphs/vol.png")

# Call the function
# pdf.create_pdf(
#     punctuated_text=full_text,
#     word_count=word_count,
#     parts_of_speech=parts_of_speech_dict,
#     rate_of_speech_points=rate_of_speech_points,
#     volume_points=volume_points,
#     pronunciation_mistakes=[], # TODO: paste in real values
#     floss_mistakes=floss_mistakes,
#     grammar_mistakes=[],       # TODO: paste in real values
# )
# This script is now for backend CLI/testing only. For web UI, use the FastAPI endpoints.
if __name__ == "__main__":
    ...
    # Call the function
    # pdf.create_pdf(
    #     word_count=word_count,
    #     parts_of_speech=parts_of_speech_dict,
    #     rate_of_speech_points=rate_of_speech_points,
    #     volume_points=volume_points
    # )
