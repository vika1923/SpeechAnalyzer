interface JobStatus {
    status: string;
    progress: number;
    current_task: string;
    job_id?: string;
    results?: any;
    error?: string;
}

const PROCESSING_TASKS = [
    { id: 1, name: "Converting video to audio", threshold: 10 },
    { id: 2, name: "Transcribing speech to text", threshold: 20 },
    { id: 3, name: "Analyzing word patterns", threshold: 30 },
    { id: 4, name: "Adding punctuation and formatting", threshold: 40 },
    { id: 5, name: "Checking grammar and corrections", threshold: 50 },
    { id: 6, name: "Analyzing parts of speech", threshold: 60 },
    { id: 7, name: "Analyzing speech rate and volume", threshold: 70 },
    { id: 8, name: "Analyzing tone and sentiment", threshold: 80 },
    { id: 9, name: "Analyzing body language and gaze", threshold: 90 },
    { id: 10, name: "Calculating proficiency scores", threshold: 95 },
    { id: 11, name: "Analysis complete", threshold: 100 },
];

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    const uploadBtn = document.getElementById('uploadBtn') as HTMLButtonElement;
    const recordBtn = document.getElementById('recordBtn') as HTMLButtonElement;
    const analyzeBtn = document.getElementById('analyzeBtn') as HTMLButtonElement;
    const statusMessage = document.getElementById('statusMessage') as HTMLParagraphElement;
    const progressContainer = document.getElementById('progressContainer') as HTMLDivElement;
    const progressBar = document.getElementById('progressBar') as HTMLDivElement;
    const progressText = document.getElementById('progressText') as HTMLParagraphElement;
    const taskList = document.getElementById('taskList') as HTMLUListElement;
    const errorMessage = document.getElementById('errorMessage') as HTMLDivElement;
    const fileSelection = document.getElementById('fileSelection') as HTMLDivElement;
    const fileName = document.getElementById('fileName') as HTMLSpanElement;

    // Form inputs
    const userNameInput = document.getElementById('userName') as HTMLInputElement;
    const ageInput = document.getElementById('age') as HTMLInputElement;
    const orgInput = document.getElementById('organization') as HTMLInputElement;
    const roleInput = document.getElementById('role') as HTMLSelectElement;

    let selectedFile: File | null = null;
    let isRecording = false;
    let mediaRecorder: MediaRecorder | null = null;
    let recordedChunks: Blob[] = [];
    let stream: MediaStream | null = null;

    // Helper to show error
    const showError = (msg: string) => {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        setTimeout(() => errorMessage.classList.add('hidden'), 5000);
    };

    // Helper to validate form
    const isFormValid = () => {
        return (
            userNameInput.value.trim().length > 0 &&
            ageInput.value.trim().length > 0 &&
            Number(ageInput.value) > 0 &&
            orgInput.value.trim().length > 0 &&
            roleInput.value !== ""
        );
    };

    // File Selection
    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const files = (e.target as HTMLInputElement).files;
        if (files && files.length > 0) {
            selectedFile = files[0];
            fileName.textContent = selectedFile.name;
            fileSelection.classList.remove('hidden');
            errorMessage.classList.add('hidden');
        }
    });

    // Recording Logic
    recordBtn.addEventListener('click', async () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    async function startRecording() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            mediaRecorder = new MediaRecorder(stream);
            recordedChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) recordedChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: 'video/webm' });
                selectedFile = new File([blob], `recording_${Date.now()}.webm`, { type: 'video/webm' });
                fileName.textContent = selectedFile.name;
                fileSelection.classList.remove('hidden');
                
                // Stop tracks
                stream?.getTracks().forEach(track => track.stop());
                stream = null;
            };

            mediaRecorder.start();
            isRecording = true;
            recordBtn.textContent = "Stop Recording";
            recordBtn.classList.replace('bg-indigo-600', 'bg-red-600');
            recordBtn.classList.replace('hover:bg-indigo-700', 'hover:bg-red-700');
        } catch (err) {
            console.error(err);
            showError("Could not access camera/microphone.");
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            recordBtn.textContent = "Record live";
            recordBtn.classList.replace('bg-red-600', 'bg-indigo-600');
            recordBtn.classList.replace('hover:bg-red-700', 'hover:bg-indigo-700');
        }
    }

    // Analysis Logic
    analyzeBtn.addEventListener('click', async () => {
        if (!isFormValid()) {
            showError("Please fill in all fields.");
            return;
        }
        if (!selectedFile) {
            showError("Please select or record a video.");
            return;
        }

        // Save user info to sessionStorage
        const userInfo = {
            name: userNameInput.value,
            age: ageInput.value,
            organization: orgInput.value,
            role: roleInput.value
        };
        sessionStorage.setItem('userInfo', JSON.stringify(userInfo));

        // Start Upload
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Processing...";
        statusMessage.classList.add('hidden');
        progressContainer.classList.remove('hidden');
        
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Upload failed");
            }

            const data = await response.json();
            if (data.job_id) {
                pollJobStatus(data.job_id);
            }

        } catch (err: any) {
            showError(err.message);
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Start analyzing";
            progressContainer.classList.add('hidden');
            statusMessage.classList.remove('hidden');
        }
    });

    async function pollJobStatus(jobId: string) {
        const pollInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/job/${jobId}`);
                if (!res.ok) throw new Error("Failed to fetch status");
                
                const status: JobStatus = await res.json();
                
                // Update Progress
                const progress = status.progress || 0;
                progressBar.style.width = `${progress}%`;
                progressText.textContent = `${progress}%`;

                // Update Task List
                updateTaskList(progress, status.current_task);

                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    window.location.href = `/results?job_id=${jobId}`;
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    showError(status.error || "Analysis failed");
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = "Start analyzing";
                }

            } catch (err) {
                console.error(err);
                // Don't stop polling on transient errors, but maybe limit retries in real app
            }
        }, 1000);
    }

    function updateTaskList(progress: number, currentTaskName: string) {
        taskList.innerHTML = '';
        PROCESSING_TASKS.forEach(task => {
            const li = document.createElement('li');
            li.className = "flex items-center space-x-2";
            
            const isCompleted = progress > task.threshold;
            const isCurrent = currentTaskName === task.name; // Simple string match, might need refinement

            let icon = '';
            let textClass = 'text-gray-500';

            if (isCompleted) {
                icon = `<svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`;
                textClass = 'text-gray-400 line-through';
            } else if (isCurrent) {
                icon = `<svg class="w-4 h-4 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
                textClass = 'text-indigo-600 font-bold';
            } else {
                icon = `<svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="2"></circle></svg>`;
            }

            li.innerHTML = `${icon} <span class="${textClass}">${task.name}</span>`;
            taskList.appendChild(li);
        });
    }
});
