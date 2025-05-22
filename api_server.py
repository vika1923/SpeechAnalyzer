from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import video_to_vaw
import speech_to_text
import insert_punctuation
import parts_of_speech
import read_volume
import rate_of_speech
import tone_analyzer
import custom_tone_analyzer

app = FastAPI()

# Configure CORS here
origins = [
    "http://localhost",
    "http://localhost:3000", # Keep this one as it's common
    "http://localhost:3002", # ADD THIS ONE - This is where your frontend is currently running
    # You can add other origins if your frontend might be hosted elsewhere later
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello")
def read_root():
    return {"message": "Hello from Python backend!"}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    # Save uploaded file
    upload_dir = "uploaded_videos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_path = video_to_vaw.convert_video_to_wav(file_path)
    if audio_path is None:
        return JSONResponse(status_code=400, content={"error": "No audio track found in video."})

    timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
    word_count = rate_of_speech.count_words(timestamped_transcript_by_words)
    full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
    full_text = insert_punctuation.get_punctuated_text(full_unpunctuated_text)
    parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
    rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
    volume_points = read_volume.get_rms_per_segment(audio_path)
    tone_scores = tone_analyzer.analyze_tone(full_text)
    custom_tone_results = custom_tone_analyzer.analyze_tones(full_text)

    return {
        "word_count": word_count,
        "parts_of_speech": parts_of_speech_dict,
        "rate_of_speech_points": rate_of_speech_points,
        "volume_points": volume_points,
        "tone_scores": tone_scores,
        "custom_tone_results": custom_tone_results,
        "transcript": full_text
    }