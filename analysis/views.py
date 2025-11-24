import os
import uuid
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .services.job_manager import job_manager
from .services.processor import start_processing_thread
from django.shortcuts import render
import json

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'analysis/index.html')

def results(request):
    return render(request, 'analysis/results.html')

def about(request):
    return render(request, 'analysis/about.html')

@csrf_exempt
@require_http_methods(["POST"])
def start_upload(request):
    """
    Initialize an upload session and return job ID immediately.
    """
    filename = request.POST.get("filename")
    file_size = request.POST.get("file_size")
    
    if not filename:
        return JsonResponse({"detail": "Filename is required"}, status=400)
    
    try:
        file_size = int(file_size)
    except (ValueError, TypeError):
        return JsonResponse({"detail": "Invalid file size"}, status=400)
        
    # Check file size (limit to 500MB)
    max_size = 500 * 1024 * 1024  # 500MB
    if file_size > max_size:
        return JsonResponse({"detail": "File too large. Maximum size is 500MB."}, status=413)
    
    job_id = job_manager.create_job(filename, file_size)
    
    logger.info(f"Created upload session for job {job_id}")
    
    return JsonResponse({
        "job_id": job_id,
        "status": "ready",
        "message": "Upload session created. You can now upload the file."
    })

@csrf_exempt
@require_http_methods(["POST"])
def upload_video(request):
    """
    Handle file upload. Supports both direct upload and chunked (conceptually, though simplified here).
    """
    # For simplicity in Django, we'll handle standard file uploads
    # If chunking is needed, we'd need more complex logic, but for now let's assume standard upload
    # or we can adapt to the chunked logic if the frontend sends chunks.
    # The original frontend sent chunks to /api/upload/{job_id} or full file to /api/upload
    
    # Let's handle the simple case first: /api/upload with full file
    if 'file' not in request.FILES:
        return JsonResponse({"detail": "No file provided"}, status=400)
        
    file = request.FILES['file']
    filename = file.name
    
    # Create job
    job_id = job_manager.create_job(filename, file.size)
    
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploaded_videos")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{job_id}_{filename}")
    
    try:
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        # Update job
        job_manager.update_job(job_id, {
            "status": "uploaded",
            "progress": 5,
            "uploaded_bytes": file.size
        })
        
        # Start processing
        start_processing_thread(job_id, file_path)
        
        return JsonResponse({
            "status": "processing",
            "job_id": job_id,
            "message": "File uploaded successfully. Processing started."
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        job_manager.update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })
        if os.path.exists(file_path):
            os.remove(file_path)
        return JsonResponse({"detail": str(e)}, status=500)

@require_http_methods(["GET"])
def get_job_status(request, job_id):
    job = job_manager.get_job(job_id)
    if not job:
        return JsonResponse({"status": "error", "error": "Job not found"}, status=404)
        
    if job["status"] == "completed":
        return JsonResponse({
            "status": "completed",
            "progress": 100,
            "current_task": job.get("current_task", "Analysis complete"),
            "results": job["results"]
        })
    elif job["status"] == "failed":
        return JsonResponse({
            "status": "failed",
            "error": job.get("error", "Unknown error")
        })
    else:
        return JsonResponse({
            "status": job["status"],
            "progress": job.get("progress", 0),
            "current_task": job.get("current_task", "Processing...")
        })

@require_http_methods(["GET"])
def list_jobs(request):
    jobs = job_manager.list_jobs()
    # Remove results for summary
    jobs_summary = {job_id: {k: v for k, v in job.items() if k != "results"} for job_id, job in jobs.items()}
    return JsonResponse({"jobs": jobs_summary})

def health_check(request):
    return JsonResponse({"status": "healthy"})
