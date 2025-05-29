"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaMicrophone } from "react-icons/fa"; // Make sure to install react-icons: npm install react-icons

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
 * @property {Record<string, number>} [custom_tone_results] - Optional: results for custom tone analysis.
 */
interface AnalysisResults {
  transcript: string;
  corrected_transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: [[[number, number], string, string]][]; // Updated type for grammar_mistakes
  custom_tone_results?: Record<string, number>;
}

/**
 * The main Home component for the Speech Analyzer application, styled as a SaaS landing page.
 * Handles video uploads, displays upload status, errors, and analysis results.
 */
export default function App() {
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Handles the video file upload process.
   * @param {React.FormEvent | React.ChangeEvent} e - The form or change event.
   */
  const handleUpload = async (e: React.FormEvent | React.ChangeEvent) => {
    e.preventDefault();
    setError("");
    setResults(null); // Clear previous results
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
      const data: AnalysisResults = await res.json(); // Type assertion for incoming data
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

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-indigo-500 to-purple-600 flex flex-col items-center justify-center p-4 sm:p-8 font-inter">
      <header className="w-full max-w-6xl mx-auto flex justify-between items-center py-4 px-4 sm:px-0">
        <a href="#" className="text-white text-2xl font-bold font-display">
          Speech Analyzer
        </a>
        <nav className="space-x-4">
          <a href="#" className="text-white hover:text-blue-200 transition-colors">
            About
          </a>
          <a href="#" className="text-white hover:text-blue-200 transition-colors">
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
                disabled={uploading}
              />

              <div className="flex flex-col items-center space-y-4">
                <p className="text-gray-700 text-lg font-medium text-center">
                  {uploading ? "Processing your video..." : "Click the microphone to upload your video"}
                </p>

                <motion.button
                  type="submit"
                  className="w-full max-w-xs bg-indigo-700 text-white py-3 px-6 rounded-full font-semibold hover:bg-indigo-800 disabled:opacity-50 transition-all shadow-md"
                  disabled={uploading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {uploading ? "Analyzing..." : "Analyze Speech"}
                </motion.button>
              </div>

              <motion.div
                className={`w-32 h-32 md:w-40 md:h-40 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 ease-in-out
                          ${uploading ? 'bg-gray-200 animate-pulse-slow' : 'bg-indigo-500 hover:bg-indigo-600 shadow-lg'}`}
                onClick={handleMicrophoneClick}
                whileHover={{ scale: uploading ? 1 : 1.05 }}
                whileTap={{ scale: uploading ? 1 : 0.95 }}
                title={uploading ? "Processing..." : "Click to upload video"}
              >
                <FaMicrophone className={`text-white text-5xl md:text-6xl ${uploading ? 'animate-bounce' : ''}`} />
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

          {/* Analysis results section */}
          <AnimatePresence>
            {results && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                transition={{ duration: 0.8 }}
                className="space-y-6 reveal w-full"
              >
                {/* Original Transcript */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="border-card border-green-500 bg-green-50 p-6 shadow-xl rounded-xl"
                >
                  <h3 className="font-display text-xl text-green-700 mb-4">Original Transcript</h3>
                  <p className="font-body text-gray-800 leading-relaxed">{results.transcript}</p>
                </motion.div>

                {/* Corrected Transcript with Highlights */}
                {results.corrected_transcript && results.corrected_transcript !== results.transcript && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="border-card border-blue-500 bg-blue-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-xl text-blue-700 mb-4">Corrected Transcript</h3>
                    <p
                      className="font-body text-gray-800 leading-relaxed grammar-highlight"
                      dangerouslySetInnerHTML={{ __html: results.corrected_transcript }}
                    />
                    <style jsx global>{`
                      .grammar-highlight c {
                        background-color: #ffd700; /* Gold-like background for highlight */
                        padding: 0 2px;
                        border-radius: 3px;
                        font-weight: bold;
                        text-decoration: underline wavy #ff4500; /* OrangeRed underline for mistakes */
                      }
                      .grammar-highlight c:hover {
                          cursor: help;
                      }
                    `}</style>
                  </motion.div>
                )}

                {/* Grammar Suggestions List */}
                {results.grammar_mistakes && results.grammar_mistakes.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="border-card border-purple-500 bg-purple-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-xl text-purple-700 mb-4">Grammar Suggestions</h3>
                    <ul className="list-disc pl-5 font-body text-gray-800 space-y-2">
                      {results.grammar_mistakes.map((mistake, index) => (
                        <li key={index}>
                          "**{mistake[2]}**" should be "**{mistake[1]}**"
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                )}

                {/* Grid for various analysis metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Word Count */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="border-card border-yellow-500 bg-yellow-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-yellow-700 mb-2">Word Count</h3>
                    <p className="text-3xl font-bold text-yellow-600">{results.word_count}</p>
                  </motion.div>

                  {/* Rate of Speech */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="border-card border-teal-500 bg-teal-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-teal-700 mb-2">Rate of Speech</h3>
                    <div className="text-sm space-y-2 max-h-40 overflow-y-auto custom-scrollbar pr-2">
                      {results.rate_of_speech_points.map(([time, rate], index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-gray-700">{time.toFixed(1)}s:</span>
                          <span className="font-medium text-teal-600">{(rate * 60).toFixed(1)} words/min</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Volume Analysis */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                    className="border-card border-orange-500 bg-orange-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-orange-700 mb-2">Volume Analysis</h3>
                    <div className="relative h-32 mt-4 flex items-end justify-around">
                      {Object.entries(results.volume_points).map(([time, volume], index) => {
                        const heightPercent = Math.min(Math.max(volume, 0), 1) * 100; // Normalize volume to 0-100
                        return (
                          <div
                            key={time}
                            className="w-1/12 bg-orange-400 mx-[1px] rounded-t-sm"
                            style={{
                              height: `${heightPercent}%`,
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
                    transition={{ delay: 0.7 }}
                    className="border-card border-red-500 bg-red-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-red-700 mb-2">Tone Analysis (VADER)</h3>
                    <div className="space-y-3">
                      {/* Filtering common VADER keys for cleaner display */}
                      {Object.entries(results.tone_scores)
                        .filter(([tone]) => ['pos', 'neu', 'neg', 'compound'].includes(tone))
                        .map(([tone, score], index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="capitalize text-gray-800">
                              {tone === 'pos' ? 'Positive' : tone === 'neu' ? 'Neutral' : tone === 'neg' ? 'Negative' : 'Overall (Compound)'}
                            </span>
                            <span className="font-medium text-red-600">
                              {(score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${(tone === 'compound' ? (score + 1) / 2 : score) * 100}%`, /* Compound score scaled to 0-100 */
                                backgroundColor: tone === 'pos' ? '#4CAF50' : tone === 'neg' ? '#F44336' : '#9E9E9E'
                              }}
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
                  transition={{ delay: 0.8 }}
                  className="border-card border-indigo-700 bg-indigo-50 p-6 shadow-xl rounded-xl"
                >
                  <h3 className="font-display text-lg text-indigo-700 mb-4">Parts of Speech</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {Object.entries(results.parts_of_speech)
                      .sort(([, countA], [, countB]) => (countB as number) - (countA as number)) // Sort by count descending
                      .map(([part, count], index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-indigo-100 rounded-lg text-sm">
                          <span className="capitalize text-gray-800">{part.replace('_', ' ')}:</span>
                          <span className="font-medium text-indigo-700">{count}</span>
                        </div>
                    ))}
                  </div>
                </motion.div>

                {/* Analyze Another Video button */}
                <div className="text-center mt-8">
                  <motion.button
                    onClick={() => { setResults(null); setError(""); }}
                    className="inline-block bg-indigo-700 text-white px-8 py-4 rounded-full hover:bg-indigo-800 transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Analyze Another Video
                  </motion.button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="w-full max-w-6xl mx-auto text-center py-8 text-white text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}