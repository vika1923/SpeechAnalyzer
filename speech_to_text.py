from faster_whisper import WhisperModel

audio_path = "SoliyevShort.wav"

model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


def speech_to_words(audio_path):

    segments, _ = model.transcribe(audio_path, language="en", beam_size=5, word_timestamps=True)

    output = {}

    for segment in segments:
        for word in segment.words:
            start = round(word.start, 2)
            end = round(word.end, 2)
            text = word.word.strip()
            
            # Only add if text is not empty
            if text:
                output[(start, end)] = text

    for k, v in output.items():
        print(k, v)