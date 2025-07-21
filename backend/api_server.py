from fastapi import FastAPI, File, UploadFile # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
import shutil
import logging
import video_to_vaw
import speech_to_text
import insert_punctuation
import parts_of_speech
import read_volume
import rate_of_speech
from done_with_some_llm import grammar_tone, sapling
# from gramformer import Gramformer # Import Gramformer
import pose_tracking
import openface

# Initialize Gramformer globally
# models=1 for corrector (default), models=2 for detector
# use_gpu=True if you have a compatible GPU and PyTorch is configured for it
# gf = Gramformer(models=1, use_gpu=False)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log', mode='a'),
        logging.StreamHandler()  # This outputs to console
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS to allow requests from your frontend
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001", # Frontend running on port 3001
    "http://localhost:3002", # Your frontend's common development port
    # Add other origins if your frontend might be hosted elsewhere later
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Grammar Correction Helper Functions ---
# Remove Gramformer and related functions

def get_grammar_corrections(text: str):
    """
    Uses get_mistakes_and_text from grammar_tone.py to return mistakes, corrected text, and highlight spans.
    """
    logger.info("get_grammar_corrections called")
    mistakes_lines, corrected_text, correction_spans = grammar_tone.get_mistakes_and_text(text)
    if mistakes_lines is None:
        mistakes_lines = []
    if corrected_text is None:
        corrected_text = text
    if correction_spans is None:
        correction_spans = []
    return mistakes_lines, corrected_text, correction_spans

# --- FastAPI Routes ---

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Handles video file uploads, processes them for speech analysis,
    and returns various metrics including grammar correction.
    """
    logger.info(f"upload_video called with file: {file.filename}")
    upload_dir = "uploaded_videos"
    os.makedirs(upload_dir, exist_ok=True) # Ensure the directory exists
    if file.filename is None:
        raise Exception("Filename is None in api/upload")
    file_path = os.path.join(upload_dir, file.filename)
    audio_path = None # Initialize audio_path to None for cleanup in finally block

    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("Converting to video to audio")
        # Convert video to WAV audio
        audio_path = video_to_vaw.convert_video_to_wav(file_path)
        logger.info(f"Audio path: {audio_path}")
        if audio_path is None:
            return JSONResponse(status_code=400, content={"error": "No audio track found in video or conversion failed."})

        logger.info("Transcribing")
        # Transcribe speech to words with timestamps
        timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
        
        logger.info("Counting words")
        # Calculate word count
        word_count = rate_of_speech.count_words(timestamped_transcript_by_words)
        
        # Combine words into a single unpunctuated string
        # FIX: Changed 'timestamped_transcript_by_items' to 'timestamped_transcript_by_words'
        full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
        
        logger.info("Adding punctuation")
        # Add punctuation to the full text
        full_text = insert_punctuation.get_punctuated_text(full_unpunctuated_text)
        
        logger.info("Getting grammar corrections")
        # --- Grammar Correction (now using grammar_tone.get_mistakes_and_text) ---
        mistakes_lines, corrected_text, correction_spans = get_grammar_corrections(full_text)
        
        # For highlighting, wrap the corrected spans in <c> tags
        highlighted_text = corrected_text
        # Sort spans in reverse order to avoid messing up indices
        for start, end in sorted(correction_spans, reverse=True):
            highlighted_text = (
                highlighted_text[:start] +
                f'<c>{highlighted_text[start:end]}</c>' +
                highlighted_text[end:]
            )
        
        # Prepare grammar mistakes for frontend (list of [span, suggestion, original])
        grammar_mistakes = []
        for line in mistakes_lines:
            if '"' in line and 'should be' in line:
                try:
                    first_quote = line.find('"')
                    second_quote = line.find('"', first_quote + 1)
                    incorrect_phrase = line[first_quote + 1:second_quote]
                    should_be_idx = line.find("should be", second_quote)
                    third_quote = line.find('"', should_be_idx)
                    fourth_quote = line.find('"', third_quote + 1)
                    correct_phrase = line[third_quote + 1:fourth_quote]
                    grammar_mistakes.append([[start, end], correct_phrase, incorrect_phrase])
                except Exception:
                    continue
            else:
                grammar_mistakes.append([[0, 0], line, line])
        
        corrected_transcript_with_highlights = highlighted_text

        logger.info("Analyzing parts of speech")
        # Analyze parts of speech
        parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
        
        logger.info("Analyzing rate of speech")
        # Calculate rate of speech points over time
        rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
        
        logger.info("Getting volume")
        # Get volume (RMS) points over time
        volume_points_list = read_volume.get_rms_per_segment(audio_path)
        volume_points = {str(ts): float(rms) for ts, rms in volume_points_list}
        
        logger.info("Getting tone")
        # Analyze custom tones (Grammarly-like, now using Sapling)
        custom_tone_results = sapling.get_tone(full_text)

        logger.info("Looking at hands")
        # Analyze hand positions
        hand_position_results_dict = pose_tracking.analyze_hand_positions(file_path)
        hand_position_results_text = pose_tracking.format_analysis_results(hand_position_results_dict)

        logger.info("Getting gaze and face info")
        # OpenFace analysis
        gaze_x, gaze_y, aus_sum = openface.return_numbers(file_path)
        json_content = {"word_count": word_count,
            "parts_of_speech": parts_of_speech_dict,
            "rate_of_speech_points": rate_of_speech_points,
            "volume_points": volume_points,
            "tone_scores": custom_tone_results,
            "custom_tone_results": custom_tone_results,
            "transcript": full_text,
            "corrected_transcript": corrected_transcript_with_highlights, # Send the highlighted text
            "grammar_mistakes": grammar_mistakes,                       # Send parsed mistakes
            "hand_position_results": hand_position_results_text,
            "gaze_angle_x": gaze_x,
            "gaze_angle_y": gaze_y,
            "all_aus_sum": aus_sum,
                        }
        # Return all analysis results as JSON
        return JSONResponse(content=json_content)
    except Exception as e:
        # Log the error for debugging purposes (consider using a proper logging library like 'logging')
        logger.error(f"Error processing video: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"An error occurred during processing: {str(e)}"})
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if audio_path and os.path.exists(audio_path): # Ensure audio_path was successfully assigned before trying to remove
            os.remove(audio_path)
