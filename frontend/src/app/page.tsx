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
interface AnalysisResults {
  transcript: string;
  corrected_transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores?: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: [[number, number], string, string][];
  custom_tone_results: [number, string, string][];
  hand_position_results: string;
}

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
   * Handles the video file upload process.
   * @param {React.FormEvent | React.ChangeEvent} e - The form or change event.
   */
  const handleUpload = async (e: React.FormEvent | React.ChangeEvent) => {
    e.preventDefault();
    setError("");
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Please select a video file.");
      return;
    }
    
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
    <div className="min-h-screen w-full bg-gradient-to-br from-indigo-500 to-purple-600 flex flex-col items-center justify-center p-4 sm:p-8 font-inter">
      <header className="w-full max-w-6xl mx-auto flex justify-between items-center py-4 px-4 sm:px-0">
        <a href="#" className="text-white text-2xl font-bold font-display">
          Speech Analyzer
        </a>
        <nav className="space-x-4">
          <a href="/about" className="text-white hover:text-blue-200 transition-colors">
            About
          </a>
          <a href="/results" className="text-white hover:text-blue-200 transition-colors">
            Results
          </a>
        </nav>
      </header>

      <main className="container mx-auto px-4 py-8 flex-grow flex flex-col items-center justify-center">
        <div className="w-full md:w-1/2 lg:w-1/2 mx-auto">
          {/* Hero Section */}
          <motion.h1
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl md:text-7xl font-display text-white text-center mb-4 leading-tight"
          >
            <span className="text-blue-200 text-highlight">Analyze Your Speech</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl md:text-2xl text-white text-center max-w-3xl mb-12"
          >
            Get instant, AI-powered feedback on your spoken English. Upload a video and unlock your speaking potential.
          </motion.p>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="border-card border-indigo-700 bg-white p-8 mb-8 shadow-2xl rounded-xl reveal-scale w-full"
          >
            <h2 className="font-display text-3xl text-indigo-700 text-center mb-6"></h2>
            <form onSubmit={handleUpload} className="flex flex-col md:flex-row items-center justify-center md:space-x-8 space-y-6 md:space-y-0">
              <input
                type="file"
                accept="video/*"
                ref={fileInputRef}
                onChange={handleUpload}
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

                <motion.button
                  type="submit"
                  className="w-full max-w-xs bg-indigo-700 text-white py-3 px-6 rounded-full font-semibold hover:bg-indigo-800 disabled:opacity-50 transition-all shadow-md"
                  disabled={isProcessingState}
                  whileHover={{ scale: isProcessingState ? 1 : 1.02 }}
                  whileTap={{ scale: isProcessingState ? 1 : 0.98 }}
                >
                  {uploading ? "Uploading..." : processing ? `Processing... ${progress}%` : "Analyze Speech"}
                </motion.button>
              </div>

              <motion.div
                className={`w-32 h-32 md:w-40 md:h-40 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 ease-in-out
                          ${isProcessingState ? 'bg-gray-200 animate-pulse-slow' : 'bg-indigo-500 hover:bg-indigo-600 shadow-lg'}`}
                onClick={handleMicrophoneClick}
                whileHover={{ scale: isProcessingState ? 1 : 1.05 }}
                whileTap={{ scale: isProcessingState ? 1 : 0.95 }}
                title={isProcessingState ? (uploading ? "Uploading..." : "Processing...") : "Click to upload video"}
              >
                <FaMicrophone className={`text-white text-5xl md:text-6xl ${isProcessingState ? 'animate-bounce' : ''}`} />
              </motion.div>
            </form>

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
        </div>
      </main>

      <footer className="w-full max-w-6xl mx-auto text-center py-8 text-white text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}