"use client";
import { useState, useRef } from "react";
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
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_err) {
      setError("Could not connect to backend");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-animate from-cream via-mintgreen to-aqua">
      <main className="container mx-auto px-4 py-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-6xl font-display text-deepgreen text-center mb-8"
        >
          <span className="text-highlight">Speech Analyzer</span>
        </motion.h1>
        
        <div className="max-w-2xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border-card border-deep bg-white p-8 mb-8 reveal-scale"
          >
            <h2 className="font-display text-2xl text-deepgreen mb-6">Upload Your Video</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div className="relative">
                <input
                  type="file"
                  accept="video/*"
                  ref={fileInputRef}
                  className="w-full p-4 border-2 border-dashed border-aqua rounded-lg cursor-pointer hover:border-lime transition-colors"
                  disabled={uploading}
                />
                {uploading && (
                  <div className="absolute inset-0 bg-white/80 flex items-center justify-center rounded-lg">
                    <div className="w-8 h-8 border-4 border-deepgreen border-t-transparent rounded-full animate-rotate-slow"></div>
                  </div>
                )}
              </div>
              <motion.button
                type="submit"
                className="w-full bg-deepgreen text-cream py-3 px-6 rounded-full font-medium hover:bg-burgundy disabled:opacity-50 transition-all"
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
                  className="mt-4 p-4 bg-burgundy/10 text-burgundy rounded-lg"
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
                  className="border-card border-lime bg-white p-6 reveal"
                >
                  <h3 className="font-display text-xl text-deepgreen mb-4">Transcript</h3>
                  <p className="font-body text-blackbase leading-relaxed">{results.transcript}</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="border-card border-gold bg-white p-6 float"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Word Count</h3>
                    <p className="text-3xl font-bold text-gold">{results.word_count}</p>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="border-card border-aqua bg-white p-6 reveal"
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

                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="border-card border-mint bg-white p-6 reveal"
                  >
                    <h3 className="font-display text-lg text-deepgreen mb-2">Volume Analysis</h3>
                    <div className="relative h-32 mt-4">
                      {Object.entries(results.volume_points).map(([time, volume], index) => {
                        const leftPosition = (parseFloat(time) / Object.keys(results.volume_points).length) * 100;
                        const heightPercent = volume * 100;
                        return (
                          <div 
                            key={index}
                            className="volume-bar"
                            style={{
                              height: `${heightPercent}%`,
                              left: `${leftPosition}%`
                            }}
                          />
                        );
                      })}
                    </div>
                  </motion.div>

                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="border-card border-burgundy bg-white p-6 reveal"
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
                              className="progress-bar"
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
                  className="border-card border-deep bg-white p-6 reveal"
                >
                  <h3 className="font-display text-lg text-deepgreen mb-4">Parts of Speech</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(results.parts_of_speech).map(([part, count], index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-mintgreen rounded-lg">
                        <span className="capitalize text-blackbase">{part.replace('_', ' ')}</span>
                        <span className="font-medium text-deepgreen">{count}</span>
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
