"use client";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
// Importing a microphone icon from react-icons/fa.
// You might need to install it: npm install react-icons
import { FaMicrophone } from "react-icons/fa";

/**
 * Defines the structure for the analysis results returned from the backend.
 * @property {string} transcript - The full transcribed text of the speech.
 * @property {number} word_count - The total number of words in the transcript.
 * @property {[number, number][]} rate_of_speech_points - An array of [timestamp, rate] tuples,
 * representing speech rate over time.
 * @property {Record<string, number>} volume_points - An object where keys are timestamps (strings)
 * and values are corresponding volume levels.
 * @property {Record<string, number>} tone_scores - An object where keys are tone categories
 * (e.g., "joy", "sadness") and values are their scores.
 * @property {Record<string, number>} parts_of_speech - An object where keys are parts of speech
 * (e.g., "nouns", "verbs") and values are their counts.
 * @property {Record<string, number>} [custom_tone_results] - Optional: results for custom tone analysis.
 */
interface AnalysisResults {
  transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores: Record<string, number>;
  parts_of_speech: Record<string, number>;
  custom_tone_results?: Record<string, number>;
}

/**
 * The main Home component for the Speech Analyzer application, styled as a SaaS landing page.
 * Handles video uploads, displays upload status, errors, and analysis results.
 */
