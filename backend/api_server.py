from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Form # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
import shutil
import uuid
import asyncio
import concurrent.futures
import threading
from typing import Dict, Optional
import aiofiles
from my_logger import get_logger
import video_to_vaw
import speech_to_text
import readability
import active_passive
import parts_of_speech
import read_volume
import rate_of_speech
from done_with_some_llm import grammar_tone, sapling
import openface
# from gramformer import Gramformer # Import Gramformer
import pose_tracking
# import openface  # Removed - not needed
import counts

# --- Job Storage ---
jobs: Dict[str, Dict] = {}

# Create a thread pool executor for CPU-intensive tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Initialize Gramformer globally
# models=1 for corrector (default), models=2 for detector
# use_gpu=True if you have a compatible GPU and PyTorch is configured for it
# gf = Gramformer(models=1, use_gpu=False)

# --- Logging Setup ---
logger = get_logger(__name__)

app = FastAPI()

# Configure CORS to allow requests from your frontend
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001", # Frontend running on port 3001
    "http://localhost:3002",
    "http://commai.online",
    "https://commai.online",
    "https://www.commai.online",
    "http://www.commai.online",
    "*"  # Allow all origins for debugging - remove in production
    # Add other origins if your frontend might be hosted elsewhere later
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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

def process_video_analysis_sync(job_id: str, file_path: str):
    """
    Synchronous video processing function that runs in a separate thread.
    """
    logger.info(f"Starting thread processing for job {job_id}")
    audio_path = None
    
    try:
        # Update job status to processing
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        
        # Convert video to WAV audio
        logger.info("Converting video to audio")
        audio_path = video_to_vaw.convert_video_to_wav(file_path)
        logger.info(f"Audio path: {audio_path}")
        if audio_path is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No audio track found in video or conversion failed."
            return
        
        jobs[job_id]["progress"] = 20

        # Transcribe speech to words with timestamps
        logger.info("Transcribing")
        timestamped_transcript_by_words = speech_to_text.speech_to_words(audio_path=audio_path)
        words = list(timestamped_transcript_by_words.values())
        jobs[job_id]["progress"] = 30
        
        # Calculate word count
        logger.info("Counting words")
        word_count = rate_of_speech.count_words(timestamped_transcript_by_words)
        
        # Combine words into a single unpunctuated string
        full_unpunctuated_text = ' '.join(word for _, word in timestamped_transcript_by_words.items())
        jobs[job_id]["progress"] = 40
        
        # Add punctuation to the full text
        logger.info("Adding punctuation")
        full_text = grammar_tone.fix_punctuation_and_paragraphs(full_unpunctuated_text)
        if full_text is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Failed to add punctuation to text."
            return

        jobs[job_id]["progress"] = 50
        
        # --- Grammar Correction (now using grammar_tone.get_mistakes_and_text) ---
        logger.info("Getting grammar corrections")
        mistakes_lines, corrected_text, correction_spans = get_grammar_corrections(full_text)
        
        # For highlighting, wrap the corrected spans in <c> tags
        highlighted_text = corrected_text
        # Sort spans in reverse order to avoid messing up indices
        start, end = 0, 0
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
        jobs[job_id]["progress"] = 60

        # Analyze parts of speech
        logger.info("Analyzing parts of speech")
        parts_of_speech_dict = parts_of_speech.parts_of_speech(full_text)
        jobs[job_id]["progress"] = 70
        
        # Calculate rate of speech points over time
        logger.info("Analyzing rate of speech")
        rate_of_speech_points = rate_of_speech.get_rate_of_speech(timestamped_transcript_by_words)
        
        # Get volume (RMS) points over time
        logger.info("Getting volume")
        volume_points_list = read_volume.get_rms_per_segment(audio_path)
        volume_points = {str(ts): float(rms) for ts, rms in volume_points_list}
        jobs[job_id]["progress"] = 80
        
        # Analyze custom tones (Grammarly-like, now using Sapling)
        logger.info("Getting tone")
        custom_tone_results = sapling.get_tone(full_text)

        # Analyze hand positions
        logger.info("Looking at hands")
        hand_position_results_dict = pose_tracking.analyze_hand_positions(file_path)
        hand_position_results_text = str(hand_position_results_dict)
        # hand_position_results_text = pose_tracking.format_analysis_results(hand_position_results_dict)
        jobs[job_id]["progress"] = 90

        # Analyze gaze
        logger.info("Looking at gaze")
        gaze_x = [0, 0]
        gaze_y = [0, 0]
        aus_sum = 0
        blinks = 0
        # openface_info = openface.extract_and_get_info(file_path)
        # gaze_x = openface_info["gaze_angle_x"]
        # gaze_y = openface_info["gaze_angle_y"]
        # aus_sum = openface.get_all_aus_sum(openface_info)
        # blinks = openface_info["blinks"]

        # Analyze active
        logger.info("Looking at active/passive")
        active, passive = active_passive.get_active_passive(full_text.split("."))

        # Add readability score
        logger.info("Looking at readability")   
        readability_score = readability.readibility_score(len(full_text.split(".")), words)

        # Add CEFR score
        logger.info("Looking at CEFR")
        ielts_cefr = grammar_tone.get_ielts_and_cefr(full_text)
        if ielts_cefr is None:
            logger.info("IELTS and CEFR scores not found")
            ielts, cefr = "42", "B42"
        else:
            ielts, cefr = ielts_cefr

        # Calculate sentence count
        sentence_count = counts.count_sentences(full_text)

        # Calculate paragraph count
        paragraph_count = counts.count_paragraphs(full_text)

        # Calculate letter count
        letter_count = counts.count_letters(full_text)

        hands_analysis_results = pose_tracking.analyze_hand_positions()["hand_activity"]

        # Prepare final results
        json_content = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "letter_count": letter_count,
            "parts_of_speech": parts_of_speech_dict,
            "rate_of_speech_points": rate_of_speech_points,
            "volume_points": volume_points,
            "tone_scores": custom_tone_results,
            "custom_tone_results": custom_tone_results,
            "transcript": full_text,
            "corrected_transcript": corrected_transcript_with_highlights,
            "grammar_mistakes": grammar_mistakes,
            "hand_position_results": hand_position_results_text,
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "aus_sum": aus_sum,
            "blinks": blinks,
            "active": active,
            "passive": passive,
            "readability_score": readability_score,
            "cefr": cefr,
            "ielts": ielts,
            "hands_analysis_results": hands_analysis_results,
        }
        
        # Update job with results
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["results"] = json_content
        jobs[job_id]["completed_at"] = str(threading.current_thread().ident)
        
        logger.info(f"Job {job_id} completed successfully")
            
    except Exception as e:
        logger.error(f"Error processing video for job {job_id}: {e}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

async def process_video_analysis(job_id: str, file_path: str):
    """
    Async wrapper that runs the sync processing in a thread pool.
    """
    logger.info(f"Starting async wrapper for job {job_id}")
    
    # Run the CPU-intensive work in a separate thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, process_video_analysis_sync, job_id, file_path)

# --- FastAPI Routes ---

@app.options("/api/upload")
async def upload_options():
    """Handle preflight CORS requests"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "3600"
    }
    return JSONResponse(content={"message": "OK"}, headers=headers)

@app.post("/api/start-upload")
async def start_upload(filename: str = Form(...), file_size: int = Form(...)):
    """
    Initialize an upload session and return job ID immediately.
    """
    logger.info(f"start_upload called with filename: {filename}, size: {file_size}")
    
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Check file size (limit to 500MB)
    max_size = 500 * 1024 * 1024  # 500MB
    if file_size > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 500MB.")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job in storage
    jobs[job_id] = {
        "status": "waiting_for_upload",
        "progress": 0,
        "filename": filename,
        "file_size": file_size,
        "uploaded_bytes": 0,
        "created_at": str(asyncio.get_event_loop().time())
    }
    
    logger.info(f"Created upload session for job {job_id}")
    
    return JSONResponse(content={
        "job_id": job_id,
        "status": "ready",
        "message": "Upload session created. You can now upload the file."
    })

@app.post("/api/upload/{job_id}")
async def upload_video_chunk(job_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload video file for a specific job and start processing.
    """
    logger.info(f"upload_video_chunk called for job {job_id}")
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "waiting_for_upload":
        raise HTTPException(status_code=400, detail="Job is not ready for upload")
    
    upload_dir = "uploaded_videos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file with job_id prefix to avoid conflicts
    file_path = os.path.join(upload_dir, f"{job_id}_{job['filename']}")
    
    try:
        # Update status to uploading
        jobs[job_id]["status"] = "uploading"
        jobs[job_id]["progress"] = 1
        
        # Save file with a timeout and smaller chunks
        logger.info(f"Starting file save for job {job_id}")
        
        async with aiofiles.open(file_path, "wb") as buffer:
            # Use smaller chunks and timeout
            chunk_size = 256 * 1024  # 256KB chunks
            total_bytes = 0
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    chunk = await asyncio.wait_for(file.read(chunk_size), timeout=10.0)
                    if not chunk:
                        break
                    await buffer.write(chunk)
                    total_bytes += len(chunk)
                    
                    # Update progress
                    if job["file_size"] > 0:
                        progress = min(int((total_bytes / job["file_size"]) * 80), 80)  # Up to 80% for upload
                        jobs[job_id]["progress"] = progress
                        jobs[job_id]["uploaded_bytes"] = total_bytes
                    
                    # Yield control more frequently
                    if total_bytes % (chunk_size * 4) == 0:  # Every 1MB
                        await asyncio.sleep(0.001)
                        
                except asyncio.TimeoutError:
                    logger.error(f"Timeout reading chunk for job {job_id}")
                    break
            
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.info(f"File save completed for job {job_id}: {total_bytes} bytes in {elapsed:.2f}s")
        
        # Update job status after upload
        jobs[job_id]["status"] = "uploaded"
        jobs[job_id]["progress"] = 5
        jobs[job_id]["uploaded_bytes"] = total_bytes
        
        # Start processing in background
        background_tasks.add_task(process_video_analysis, job_id, file_path)
        
        logger.info(f"Started processing for job {job_id}")
        
        return JSONResponse(content={
            "status": "processing",
            "job_id": job_id,
            "message": "File uploaded successfully. Processing started."
        })
        
    except Exception as e:
        logger.error(f"Error uploading file for job {job_id}: {e}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"Upload failed: {str(e)}"
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/upload")
async def upload_video_immediate(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Read file during request, process in background.
    """
    logger.info(f"Upload called with file: {file.filename}")
    
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "status": "uploading",
        "progress": 1,
        "filename": file.filename,
        "created_at": str(asyncio.get_event_loop().time())
    }
    
    try:
        # Read file content DURING the request (while file stream is open)
        logger.info(f"Reading file content for job {job_id}")
        file_content = await file.read()
        logger.info(f"File content read: {len(file_content)} bytes")
        
        # Define processing function that uses the already-read content
        async def save_and_process():
            upload_dir = "uploaded_videos"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
            
            try:
                # Save to disk using the content we already read
                async with aiofiles.open(file_path, "wb") as buffer:
                    await buffer.write(file_content)
                
                logger.info(f"File saved for job {job_id}: {len(file_content)} bytes")
                
                # Update status and start processing
                jobs[job_id]["status"] = "uploaded"
                jobs[job_id]["progress"] = 5
                
                # Process the video
                await process_video_analysis(job_id, file_path)
                
            except Exception as e:
                logger.error(f"Processing failed for job {job_id}: {e}")
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = str(e)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Start background task
        background_tasks.add_task(save_and_process)
        
        # Return immediately after reading file
        logger.info(f"Returning response for job {job_id}")
        return JSONResponse(content={
            "status": "processing", 
            "job_id": job_id,
            "message": "File received. Processing started."
        })
        
    except Exception as e:
        logger.error(f"Failed to read file for job {job_id}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"Failed to read file: {str(e)}"
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

@app.options("/api/job/{job_id}")
async def job_status_options(job_id: str):
    """Handle preflight CORS requests for job status"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "3600"
    }
    return JSONResponse(content={"message": "OK"}, headers=headers)

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Returns the current status and results of a job.
    """
    # Add explicit CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    
    if job_id not in jobs:
        return JSONResponse(
            content={"status": "error", "error": "Job not found"}, 
            status_code=404,
            headers=headers
        )
    
    job = jobs[job_id]
    
    if job["status"] == "completed":
        return JSONResponse(content={
            "status": "completed",
            "progress": 100,
            "results": job["results"]
        }, headers=headers)
    elif job["status"] == "failed":
        return JSONResponse(content={
            "status": "failed",
            "error": job.get("error", "Unknown error")
        }, headers=headers)
    else:
        return JSONResponse(content={
            "status": job["status"],
            "progress": job.get("progress", 0)
        }, headers=headers)

@app.options("/api/jobs")
async def jobs_options():
    """Handle preflight CORS requests for jobs list"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "3600"
    }
    return JSONResponse(content={"message": "OK"}, headers=headers)

@app.get("/api/jobs")
async def list_jobs():
    """
    Returns a list of all jobs (for debugging and fallback).
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    
    # Return jobs without results for performance
    jobs_summary = {job_id: {k: v for k, v in job.items() if k != "results"} for job_id, job in jobs.items()}
    
    return JSONResponse(content={"jobs": jobs_summary}, headers=headers)

@app.get("/api/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "jobs_count": len(jobs), "timestamp": asyncio.get_event_loop().time()}

@app.get("/api/test-cors")
async def test_cors():
    """
    Test CORS configuration.
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS", 
        "Access-Control-Allow-Headers": "*"
    }
    return JSONResponse(
        content={"message": "CORS test successful", "timestamp": asyncio.get_event_loop().time()},
        headers=headers
    )
