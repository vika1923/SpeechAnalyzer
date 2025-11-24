import uuid
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime

class JobManager:
    _instance = None
    _jobs: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
        return cls._instance

    def create_job(self, filename: str, file_size: int) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "waiting_for_upload",
            "progress": 0,
            "filename": filename,
            "file_size": file_size,
            "uploaded_bytes": 0,
            "created_at": datetime.now().isoformat(),
            "current_task": "Initialized",
            "results": None,
            "error": None
        }
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, updates: Dict[str, Any]):
        if job_id in self._jobs:
            self._jobs[job_id].update(updates)

    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        # Return a copy to prevent modification
        return {k: v.copy() for k, v in self._jobs.items()}

    def delete_job(self, job_id: str):
        if job_id in self._jobs:
            del self._jobs[job_id]

job_manager = JobManager()
