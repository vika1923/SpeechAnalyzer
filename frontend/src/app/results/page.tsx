"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import ResultsDisplay from "./ResultsDisplay";
import { motion } from "framer-motion";

// Define the interface for AnalysisResults again, or import it if you move it to a shared types file
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

export default function Results() {
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // This code runs only on the client, after the component mounts
    try {
      const storedResults = sessionStorage.getItem('analysisResults');
      if (storedResults) {
        setResults(JSON.parse(storedResults));
      } else {
        setError("No analysis results found. Please upload a video first.");
      }
    } catch (e) {
      console.error("Failed to parse results from sessionStorage", e);
      setError("There was an error loading your results.");
    }
  }, []); // Empty dependency array ensures this runs once on mount

  return (
    <div className=" relative overflow-hidden min-h-screen w-full bg-[#dbc7fe] flex flex-col items-center p-4 sm:p-8 font-inter">
      <div className="absolute top-1/4 left-0 -translate-y-1/2 -translate-x-1/2 
              w-64 h-64 bg-[#80003a] rotate-45">
      </div>

      <div className="absolute top-1/4 right-0 -translate-y-1/2 translate-x-1/2 
                  w-64 h-64 bg-[#80003a] rotate-45">
      </div>
      <div className="absolute top-3/4 left-0 -translate-y-1/2 -translate-x-1/2 
              w-64 h-64 bg-[#80003a] rotate-45">
      </div>

      <div className="absolute top-3/4 right-0 -translate-y-1/2 translate-x-1/2 
                  w-64 h-64 bg-[#80003a] rotate-45">
      </div>

      <header className="relative w-full max-w-7xl mx-auto flex justify-between items-center py-4 px-4 sm:px-0">
        <a href="/" className="text-white text-2xl font-bold font-display">
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
      
      <main className="relative w-full  max-w-full px-5 py-8 flex-grow flex flex-col items-center justify-center">
        <div className="w-full mx-auto">
          <h1 className="text-4xl font-bold mb-6 text-white text-center">Analysis Results</h1>
          {error && <p className="text-red-300 text-center">{error}</p>}
          {results ? (
            <>
              <ResultsDisplay results={results} />
              <div className="text-center mt-8">
                <motion.button
                  onClick={() => window.location.href = '/'}
                  className="inline-block bg-indigo-700 text-white px-8 py-4 rounded-full hover:bg-indigo-800 transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Analyze Another Video
                </motion.button>
              </div>
            </>
          ) : (
            !error && <p className="text-white text-center">Loading results...</p>
          )}
        </div>
      </main>

      <footer className="relative w-full max-w-6xl mx-auto text-center py-8 text-white text-sm">
        &copy; {new Date().getFullYear()} Speech Analyzer. All rights reserved.
      </footer>
    </div>
  );
}
