"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from 'next/navigation';
import {
  PieChart, Pie, Cell, // Add these
} from 'recharts';
import { motion, AnimatePresence } from "framer-motion";
import { FaMicrophone } from "react-icons/fa"; // Make sure to install react-icons: npm install react-icons
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  // ... other imports
  BarChart, Bar, // Add these
  // ... rest of imports
} from 'recharts';

/**
 * Defines the structure for the analysis results returned from the backend.
 * @property {string} transcript - The full transcribed text of the speech.
 * @property {string} corrected_transcript - The grammatically corrected full text, potentially with HTML highlight tags.
 * @property {number} word_count - The total number of words in the transcript.
 * @property {[number, number][]} rate_of_speech_points - An array of [timestamp, rate] tuples,
 * representing speech rate over time.
 * @property {Record<string, number>} volume_points - An object where keys are timestamps (strings)
 * and values are their corresponding volume levels.
 * @property {Record<string, number>} tone_scores - An object where keys are tone categories
 * (e.g., "compound", "pos", "neu", "neg") and values are their scores.
 * @property {Record<string, number>} parts_of_speech - An object where keys are parts of speech
 * (e.g., "NOUN", "VERB") and values are their counts.
 * @property {[[[number, number], string, string]]} grammar_mistakes - An array of grammar mistakes,
 * where each item is a tuple:
 * - [0]: [start_index_in_highlighted_string, end_index_in_highlighted_string]
 * - [1]: The suggested correction string.
 * - [2]: The original incorrect word/phrase as captured by the tag content.
 *  @property {[number, string, string][]} [custom_tone_results] - Optional: results for custom tone analysis.
 */

/**
 * The main Home component for the Speech Analyzer application, styled as a SaaS landing page.
 * Handles video uploads, displays upload status, errors, and analysis results.
 */
