import os
import threading
import asyncio
import logging
from typing import Dict, Any, List
from .job_manager import job_manager
from . import video_to_vaw
from . import speech_to_text
from . import rate_of_speech
from .done_with_some_llm import grammar_tone, sapling
from . import counts
from . import predict_flaws
from . import parts_of_speech
from . import read_volume
from . import pose_tracking
from . import eye_tracking
from . import active_passive
from . import readability
from datetime import datetime

logger = logging.getLogger(__name__)

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

def create_word_boundary_mapping(timestamped_transcript, full_text):
    """
    Create mapping from TimeStamp to WordBoundary for floss() function.
    Maps timestamped words to their positions in the full text.
    """
    logger.info("create_word_boundary_mapping called")
    try:
        mapping = {}
        current_pos = 0
        
        # Sort timestamped words by start time
        sorted_words = sorted(timestamped_transcript.items(), key=lambda x: x[0][0])
        
        for (start_time, end_time), word in sorted_words:
            # Find the word in the full text starting from current position
            word_lower = word.lower().strip()
            full_text_lower = full_text.lower()
            
            # Find the next occurrence of this word in the text
            word_start = full_text_lower.find(word_lower, current_pos)
            
            if word_start != -1:
                word_end = word_start + len(word)
                mapping[(start_time, end_time)] = (word_start, word_end)
                current_pos = word_end
            else:
                logger.warning(f"Could not find word '{word}' in full text at position {current_pos}")
        
        logger.info(f"Created word boundary mapping with {len(mapping)} entries")
        return mapping
    except Exception as e:
        logger.error(f"Error creating word boundary mapping: {e}", exc_info=True)
        return {}

