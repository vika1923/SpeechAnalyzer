import video_to_vaw
import speech_to_text

audio_path = video_to_vaw.convert_video_to_wav("videos/com225intro.mp4")
timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
print(timestamped_transcript_by_words)