export default function App() {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  // User info form state
  const [userName, setUserName] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [organization, setOrganization] = useState("");
  const [role, setRole] = useState<"student" | "teacher" | "working professional" | "guest" | "">("");
  const [formTouched, setFormTouched] = useState(false);
  // Video selection/recording state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recordedChunksRef = useRef<BlobPart[]>([]);

  // Poll job status
  const pollJobStatus = async (jobId: string) => {
    const maxAttempts = 600; // 5 minutes with 1-second intervals
    let attempts = 0;
    
    console.log(`Starting to poll job ${jobId}`);
    
    while (attempts < maxAttempts) {
      try {
        console.log(`Polling attempt ${attempts + 1} for job ${jobId}`);
        
        // Add timeout and retry logic for 524 errors
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000); // 10 second timeout
        
        const res = await fetch(`http://localhost:8000/api/job/${jobId}`, {
          signal: controller.signal,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        clearTimeout(timeoutId);
        
        if (!res.ok) {
          console.error(`Failed to fetch job status: ${res.status} ${res.statusText}`);
          
          // Handle 524 errors specially
          if (res.status === 524) {
            console.log(`Cloudflare timeout (524) for job ${jobId}, will retry...`);
            // Wait longer before retry for 524 errors
            await new Promise(resolve => setTimeout(resolve, 5000));
            attempts--; // Don't count 524 as a real attempt
            continue;
          }
          
          throw new Error(`Failed to fetch job status: ${res.status}`);
        }
        
        const jobData = await res.json();
        console.log(`Job ${jobId} status:`, jobData);
        
        if (jobData.status === 'completed') {
          console.log(`Job ${jobId} completed successfully`);
          setProcessing(false);
          setProgress(100);
          if (jobData.results) {
            // Cleanup any locally stored recorded video once analysis completes
            try { localStorage.removeItem('recordedVideo'); } catch {}
            sessionStorage.setItem('analysisResults', JSON.stringify(jobData.results));
            router.push('/results');
          } else {
            setError('Analysis completed but no results received');
          }
          return;
        } else if (jobData.status === 'failed') {
          console.error(`Job ${jobId} failed:`, jobData.error);
          setProcessing(false);
          setError(jobData.error || 'Processing failed');
          return;
        } else {
          // Update progress for uploading, uploaded, processing states
          const newProgress = jobData.progress || 0;
          console.log(`Job ${jobId} status: ${jobData.status}, progress: ${newProgress}%`);
          setProgress(newProgress);
        }
        
        // Wait 1 second before next poll
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      } catch (err: any) {
        console.error('Error polling job status:', err);
        
        // Try fallback method for 524/network errors
        if (err.name === 'AbortError' || err.message?.includes('Load failed') || err.message?.includes('524')) {
          console.log(`Network error for job ${jobId}, trying fallback...`);
          
          try {
            // Try the /api/jobs endpoint as fallback
            const fallbackRes = await fetch(`http://localhost:8000/api/jobs`, {
              headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
              }
            });
            
            if (fallbackRes.ok) {
              const allJobs = await fallbackRes.json();
              const jobInfo = allJobs.jobs?.[jobId];
              
              if (jobInfo) {
                console.log(`Found job ${jobId} via fallback:`, jobInfo);
                
                if (jobInfo.status === 'completed') {
                  // If completed, try to get results directly
                  setProcessing(false);
                  setProgress(100);
                  // For fallback, we might not have results, so show a message
                  setError('Processing completed but results may not be available. Please try uploading again.');
                  return;
                } else if (jobInfo.status === 'failed') {
                  setProcessing(false);
                  setError(jobInfo.error || 'Processing failed');
                  return;
                } else {
                  // Update progress from fallback
                  setProgress(jobInfo.progress || 0);
                  // Wait longer for next attempt after fallback
                  await new Promise(resolve => setTimeout(resolve, 3000));
                  attempts--; // Don't count fallback attempts
                  continue;
                }
              }
            }
          } catch (fallbackErr) {
            console.error('Fallback also failed:', fallbackErr);
          }
          
          // If we've had many network errors, wait longer
          if (attempts > 10) {
            await new Promise(resolve => setTimeout(resolve, 5000));
          }
          
          attempts--; // Don't count network errors as real attempts
          continue;
        }
        
        setError(`Failed to check processing status: ${err}`);
        setProcessing(false);
        return;
      }
    }
    
    // Timeout
    console.error(`Job ${jobId} polling timed out after ${maxAttempts} attempts`);
    setProcessing(false);
    setError('Processing timed out. Please try again.');
  };

  /**
   * Actually uploads a File to backend and starts polling
   */
  const uploadFileForAnalysis = async (file: File) => {
    setError("");
    setUploading(true);
    setProgress(0);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      // Create an AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000); // 5 minute timeout
      
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        const err = await res.json();
        setError(err.detail || err.error || "Upload failed");
        return;
      }
      
      const uploadData = await res.json();
      
      if (uploadData.status === "processing" && uploadData.job_id) {
        setUploading(false);
        setProcessing(true);
        setJobId(uploadData.job_id);
        setProgress(5);
        
        // Start polling for job status
        pollJobStatus(uploadData.job_id);
      } else {
        setError("Unexpected response from server");
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      if (err.name === 'AbortError') {
        setError("Upload timed out. Please try with a smaller video file or check your connection.");
      } else if (err.message?.includes('fetch')) {
        setError("Could not connect to backend. Please ensure the backend server is running.");
      } else {
        setError("Upload failed. Please try again.");
      }
    } finally {
      setUploading(false);
    }
  };

  /**
   * Triggers the hidden file input when the microphone icon is clicked.
   */
  const handleMicrophoneClick = () => {
    if (fileInputRef.current && !uploading && !processing) {
      fileInputRef.current.click();
    }
  };
  /**
   * Handle file selection without auto-starting analysis
   */
  const handleFileSelected: React.ChangeEventHandler<HTMLInputElement> = async (e) => {
    setError("");
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
    // If user selects a file, clear any recorded video stored earlier
    try { localStorage.removeItem('recordedVideo'); } catch {}
  };
  /**
   * Start recording using MediaRecorder
   */
  const startRecording = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      mediaStreamRef.current = stream;
      recordedChunksRef.current = [];
      const mr = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp8,opus' });
      mediaRecorderRef.current = mr;
      mr.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };
      mr.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        // Save to localStorage as base64 (can be large; acceptable for short recordings)
        const reader = new FileReader();
        reader.onloadend = () => {
          try {
            const base64 = reader.result as string; // data:...;base64,xxxx
            localStorage.setItem('recordedVideo', base64);
            // Also reflect selection in UI by creating a File-like object for display/upload later
            const fileLike = new File([blob], `recording_${Date.now()}.webm`, { type: 'video/webm' });
            setSelectedFile(fileLike);
          } catch (e) {
            console.error('Failed saving recording locally', e);
            setError("Couldn't save the recording locally.");
          }
        };
        reader.readAsDataURL(blob);
        // Stop tracks
        mediaStreamRef.current?.getTracks().forEach(t => t.stop());
        mediaStreamRef.current = null;
        setRecording(false);
      };
      mr.start();
      setRecording(true);
    } catch (e: any) {
      console.error('Recording error', e);
      setError(e?.message || "Failed to access camera/microphone.");
    }
  };
  /**
   * Stop an ongoing recording
   */
  const stopRecording = () => {
    try {
      mediaRecorderRef.current?.stop();
    } catch (e) {
      console.error(e);
      setRecording(false);
    }
  };
  /**
   * Validate form inputs
   */
  const isFormValid = () => {
    return (
      userName.trim().length > 0 &&
      organization.trim().length > 0 &&
      role !== "" &&
      age !== "" &&
      Number.isFinite(Number(age)) &&
      Number(age) > 0
    );
  };
  /**
   * Persist user info for results page
   */
  const persistUserInfo = () => {
    const info = {
      name: userName.trim(),
      age: Number(age),
      organization: organization.trim(),
      role,
    };
    sessionStorage.setItem('userInfo', JSON.stringify(info));
  };
  /**
   * Handler to begin analysis after user clicks button
   */
  const startAnalysis = async () => {
    setFormTouched(true);
    setError("");
    if (!isFormValid()) {
      setError("Please complete all fields in the form.");
      return;
    }
    // Ensure a video source is present either as selected file or in localStorage
    let fileToAnalyze: File | null = selectedFile;
    if (!fileToAnalyze) {
      // Try reconstructing from localStorage
      try {
        const base64 = localStorage.getItem('recordedVideo');
        if (base64) {
          const res = await fetch(base64);
          const blob = await res.blob();
          fileToAnalyze = new File([blob], `recording_${Date.now()}.webm`, { type: blob.type || 'video/webm' });
        }
      } catch (e) {
        console.error('Failed to reconstruct recorded video', e);
      }
    }
    if (!fileToAnalyze) {
      setError("Please upload or record a video first.");
      return;
    }
    // Save user info for results page
    persistUserInfo();
    await uploadFileForAnalysis(fileToAnalyze);
  };

  // Effect to handle 'reveal-scale' and 'reveal' animations at runtime using IntersectionObserver.
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        } else {
          // Optional: remove 'active' if you want elements to re-animate on scroll back into view
          // entry.target.classList.remove('active');
        }
      });
    }, {
      threshold: 0.1 // Trigger when 10% of the element is visible
    });

    const timer = setTimeout(() => {
      document.querySelectorAll('.reveal-scale, .reveal, .float').forEach((element) => {
        observer.observe(element);
        // Add 'active' immediately for elements already in view on load, if desired
        if (element.getBoundingClientRect().top < window.innerHeight) {
          element.classList.add('active');
        }
      });
    }, 100);

    return () => {
      clearTimeout(timer);
      observer.disconnect();
    };
  }, []);

  const isProcessingState = uploading || processing;
  const statusMessage = uploading ? "Uploading your video..." : 
                       processing ? `Processing your video... ${progress}%` : 
                       "Click the microphone to upload your video";

  return (
    <div className="relative overflow-hidden min-h-screen w-full bg-[#dbc7fe] flex flex-col items-center justify-center p-4 sm:p-8 font-inter">
      <div className="absolute top-1/2 left-0 -translate-y-1/2 -translate-x-1/2 
              w-64 h-64 bg-[#80003a] rotate-45">
      </div>

      <div className="absolute top-1/2 right-0 -translate-y-1/2 translate-x-1/2 
                  w-64 h-64 bg-[#80003a] rotate-45">
      </div>

      <header className="relative w-full max-w-6xl mx-auto flex justify-between items-center py-4 px-4 sm:px-0">
        <a href="#" className="text-[#80003a] text-2xl font-bold font-display">
          Speech Analyzer
        </a>
        <nav className="space-x-4">
          <a href="/about" className="text-[#80003a] hover:text[#80003a] transition-colors">
            About
          </a>
          <a href="/results" className="text-[#80003a] hover:text[#80003a] transition-colors">
            Results
          </a>
        </nav>
      </header>

      <main className="relative container mx-auto px-4 py-8 flex-grow flex flex-col items-center justify-center">
        <div className="w-full md:w-1/2 lg:w-1/2 mx-auto">
          
          {/* Hero Section */}
          <motion.h1
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl md:text-7xl font-display text-[#80003a] text-center mb-4 leading-tight"
          >
            <span className="text-[#511b2c] text-highlight">Analyze Your Speech</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl md:text-2xl text-[#80003a] text-center max-w-3xl mb-12"
          >
            Get instant, AI-powered feedback on your spoken English. Upload a video and unlock your speaking potential.
          </motion.p>

          {/* User Info Form */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="border-card border-indigo-700 bg-white p-6 mb-8 shadow-2xl rounded-xl reveal-scale w-full"
          >
            <h2 className="font-display text-2xl text-indigo-700 text-center mb-4">Tell us about you</h2>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  className={`w-full rounded-md border px-3 py-2 outline-none ${formTouched && !userName.trim() ? 'border-red-400' : 'border-gray-300'}`}
                  placeholder="Enter your name"
                  disabled={isProcessingState}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                <input
                  type="number"
                  min={1}
                  value={age}
                  onChange={(e) => setAge(e.target.value === "" ? "" : Number(e.target.value))}
                  className={`w-full rounded-md border px-3 py-2 outline-none ${formTouched && (age === "" || Number(age) <= 0) ? 'border-red-400' : 'border-gray-300'}`}
                  placeholder="Enter your age"
                  disabled={isProcessingState}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Organization</label>
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className={`w-full rounded-md border px-3 py-2 outline-none ${formTouched && !organization.trim() ? 'border-red-400' : 'border-gray-300'}`}
                  placeholder="Enter your organization"
                  disabled={isProcessingState}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as any)}
                  className={`w-full rounded-md border px-3 py-2 outline-none bg-white ${formTouched && role === "" ? 'border-red-400' : 'border-gray-300'}`}
                  disabled={isProcessingState}
                >
                  <option value="" disabled>Select your role</option>
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="working professional">Working Professional</option>
                  <option value="guest">Guest</option>
                </select>
              </div>
            </div>
          </motion.div>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="border-card border-indigo-700 bg-white p-8 mb-8 shadow-2xl rounded-xl reveal-scale w-full"
          >
            <h2 className="font-display text-3xl text-indigo-700 text-center mb-6"></h2>
            <div className="flex flex-col md:flex-row items-center justify-center md:space-x-8 space-y-6 md:space-y-0">
              <input
                type="file"
                accept="video/*"
                ref={fileInputRef}
                onChange={handleFileSelected}
                className="hidden"
                disabled={isProcessingState}
              />

              <div className="flex flex-col items-center space-y-4">
                <p className="text-gray-700 text-lg font-medium text-center">
                  {statusMessage}
                </p>

                {/* Progress Bar */}
                {processing && (
                  <div className="w-full max-w-xs bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                )}

                {/* Selected file / recording status */}
                {selectedFile && (
                  <div className="text-sm text-gray-600">
                    Selected: <span className="font-medium">{selectedFile.name}</span>
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="flex flex-col items-center space-y-3">
                <motion.button
                  type="button"
                  className={`px-5 py-3 rounded-md text-white font-semibold shadow ${recording ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'} disabled:opacity-50`}
                  onClick={recording ? stopRecording : startRecording}
                  disabled={isProcessingState}
                  whileHover={{ scale: isProcessingState ? 1 : 1.02 }}
                  whileTap={{ scale: isProcessingState ? 1 : 0.98 }}
                >
                  {recording ? 'Stop recording' : 'Record live'}
                </motion.button>
                <motion.button
                  type="button"
                  className="px-5 py-3 rounded-md bg-gray-800 text-white font-semibold shadow hover:bg-gray-900 disabled:opacity-50"
                  onClick={handleMicrophoneClick}
                  disabled={isProcessingState}
                  whileHover={{ scale: isProcessingState ? 1 : 1.02 }}
                  whileTap={{ scale: isProcessingState ? 1 : 0.98 }}
                >
                  Upload from device
                </motion.button>
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg text-center"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
          {/* Start Analyzing Button */}
          <div className="w-full flex items-center justify-center">
            <motion.button
              type="button"
              className="inline-block bg-indigo-700 text-white px-8 py-4 rounded-full hover:bg-indigo-800 transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md disabled:opacity-50"
              onClick={startAnalysis}
              disabled={isProcessingState}
              whileHover={{ scale: isProcessingState ? 1 : 1.02 }}
              whileTap={{ scale: isProcessingState ? 1 : 0.98 }}
            >
              Start analyzing
            </motion.button>
          </div>
        </div>
      </main>

      <footer className="relative w-full max-w-6xl mx-auto text-center py-8 text-[#80003a] text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}
