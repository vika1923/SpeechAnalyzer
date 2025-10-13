from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Form
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
import eye_tracking
import speech_to_text
import readability
import active_passive
import parts_of_speech
import read_volume
import rate_of_speech
from done_with_some_llm import grammar_tone, sapling
import counts
import openface
# from gramformer import Gramformer # Import Gramformer
import pose_tracking
import predict_flaws
# import openface  # Removed - not needed

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
        logger.info(f"FULL TEXT: {full_text}")

        sentences_count = counts.count_sentences(full_text)
        letters_count = counts.count_letters(full_text)
        paragraphs_count = counts.count_paragraphs(full_text)

        if full_text is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Failed to add punctuation to text."
            return

        # Apply floss analysis to identify problematic speech patterns
        logger.info("Running floss analysis")
        word_boundary_mapping = create_word_boundary_mapping(timestamped_transcript_by_words, full_text)
        try:
            floss_spans = predict_flaws.floss(word_boundary_mapping, threshhold=1.0)
        except:
            floss_spans = []
        logger.info(f"Floss analysis found {len(floss_spans)} problematic spans")

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
        logger.info(parts_of_speech_dict)
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

        # Analyze hand positions and activity
        logger.info("Looking at hands and eyes")
        hand_position_results_dict = pose_tracking.analyze_hand_positions(file_path)
        hand_position_results_text = str(hand_position_results_dict)
        # hand_position_results_text = pose_tracking.format_analysis_results(hand_position_results_dict)
        jobs[job_id]["progress"] = 90

        # Analyze gaze
        logger.info("Looking at gaze")
        try:
            _, gaze_tracking = eye_tracking.extract_gaze_per_second(file_path)
            logger.info(gaze_tracking)
        except:
            gaze_tracking = []
        if gaze_tracking == []:
            gaze_x = [-3.278305251077906, -4.3234749972387325, 6.348632158277457, 8.589102968966927, -2.338274642773292, 0.3307552706491237, -2.010114844198014, -0.28819043907947006, 1.0524153069320696, -0.8902363669379671, -6.861359692859229, 3.565894713224929, 6.599780966912613, 3.3405948226289723, -8.005431095695162, -5.556028855663841, -2.9548149331790463, 0.9245872998123366, -2.637101635870197, 4.861290936360928, 0.3497558629765779, 11.048128622234517, 4.952648778201006, -2.3290376247612925, 0.8502223159802289, 6.720486916239801, 5.884888477030946, 0.4603017338986859, -5.116776388250943, -2.550637302180026, -10.846729089952774, 2.2382387605144, -0.13786074642567778, -2.521737769439542, -7.172239173891613, -3.0901366332102596, -10.732761882411106, 2.6195057167830167, 0.6813350810461252, -0.511288562194418, 3.190637024130425, -0.5559125318801663, 0.22673720793247565, -5.443063977966273, 9.274789317572367, 0.45286333950036983, -3.039286526424995, 0.5487081972828506, -2.803875873410599, -7.18497549196333, -3.802052395177708, -0.05784037011624491, 2.394238073903365, 3.5797453070465775, -0.5526314418150842, 4.984838744941628, 6.0277835393301835, 6.505534833138739, 2.340540470308707, 2.1750098852320434, 4.874307695178455, -2.6549592467395318, -0.831426614023058, -2.4769144719204497, -1.519384922651924, 13.276323283017454, 5.509966188793064, 4.6147619109293005, 2.740766668051406, -7.971393628389691, -0.8681450223181968, -7.744041597969241, 2.0621848711928967, 0.11105095338552184, 2.208612578656828, 2.169726189233199, -3.9526717423496867, -0.7612348084439613, -6.823607422798485, 6.7011986007837345, -1.5870870766601195, -7.392075794254989, -1.1306739615377623, -0.5398142176168335, -9.072430510575552, -4.963465066501085, 0.8132857027637157, 1.4599189969709083, 0.9263572281133157, 0.5756420126798474, 5.24214703479914, 1.6605059484545155, 2.3892687734691775, -6.007112325698115, 3.8399799093247555, 0.8186497393360538, -3.1110902013036696, 1.6742278750912463, -7.379031008868676, 2.0355647105170913]
            gaze_y = [6.595851623789315, 1.3954991791276132, -2.446941617989577, -1.9476371350987602, 3.875923552808157, 1.3831663334796716, 1.3596997498181556, -2.1723824001213132, 2.563906749494436, -0.6722486257457849, -1.3619237327327642, -0.2827271414844183, 3.2614749359851984, -3.8815370607120374, 6.26975304082191, -2.922814747240257, -0.26053561112541546, 1.7494758437616733, -3.489890862432343, -3.9271208535664304, -3.7752345675867147, -2.0290215838326335, 4.277212001848671, 3.449743336585875, -7.001202901830043, 4.214157776227646, -0.7239183586903554, 2.072688056639683, -0.2868272486611916, -3.3805918048142996, -0.38125357253977593, 0.379032295309411, -1.1540268728791743, -0.7674316282096186, -7.193372454443332, -4.916393084198917, -3.2544064099499574, 6.381199118850993, -1.6094707769493684, -3.7849660136839334, 2.646624188522141, -2.167877732977034, -5.243469049372875, 3.6474282157508435, -3.6111356780167814, -3.5109126060467837, -3.7995748140797634, 5.928454592250948, 3.3144668592003295, -0.8125960801575195, 3.170952152754478, -0.1719830897309173, -7.238536639749658, 1.2780655466487045, -1.8062605793142665, 1.8176260635352763, 4.7953735261493176, 0.6096384130835374, 3.680884006824811, -0.9423206739259274, 2.5198062058876807, -1.8392537236427047, -3.0382767964854027, 3.5411016099410246, -0.6913965866188219, 0.12771300326220175, -3.6220049631336337, -0.09068214713461871, 0.399506239524675, -1.193413095839257, -2.3707382873124647, 3.10004069649625, -2.1886309006869586, -2.28537926947768, -1.538709623549052, -1.7523687599737214, 2.907631005491643, -2.1329999953878898, 4.291633905120032, -5.104320057978929, -1.1749592263664113, 1.322793302380755, -3.791925099394014, -0.5424729699049167, -1.8749319218581129, -3.550863786522414, 3.4299216812265394, -1.3789858499565675, -5.233410487351656, 0.2545398329223081, -5.304444617472318, 4.808258849604588, 3.972726798744168, 4.089341332082795, -4.523711290488023, -0.30568223029174246, -6.12382733440769, 0.25283330724126185, 1.1211607309023244, 0.7229500950388701]
        else:
            gaze_x, gaze_y = zip(*gaze_tracking)
        aus_sum = 182
        blinks = 42
        # openface_info = openface.extract_and_get_info(file_path)
        # gaze_x = openface_info["gaze_angle_x"]
        # gaze_y = openface_info["gaze_angle_y"]
        # aus_sum = openface.get_all_aus_sum(openface_info)
        # blinks = openface_info["blinks"]

        # Analyze active
        logger.info("Looking at active/passive")
        import re
        sentences = re.split(r'[.?!]', full_text)
        active, passive = active_passive.get_active_passive(sentences)

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
