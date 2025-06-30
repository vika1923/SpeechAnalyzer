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
import openface
# Remove Gramformer import since we're using grammar_tone instead
# from gramformer import Gramformer # Import Gramformer

# Remove Gramformer initialization since we're using grammar_tone instead
# Initialize Gramformer globally
# models=1 for corrector (default), models=2 for detector
# use_gpu=True if you have a compatible GPU and PyTorch is configured for it
# gf = Gramformer(models=1, use_gpu=False)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS to allow requests from your frontend
origins = [
    "http://localhost",
    "http://localhost:3000",
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
# Remove the old Gramformer-based functions and replace with grammar_tone integration
def process_grammar_correction(text_to_check: str):
    """
    Uses the get_mistakes_and_text function from grammar_tone.py to process grammar correction.
    Returns (mistakes_list, corrected_text, correction_spans).
    """
<<<<<<< HEAD
    result = grammar_tone.get_mistakes_and_text(text_to_check)
    if result is None or len(result) < 3:
        # If no mistakes found or error occurred, return empty list and original text
        return [], text_to_check, []
    mistakes_lines, corrected_text, correction_spans = result
    
    # Filter out empty lines and clean up the mistakes
    cleaned_mistakes = []
    for mistake in mistakes_lines:
        mistake = mistake.strip()
        if mistake and mistake != "No corrections needed":
            cleaned_mistakes.append(mistake)
    
    print("corrected with grammar_tone in api_server")
    print(f"Mistakes found: {len(cleaned_mistakes)}")
    print(f"Corrected text: {corrected_text}")
    print(f"Correction spans: {correction_spans}")
    
    return cleaned_mistakes, corrected_text, correction_spans
=======
    logger.info("get_corrected_text called")
    edited_sentences = []
    for influent_sentence in influent_sentences:
        # Correct the sentence, getting only one candidate for simplicity
        corrected_candidates = gf.correct(influent_sentence, max_candidates=1)
        if corrected_candidates is None:
            raise Exception("corrected_candidates is None in Grammar correction helper function")
        for corrected_sentence in corrected_candidates:
            # Highlight the differences between original and corrected sentences
            # The output will include tags like <c orig_tok="original" edit="corrected">original</c>
            edited_sentences.append(gf.highlight(influent_sentence, corrected_sentence))
    print("corrected with gramformer in api_server")
    print(edited_sentences)
    return edited_sentences

def get_parsed_corrections(highlighted_sentences: list[str]) -> list[tuple[tuple[int, int], str]]:
    """
    Parses sentences highlighted by Gramformer to extract mistake details.
    Each mistake is returned as ((start_index_in_highlighted_string, end_index_in_highlighted_string), suggested_correction).
    """
    logger.info("get_parsed_corrections called")
    mistake_details = []
    for highlighted_sentence in highlighted_sentences:
        current_idx = 0
        while True:
            # Find the start of a correction tag: <c
            tag_start = highlighted_sentence.find('<c', current_idx)
            if tag_start == -1:
                break # No more tags found

            # Find the end of the opening tag's attributes and content: >
            tag_content_start = highlighted_sentence.find('>', tag_start)
            if tag_content_start == -1: # Malformed tag
                current_idx = tag_start + 1
                continue

            # Find the closing tag: </c>
            closing_tag_start = highlighted_sentence.find('</c>', tag_content_start)
            if closing_tag_start == -1: # Malformed tag
                current_idx = tag_start + 1
                continue

            # The "incorrect word" is the content *between* the opening '>' and '</c>'
            incorrect_word_in_tag = highlighted_sentence[tag_content_start + 1:closing_tag_start]

            # Extract the 'edit' attribute value
            edit_attr_search_start = tag_start # Search for 'edit=' within the opening tag
            edit_attr_value_start_quote_idx = highlighted_sentence.find("edit='", edit_attr_search_start, tag_content_start)

            correction_text = ""
            if edit_attr_value_start_quote_idx != -1:
                edit_value_start_idx = edit_attr_value_start_quote_idx + len("edit='")
                edit_value_end_quote_idx = highlighted_sentence.find("'", edit_value_start_idx)
                if edit_value_end_quote_idx != -1:
                    correction_text = highlighted_sentence[edit_value_start_idx:edit_value_end_quote_idx]
            
            # The indices returned here are for the highlighted string itself,
            # as Gramformer's highlight method embeds tags directly.
            # If you need mapping to the *original* unhighlighted text,
            # more complex string manipulation (like tokenization and index mapping)
            # would be required before/after Gramformer.
            mistake_details.append(
                ((tag_start, closing_tag_start + 3), correction_text, incorrect_word_in_tag) # (indices in highlighted string, correction, original_word_in_tag)
            )

            # Move past the current closing tag for the next search
            current_idx = closing_tag_start + len('</c>')

    return mistake_details
>>>>>>> aa95176367686ad53c04c035de894d611020186d

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

        # Convert video to WAV audio
        audio_path = video_to_vaw.convert_video_to_wav(file_path)
        if audio_path is None:
            return JSONResponse(status_code=400, content={"error": "No audio track found in video or conversion failed."})

        # Transcribe speech to words with timestamps
        timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
        
        # Calculate word count
        word_count = rate_of_speech.count_words(timestamped_transcript_by_words)
        
        # Combine words into a single unpunctuated string
        # FIX: Changed 'timestamped_transcript_by_items' to 'timestamped_transcript_by_words'
        full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
        
        # Add punctuation to the full text
        full_text = insert_punctuation.get_punctuated_text(full_unpunctuated_text)
        
        # --- Grammar Correction using grammar_tone ---
        grammar_mistakes, corrected_text, correction_spans = process_grammar_correction(full_text)

        # Analyze parts of speech
        parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
        
        # Calculate rate of speech points over time
        rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
        
        # Get volume (RMS) points over time
        volume_points_list = read_volume.get_rms_per_segment(audio_path)
        volume_points = {str(ts): float(rms) for ts, rms in volume_points_list}
        
        # Analyze custom tones (Grammarly-like, now using Sapling)
        custom_tone_results = sapling.get_tone(full_text)

        gaze_x, gaze_y, mimics = openface.return_numbers(file_path)

        # Return all analysis results as JSON
        return JSONResponse(content={
            "word_count": word_count,
            "parts_of_speech": parts_of_speech_dict,
            "rate_of_speech_points": rate_of_speech_points,
            "volume_points": volume_points,
            "tone_scores": custom_tone_results,
            "custom_tone_results": custom_tone_results,
            "transcript": full_text,
            "corrected_transcript": corrected_text,  # Send the corrected text (no highlights needed)
            "grammar_mistakes": grammar_mistakes,    # Send the list of mistake strings
            "correction_spans": correction_spans,    # Send the correction spans for highlighting
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "mimics": mimics,
        })
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
