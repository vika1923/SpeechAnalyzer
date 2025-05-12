from pronunciation_checker import PronunciationAnalyzer, print_pronunciation_analysis
from video_to_vaw import convert_video_to_wav

# Create an analyzer instance
analyzer = PronunciationAnalyzer()

# Analyze pronunciation
audio_file = "video_audios/hello.wav"  # Your audio file
target_text = "Hello hello hello hello hello hello hello"  # The text that should be pronounced

# Get analysis
analysis = analyzer.analyze_pronunciation(audio_file, target_text)

# Print results
print_pronunciation_analysis(analysis)