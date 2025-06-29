from fastapi import FastAPI, File, UploadFile # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
import shutil
import video_to_vaw
import speech_to_text
import insert_punctuation
import parts_of_speech
import read_volume
import rate_of_speech
<<<<<<< HEAD
import tone_analyzer
import custom_tone_analyzer
from gramformer import Gramformer # type: ignore
=======
from done_with_some_llm import grammar_tone, sapling
from gramformer import Gramformer # Import Gramformer

>>>>>>> a3504f0afaacb0d9bf5b10dc0f7903f4c0c1f10f
# Initialize Gramformer globally
# models=1 for corrector (default), models=2 for detector
# use_gpu=True if you have a compatible GPU and PyTorch is configured for it
gf = Gramformer(models=1, use_gpu=False)

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
def get_corrected_text(influent_sentences: list[str]) -> list[str]:
    """
    Corrects a list of sentences using Gramformer and highlights changes.
    Returns a list of corrected sentences, with diffs highlighted using <c> tags.
    """
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

# --- FastAPI Routes ---

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Handles video file uploads, processes them for speech analysis,
    and returns various metrics including grammar correction.
    """
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
        
        # --- Grammar Correction ---
        # Get corrected text with highlights
        # Gramformer works best on complete sentences. If full_text is very long, 
        # consider splitting it into sentences before passing to get_corrected_text.
        corrected_highlighted_texts = get_corrected_text([full_text])
        
        # Parse mistakes from the highlighted text. Assumes only one sentence was processed.
        grammar_mistakes = get_parsed_corrections(corrected_highlighted_texts)
        
        # The corrected transcript (with highlight tags)
        corrected_transcript_with_highlights = corrected_highlighted_texts[0] if corrected_highlighted_texts else full_text

        # Analyze parts of speech
        parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
        
        # Calculate rate of speech points over time
        rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
        
        # Get volume (RMS) points over time
        volume_points_list = read_volume.get_rms_per_segment(audio_path)
        volume_points = {str(ts): float(rms) for ts, rms in volume_points_list}
        
        # Analyze tone (VADER-like, legacy)
        tone_scores = sapling.get_tone(full_text)  # This is now a list of lists: [[number, string, string], ...]

        # Analyze custom tones (Grammarly-like, now using Sapling)
        custom_tone_results = sapling.get_tone(full_text)

        # Return all analysis results as JSON
        return JSONResponse(content={
            "word_count": word_count,
            "parts_of_speech": parts_of_speech_dict,
            "rate_of_speech_points": rate_of_speech_points,
            "volume_points": volume_points,
            "tone_scores": {},  # Deprecated, kept for backward compatibility
            "custom_tone_results": custom_tone_results,
            "transcript": full_text,
            "corrected_transcript": corrected_transcript_with_highlights, # Send the highlighted text
            "grammar_mistakes": grammar_mistakes,                       # Send parsed mistakes
        })
    except Exception as e:
        # Log the error for debugging purposes (consider using a proper logging library like 'logging')
        print(f"Error processing video: {e}")
        return JSONResponse(status_code=500, content={"error": f"An error occurred during processing: {str(e)}"})
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if audio_path and os.path.exists(audio_path): # Ensure audio_path was successfully assigned before trying to remove
            os.remove(audio_path)