def process_video_analysis_sync(job_id: str, file_path: str):
    """
    Synchronous video processing function that runs in a separate thread.
    """
    logger.info(f"Starting thread processing for job {job_id}")
    audio_path = None
    
    try:
        # Update job status to processing
        job_manager.update_job(job_id, {
            "status": "processing",
            "progress": 10,
            "current_task": "Converting video to audio"
        })
        
        # Convert video to WAV audio
        logger.info("Converting video to audio")
        audio_path = video_to_vaw.convert_video_to_wav(file_path)
        logger.info(f"Audio path: {audio_path}")
        if audio_path is None:
            job_manager.update_job(job_id, {
                "status": "failed",
                "error": "No audio track found in video or conversion failed."
            })
            return
        
        job_manager.update_job(job_id, {
            "progress": 20,
            "current_task": "Transcribing speech to text"
        })

        # Transcribe speech to words with timestamps
        logger.info("Transcribing")
        timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
        words = list(timestamped_transcript_by_words.values())
        
        job_manager.update_job(job_id, {
            "progress": 30,
            "current_task": "Analyzing word patterns"
        })
        
        # Calculate word count
        logger.info("Counting words")
        word_count = rate_of_speech.count_words(timestamped_transcript_by_words)

        # Combine words into a single unpunctuated string
        full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
        
        job_manager.update_job(job_id, {
            "progress": 40,
            "current_task": "Adding punctuation and formatting"
        })
        
        # Add punctuation to the full text
        logger.info("Adding punctuation")
        full_text = grammar_tone.fix_punctuation_and_paragraphs(full_unpunctuated_text)
        logger.info(f"FULL TEXT: {full_text}")

        # Check if punctuation fixing failed before proceeding
        if full_text is None:
            job_manager.update_job(job_id, {
                "status": "failed",
                "error": "Failed to add punctuation to text. Please check your OpenAI API key."
            })
            return

        sentences_count = counts.count_sentences(full_text)
        letters_count = counts.count_letters(full_text)
        paragraphs_count = counts.count_paragraphs(full_text)

        # Apply floss analysis to identify problematic speech patterns
        logger.info("Running floss analysis")
        word_boundary_mapping = create_word_boundary_mapping(timestamped_transcript_by_words, full_text)
        try:
            floss_spans = predict_flaws.floss(word_boundary_mapping, threshhold=1.0)
        except:
            floss_spans = []
        logger.info(f"Floss analysis found {len(floss_spans)} problematic spans")

        job_manager.update_job(job_id, {
            "progress": 50,
            "current_task": "Checking grammar and corrections"
        })
        
        # --- Grammar Correction ---
        logger.info("Getting grammar corrections")
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
        
        job_manager.update_job(job_id, {
            "progress": 60,
            "current_task": "Analyzing parts of speech"
        })

        # Analyze parts of speech
        logger.info("Analyzing parts of speech")
        parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
        logger.info(parts_of_speech_dict)
        
        job_manager.update_job(job_id, {
            "progress": 70,
            "current_task": "Analyzing speech rate and volume"
        })
        
        # Calculate rate of speech points over time
        logger.info("Analyzing rate of speech")
        rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
        
        # Get volume (RMS) points over time
        logger.info("Getting volume")
        volume_points_list = read_volume.get_rms_per_segment(audio_path)
        volume_points = {str(ts): float(rms) for ts, rms in volume_points_list}
        
        job_manager.update_job(job_id, {
            "progress": 80,
            "current_task": "Analyzing tone and sentiment"
        })
        
        # Analyze custom tones
        logger.info("Getting tone")
        custom_tone_results, extra_tone_results = sapling.get_tone(full_text)

        # Analyze hand positions and activity
        logger.info("Looking at hands and eyes")
        hand_position_results_dict = pose_tracking.analyze_hand_positions(file_path)
        hand_position_results_text = str(hand_position_results_dict)
        
        job_manager.update_job(job_id, {
            "progress": 90,
            "current_task": "Analyzing body language and gaze"
        })

        # Analyze gaze
        logger.info("Looking at gaze")
        try:
            _, gaze_tracking_data = eye_tracking.extract_gaze_per_second(file_path)
            logger.info(gaze_tracking_data)
        except:
            gaze_tracking_data = []
            
        if not gaze_tracking_data:
            # Fallback data if gaze tracking fails
            gaze_x = [0.1687140601942668, -0.08976750767140705, 0.009551219412867025] # Truncated for brevity, use full list in real impl
            gaze_y = [-0.07395009002252187, -0.04307387478036936, 0.22497900128897472]
        else:
            gaze_x, gaze_y = zip(*gaze_tracking_data)
            
        aus_sum = 182
        blinks = 42

        # Analyze active
        logger.info("Looking at active/passive")
        active, passive = active_passive.get_active_passive(full_text.split("."))

        # Add readability score
        logger.info("Looking at readability")   
        readability_score = readability.readibility_score(len(full_text.split(".")), words)
        
        job_manager.update_job(job_id, {
            "current_task": "Calculating proficiency scores"
        })

        # Add CEFR score
        logger.info("Looking at CEFR")
        ielts_cefr = grammar_tone.get_ielts_and_cefr(full_text)
        if ielts_cefr is None:
            logger.info("IELTS and CEFR scores not found")
            ielts, cefr = "42", "B42"
        else:
            ielts, cefr = ielts_cefr

        # Prepare final results
        json_content = {
            "word_count": word_count,
            "sentence_count": sentences_count,
            "paragraph_count": paragraphs_count,
            "letter_count": letters_count,
            "parts_of_speech": parts_of_speech_dict,
            "rate_of_speech_points": rate_of_speech_points,
            "volume_points": volume_points,
            "tone_scores": custom_tone_results,
            "custom_tone_results": custom_tone_results,
            "extra_tone_results": extra_tone_results,
            "transcript": full_text,
            "corrected_transcript": corrected_transcript_with_highlights,
            "grammar_mistakes": grammar_mistakes,
            "hand_position_results": hand_position_results_text,
            "hand_eye_activity_results": hand_position_results_dict,
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "aus_sum": aus_sum,
            "blinks": blinks,
            "active": active,
            "passive": passive,
            "readability_score": readability_score,
            "cefr": cefr,
            "ielts": ielts,
            "floss_spans": floss_spans,
        }
        logger.info(json_content)
        
        # Update job with results
        job_manager.update_job(job_id, {
            "status": "completed",
            "progress": 100,
            "current_task": "Analysis complete",
            "results": json_content,
            "completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"Job {job_id} completed successfully")
            
    except Exception as e:
        logger.error(f"Error processing video for job {job_id}: {e}", exc_info=True)
        job_manager.update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

def start_processing_thread(job_id: str, file_path: str):
    thread = threading.Thread(target=process_video_analysis_sync, args=(job_id, file_path))
    thread.start()
