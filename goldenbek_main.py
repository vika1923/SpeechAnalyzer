# import video_to_vaw
# import speech_to_text
import pdf
import video_to_vaw
import speech_to_text
import nltk
import librosa
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from collections import defaultdict
import parts_of_speech
import read_volume
import rate_of_speech

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('averaged_perceptron_tagger_eng')

def analyze_parts_of_speech(text):
    """Analyze parts of speech in the given text."""
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    
    pos_counts = defaultdict(int)
    for word, tag in tagged:
        if tag.startswith('NN'):  # Nouns
            pos_counts['nouns'] += 1
        elif tag.startswith('VB'):  # Verbs
            pos_counts['verbs'] += 1
        elif tag.startswith('JJ'):  # Adjectives
            pos_counts['adjectives'] += 1
        elif tag.startswith('RB'):  # Adverbs
            pos_counts['adverbs'] += 1
        elif tag.startswith('PRP'):  # Pronouns
            pos_counts['pronouns'] += 1
        elif tag.startswith('IN'):  # Prepositions
            pos_counts['prepositions'] += 1
        elif tag.startswith('CC'):  # Conjunctions
            pos_counts['conjunctions'] += 1
    
    return dict(pos_counts)

def calculate_rate_of_speech(timestamped_words):
    """Calculate rate of speech at different intervals."""
    if not timestamped_words:
        return []
    
    # Get total duration
    max_time = max(end for (start, end), _ in timestamped_words.items())
    
    # Calculate words per minute at 10-second intervals
    intervals = []
    for time in np.arange(0, max_time, 10):
        words_in_interval = sum(1 for (start, end), _ in timestamped_words.items() 
                              if start >= time and end <= time + 10)
        words_per_minute = (words_in_interval / 10) * 60
        intervals.append((time, words_per_minute))
    
    return intervals

def analyze_volume(audio_path):
    """Analyze volume levels at different intervals."""
    # Load audio file
    y, sr = librosa.load(audio_path)
    
    # Calculate RMS energy
    frame_length = int(sr * 10)  # 10-second frames
    rms = librosa.feature.rms(y=y, frame_length=frame_length)[0]
    
    # Convert to decibels
    db = librosa.amplitude_to_db(rms, ref=np.max)
    
    # Create time points
    times = np.arange(0, len(db) * 10, 10)
    
    return list(zip(times, db))

# Convert video to WAV
audio_path = video_to_vaw.convert_video_to_wav("videos/IMG_1551.mp4")

# Transcribe speech to text
timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)

# Calculate actual data for PDF generation
word_count = rate_of_speech.count_words(timestamped_transcript_by_words)

# Combine all words into a single text for POS analysis
full_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)

# Calculate rate of speech and volume data
rate_of_speech_points = rate_of_speech.rate_of_speech(timestamped_transcript_by_words)
volume_points = read_volume.get_rms_per_segment(audio_path)

# Call the function
pdf.create_pdf(
    word_count=word_count,
    parts_of_speech=parts_of_speech_dict,
    rate_of_speech_points=rate_of_speech_points,
    volume_points=volume_points
)
