"use client";
import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface AnalysisResults {
  transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];  // Array of [timestamp, rate] tuples
  volume_points: Record<string, number>;
  tone_scores: Record<string, number>;
  parts_of_speech: Record<string, number>;
  custom_tone_results?: Record<string, number>;
}

export default function Home() {
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    } catch (err) {
      setError("Could not connect to backend");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <main className="container mx-auto px-4 py-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-center mb-8 text-gray-800"
        >
          Speech Analyzer
        </motion.h1>
        
        <div className="max-w-2xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold mb-6 text-gray-700">Upload Your Video</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div className="relative">
                <input
                  type="file"
                  accept="video/*"
                  ref={fileInputRef}
                  className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors"
                  disabled={uploading}
                />
                {uploading && (
                  <div className="absolute inset-0 bg-white/80 flex items-center justify-center rounded-lg">
                    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                )}
              </div>
              <motion.button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-all"
                disabled={uploading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {uploading ? "Processing..." : "Analyze Speech"}
              </motion.button>
            </form>
            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-4 p-4 bg-red-100 text-red-600 rounded-lg"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <AnimatePresence>
            {results && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-6"
              >
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg shadow-lg p-6"
                >
                  <h3 className="text-xl font-semibold mb-4 text-gray-700">Transcript</h3>
                  <p className="text-gray-600 leading-relaxed">{results.transcript}</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                  >
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">Word Count</h3>
                    <p className="text-3xl font-bold text-blue-600">{results.word_count}</p>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                  >
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">Rate of Speech</h3>
                    <div className="text-sm space-y-2">
                      {results.rate_of_speech_points.map(([time, rate], index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-gray-600">{time.toFixed(1)}s:</span>
                          <span className="font-medium text-blue-600">{(rate * 60).toFixed(1)} words/min</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                  >
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">Volume Analysis</h3>
                    <div className="relative h-32 mt-4">
                      {Object.entries(results.volume_points).map(([time, volume], index) => (
                        <div 
                          key={index}
                          className="absolute bottom-0 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-sm"
                          style={{
                            width: '4px',
                            height: `${volume * 100}%`,
                            left: `${(parseFloat(time) / Object.keys(results.volume_points).length) * 100}%`
                          }}
                        />
                      ))}
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                  >
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">Tone Analysis</h3>
                    <div className="space-y-3">
                      {Object.entries(results.tone_scores).map(([tone, score], index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="capitalize text-gray-600">{tone}</span>
                            <span className="font-medium text-blue-600">{(score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${score * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                </div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg shadow-lg p-6"
                >
                  <h3 className="text-lg font-semibold mb-4 text-gray-700">Parts of Speech</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(results.parts_of_speech).map(([part, count], index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="capitalize text-gray-600">{part.replace('_', ' ')}</span>
                        <span className="font-medium text-blue-600">{count}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