export default function Home() {
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Handles the video file upload process.
   * @param {React.FormEvent} e - The form event.
   */
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResults(null);
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Please select a video file.");
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        setError(err.error || "Upload failed");
        return;
      }
      const data = await res.json();
      setResults(data);
    } catch (_err) {
      setError("Could not connect to backend. Please ensure the backend server is running.");
    } finally {
      setUploading(false);
    }
  };

  /**
   * Triggers the hidden file input when the microphone icon is clicked.
   */
  const handleMicrophoneClick = () => {
    if (fileInputRef.current && !uploading) {
      fileInputRef.current.click();
    }
  };

  return (
    // Main container with a gradient background and animation for a dynamic feel
    <div className="min-h-screen w-full bg-indigo-500 flex flex-col items-center justify-center p-4 sm:p-8">
      {/* Optional: Navigation Header (can be expanded) */}
      <header className="w-full max-w-6xl mx-auto flex justify-between items-center py-4 px-4 sm:px-0">
        <Link href="/" className="text-white text-2xl font-bold font-display">
          Speech Analyzer
        </Link>
        <nav className="space-x-4">
          <Link href="/about" className="text-deepgreen hover:text-blueaccent transition-colors">
            About
          </Link>
          <Link href="/results" className="text-deepgreen hover:text-blueaccent transition-colors">
            Results
          </Link>
        </nav>
      </header>

      {/* Main content area */}
      <main className="container mx-auto px-4 py-8 flex-grow flex flex-col items-center justify-center">
        {/* Hero Section - Main Title and Subtitle */}
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-5xl md:text-7xl font-display text-deepgreen text-center mb-4 leading-tight"
        >
          <span className="text-blueaccent text-highlight">Analyze Your Speech</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-xl md:text-2xl text-white text-center max-w-3xl mb-12"
        >
          Get instant, AI-powered feedback on your spoken English. Upload a video and unlock your speaking potential.
        </motion.p>

        {/* Upload Section - Central card with microphone input */}
        <div className="max-w-2xl w-full mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="border-card border-deepgreen bg-white p-8 mb-8 shadow-2xl reveal-scale"
          >
            <h2 className="font-display text-3xl text-deepgreen text-center mb-6"></h2>
            <form onSubmit={handleUpload} className="space-y-6 flex flex-col items-center">
              {/* Hidden file input */}
              <input
                type="file"
                accept="video/*"
                ref={fileInputRef}
                onChange={handleUpload} // Trigger upload on file selection
                className="hidden" // Hide the default file input
                disabled={uploading}
              />

              {/* Microphone Icon with Clickable Animation */}
              <motion.div
                className={`w-32 h-32 md:w-40 md:h-40 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 ease-in-out
                          ${uploading ? 'bg-white animate-pulse-slow' : 'bg-indigo-500 hover:bg-gold shadow-lg'}`}
                onClick={handleMicrophoneClick}
                whileHover={{ scale: uploading ? 1 : 1.05 }}  
                whileTap={{ scale: uploading ? 1 : 0.95 }}
                title={uploading ? "Processing..." : "Click to upload video"}
              >
                <FaMicrophone className={`text-white text-5xl md:text-6xl ${uploading ? 'animate-bounce' : ''}`} />
              </motion.div>

              {/* Display text indicating action */}
              <p className="text-blackbase text-lg font-medium">
                {uploading ? "Processing your video..." : "Click the microphone to upload your video"}
              </p>

              {/* Analyze Speech Button (optional, can be removed if microphone is primary CTA) */}
              {/* Keeping it for clarity, but the microphone click also triggers upload */}
              <motion.button
                type="submit"
                className="w-full max-w-xs bg-deepgreen text-cream py-3 px-6 rounded-full font-semibold hover:bg-burgundy disabled:opacity-50 transition-all shadow-md"
                disabled={uploading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {uploading ? "Analyzing..." : "Analyze Speech"}
              </motion.button>
            </form>

            {/* Error message display */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-4 p-4 bg-burgundy/10 text-burgundy rounded-lg text-center"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Analysis results section - only visible after successful upload */}
          <AnimatePresence>
            {results && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                transition={{ duration: 0.8 }}
                className="space-y-6 reveal"
              >
                {/* Transcript section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="border-card border-lime bg-mintgreen p-6 shadow-xl"
                >
                  <h3 className="font-display text-xl text-deepgreen mb-4">Transcript</h3>
                  <p className="font-body text-blackbase leading-relaxed">{results.transcript}</p>
                </motion.div>

                {/* Grid for various analysis metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Word Count */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="border-card border-gold bg-mintgreen p-6 shadow-xl"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Word Count</h3>
                    <p className="text-3xl font-bold text-gold">{results.word_count}</p>
                  </motion.div>

                  {/* Rate of Speech */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="border-card border-aqua bg-mintgreen p-6 shadow-xl"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Rate of Speech</h3>
                    <div className="text-sm space-y-2">
                      {results.rate_of_speech_points.map(([time, rate], index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-blackbase">{time.toFixed(1)}s:</span>
                          <span className="font-medium text-blueaccent">{(rate * 60).toFixed(1)} words/min</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Volume Analysis (Placeholder for a chart/visual) */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="border-card border-mintgreen bg-mintgreen p-6 shadow-xl"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Volume Analysis</h3>
                    <div className="relative h-32 mt-4 flex items-end justify-around">
                      {/* This is a simplified representation; a real chart library would be used here */}
                      {Object.entries(results.volume_points).map(([time, volume], index) => {
                        const heightPercent = volume * 100; // Assuming volume is normalized 0-1
                        return (
                          <div
                            key={time}
                            className="volume-bar" // Using the custom volume-bar class
                            style={{
                              height: `${heightPercent}%`,
                              width: `${100 / Object.keys(results.volume_points).length}%`, // Distribute bars evenly
                            }}
                          />
                        );
                      })}
                    </div>
                  </motion.div>

                  {/* Tone Analysis */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="border-card border-burgundy bg-mintgreen p-6 shadow-xl"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Tone Analysis</h3>
                    <div className="space-y-3">
                      {Object.entries(results.tone_scores).map(([tone, score], index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="capitalize text-blackbase">{tone}</span>
                            <span className="font-medium text-burgundy">{(score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-cream rounded-full h-2">
                            <div
                              className="progress-bar" // Using the custom progress-bar class
                              style={{ width: `${score * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                </div>

                {/* Parts of Speech Analysis */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="border-card border-deepgreen bg-mintgreen p-6 shadow-xl"
                >
                  <h3 className="font-display text-lg text-deepgreen mb-4">Parts of Speech</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(results.parts_of_speech).map(([part, count], index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-aqua rounded-lg">
                        <span className="capitalize text-blackbase">{part.replace('_', ' ')}</span>
                        <span className="font-medium text-deepgreen">{count}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Back to Home button for results page */}
                <div className="text-center mt-8">
                  <Link
                    href="/"
                    className="inline-block bg-burgundy text-cream px-8 py-4 rounded-full hover:bg-gold transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
                  >
                    Analyze Another Video
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Optional: Footer */}
      <footer className="w-full max-w-6xl mx-auto text-center py-8 text-blackbase text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}

// This script handles the 'reveal-scale' and 'reveal' animations at runtime.
// It observes elements with these classes and adds an 'active' class
// when they become visible in the viewport, triggering CSS transitions.
if (typeof window !== 'undefined') {
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

  // Observe elements after a small delay to ensure DOM is ready
  setTimeout(() => {
    document.querySelectorAll('.reveal-scale, .reveal, .float').forEach((element) => {
      observer.observe(element);
      // Add 'active' immediately for elements already in view on load, if desired
      element.classList.add('active');
    });
  }, 100);
}

/*
  IMPORTANT: Ensure these CSS styles are present in your global CSS file (e.g., globals.css)
  for the animations and custom classes to work correctly.

  .reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s ease;
  }

  .reveal.active {
    opacity: 1;
    transform: translateY(0);
  }

  .reveal-scale {
    opacity: 0;
    transform: scale(0.9);
    transition: all 0.8s ease;
  }

  .reveal-scale.active {
    opacity: 1;
    transform: scale(1);
  }

  .float {
    // This float class is now primarily for the animation defined in globals.css
    // The specific 'opacity' and 'transform' for initial/active states should be handled
    // by the IntersectionObserver and the 'active' class if you want a reveal effect.
    // Otherwise, it just applies the floating keyframe animation.
    animation: floating 3s ease-in-out infinite;
  }

  // Styles for the volume bars (defined in globals.css)
  // .volume-bar {
  //   @apply absolute bottom-0 bg-gradient-to-t from-deepgreen to-aqua rounded-t-sm pulse-slow;
  //   width: 4px;
  // }

  // Styles for the progress bar (defined in globals.css)
  // .progress-bar {
  //   @apply bg-burgundy h-2 rounded-full transition-all duration-500;
  // }

  // Styles for the loading spinner (defined in globals.css)
  // .loading-spinner {
  //   width: 2rem;
  //   height: 2rem;
  //   border: 3px solid var(--lime);
  //   border-top-color: var(--deepgreen);
  //   border-radius: 50%;
  //   animation: spin 0.8s linear infinite;
  // }

  // Ensure you have font-display and font-body defined in your Tailwind config or global CSS
  // Example in tailwind.config.ts:
  // theme: {
  //   extend: {
  //     fontFamily: {
  //       display: ['Migra', 'serif'],
  //       body: ['Satoshi', 'sans-serif'],
  //     },
  //   },
  // },
*/
