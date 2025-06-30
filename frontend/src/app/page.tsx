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
 * @property {string} corrected_transcript - The grammatically corrected full text (plain text, no highlights).
 * @property {number} word_count - The total number of words in the transcript.
 * @property {[number, number][]} rate_of_speech_points - An array of [timestamp, rate] tuples,
 * representing speech rate over time.
 * @property {Record<string, number>} volume_points - An object where keys are timestamps (strings)
 * and values are their corresponding volume levels.
 * @property {Record<string, number>} tone_scores - An object where keys are tone categories
 * (e.g., "compound", "pos", "neu", "neg") and values are their scores.
 * @property {Record<string, number>} parts_of_speech - An object where keys are parts of speech
 * (e.g., "NOUN", "VERB") and values are their counts.
 * @property {string[]} grammar_mistakes - An array of grammar mistake strings in the format
 * "incorrect_phrase should be correct_phrase".
 * @property {[number, number][]} correction_spans - Array of [start, end] indices for highlights in corrected_transcript.
 *  @property {[number, string, string][]} [custom_tone_results] - Optional: results for custom tone analysis.
 * @property {number} gaze_x - The x-coordinate of the average gaze direction.
 * @property {number} gaze_y - The y-coordinate of the average gaze direction.
 * @property {number} mimics - The number of mimics detected.
 */
interface AnalysisResults {
  transcript: string;
  corrected_transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores?: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: string[];
  correction_spans: [number, number][];
  custom_tone_results: [number, string, string][];
  hand_position_results: string;
  gaze_angle_x: number;
  gaze_angle_y: number;
  all_aus_sum: number;
}

/**
 * The main Home component for the Speech Analyzer application, styled as a SaaS landing page.
 * Handles video uploads, displays upload status, errors, and analysis results.
 */
export default function App() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

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
      const data: AnalysisResults = await res.json();
      sessionStorage.setItem('analysisResults', JSON.stringify(data));
      router.push('/results');
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
<<<<<<< HEAD

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

                {/* Corrected Transcript */}
                {results.corrected_transcript && results.corrected_transcript !== results.transcript && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="border-card border-blue-500 bg-blue-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-xl text-blue-700 mb-4">Corrected Transcript</h3>
                    <p className="font-body text-gray-800 leading-relaxed">
                      {highlightSpans(results.corrected_transcript, results.correction_spans)}
                    </p>
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
                        <li key={index} className="font-medium">
                          {mistake}
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
                 {/* Rate of Speech Chart */}
<motion.div
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: 0.5 }}
    className="border-card border-teal-500 bg-teal-50 p-6 shadow-xl rounded-xl"
>
    <h3 className="font-display text-lg text-teal-700 mb-2">Rate of Speech (Words/Min)</h3>
    <ResponsiveContainer width="100%" height={200}>
        <LineChart data={results.rate_of_speech_points.map(([time, rate]) => ({
            time: time.toFixed(1),
            "Words/Min": (rate * 60).toFixed(1) // Convert to words per minute
        }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0f2f2" />
            <XAxis dataKey="time" label={{ value: "Time (s)", position: "insideBottom", offset: -5 }} />
            <YAxis label={{ value: "Words/Min", angle: -90, position: "insideLeft" }} />
            <Tooltip
                formatter={(value: any, name: string) => [`${value} ${name}`, `Time: ${name === "Words/Min" ? "" : name}s`]}
                labelFormatter={(label: any) => `At ${label}s`}
            />
            <Legend />
            <Line type="monotone" dataKey="Words/Min" stroke="#009688" activeDot={{ r: 8 }} />
        </LineChart>
    </ResponsiveContainer>
</motion.div>

                  {/* Volume Analysis */}
           {/* Volume Analysis Chart */}
<motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: 0.6 }}
    className="border-card border-orange-500 bg-orange-50 p-6 shadow-xl rounded-xl"
>
    <h3 className="font-display text-lg text-orange-700 mb-2">Volume Analysis</h3>
    <ResponsiveContainer width="100%" height={200}>
        <BarChart data={Object.entries(results.volume_points).map(([time, volume]) => ({
            time: time,
            Volume: Math.min(Math.max(volume * 100, 0), 100) // Scale to 0-100 for display
        }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffe0b2" />
            <XAxis dataKey="time" label={{ value: "Time Segment", position: "insideBottom", offset: -5 }} hide={true} /> {/* Hide X-axis labels if too many */}
            <YAxis label={{ value: "Volume (%)", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Volume" fill="#fb923c" />
        </BarChart>
    </ResponsiveContainer>
</motion.div>

                  {/* Tone Analysis (Custom Tone Results) */}
                  {results.custom_tone_results && results.custom_tone_results.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 }}
                      className="border-card border-red-500 bg-red-50 p-6 shadow-xl rounded-xl"
                    >
                      <h3 className="font-display text-lg text-red-700 mb-2">Tone Analysis</h3>
                      <ul className="space-y-2">
                        {results.custom_tone_results.map(([score, label, emoji], idx) => (
                          <li key={idx} className="flex items-center space-x-2">
                            <span className="text-2xl">{emoji}</span>
                            <span className="font-medium text-gray-800">{label}</span>
                            <span className="ml-auto font-semibold text-red-600">{(score * 100).toFixed(1)}%</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* Gaze Direction */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 }}
                    className="border-card border-cyan-500 bg-cyan-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-cyan-700 mb-2">Average Gaze Direction</h3>
                    <p className="text-2xl font-bold text-cyan-600">
                      X: {results.gaze_x.toFixed(2)}, Y: {results.gaze_y.toFixed(2)}
                    </p>
                  </motion.div>

                  {/* Mimics */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.9 }}
                    className="border-card border-lime-500 bg-lime-50 p-6 shadow-xl rounded-xl"
                  >
                    <h3 className="font-display text-lg text-lime-700 mb-2">Mimics</h3>
                    <p className="text-3xl font-bold text-lime-600">{results.mimics.toFixed(2)}</p>
                  </motion.div>
                </div>

                {/* Parts of Speech Analysis */}
           {/* Parts of Speech Analysis Chart */}
<motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.8 }}
    className="border-card border-indigo-700 bg-indigo-50 p-6 shadow-xl rounded-xl"
>
    <h3 className="font-display text-lg text-indigo-700 mb-4">Parts of Speech Distribution</h3>
    <div className="flex flex-col md:flex-row items-center justify-center">
        <ResponsiveContainer width="100%" height={300}>
            <PieChart>
                <Pie
                    data={Object.entries(results.parts_of_speech).map(([part, count]) => ({
                        name: part.replace('_', ' '), // Clean up name for display
                        value: count
                    }))}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    animationBegin={0}
                    animationDuration={800}
                    animationEasing="ease-out"
                >
                    {
                        Object.entries(results.parts_of_speech).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={`hsl(${index * 60}, 70%, 50%)`} /> // Dynamic colors
                        ))
                    }
                </Pie>
                <Tooltip />
                <Legend layout="vertical" align="right" verticalAlign="middle" />
            </PieChart>
        </ResponsiveContainer>
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
=======
>>>>>>> aa95176367686ad53c04c035de894d611020186d
        </div>
      </main>

      <footer className="w-full max-w-6xl mx-auto text-center py-8 text-white text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}