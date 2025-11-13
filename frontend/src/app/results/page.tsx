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
  sentence_count: number;
  paragraph_count: number;
  letter_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores?: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: [[number, number], string, string][];
  custom_tone_results: [number, string, string][];
  hand_position_results: string;
  gaze_x?: number[];
  gaze_y?: number[];
  gaze_angle_x?: number[];
  gaze_angle_y?: number[];
  hand_eye_activity_results?: any;
  aus_sum: number;
  blinks: number;
  active: number;
  passive: number;
  readability_score: string;
  cefr: string;
  ielts: string;
  floss_spans: [number, number][];
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
    <div id="results-print-root" className=" relative overflow-hidden min-h-screen w-full bg-[#dbc7fe] flex flex-col items-center p-4 sm:p-8">
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
        <a href="/" className="text-[#80003a] text-2xl font-bold font-display">
          CommAI
        </a>
        <nav className="space-x-4">
          <a href="/about" className="text-[#80003a] hover:text-[#511b2c] transition-colors">
            About
          </a>
          <a href="/results" className="text-[#80003a] hover:text-[#511b2c] transition-colors">
            Results
          </a>
        </nav>
      </header>
      
      <main className="relative w-full  max-w-full px-5 py-8 flex-grow flex flex-col items-center justify-center">
        <div className="w-full mx-auto">
          {error && <p className="text-red-300 text-center">{error}</p>}
          {results ? (
            <>
              <div id="results-capture">
                <h1 className="text-4xl font-bold mb-6 text-[#80003a] text-center">CommAI Analysis</h1>
                <ResultsDisplay results={results} />
              </div>
              <div className="text-center mt-8 flex items-center justify-center gap-4">
                <motion.button
                  id="analyze-another"
                  onClick={() => window.location.href = '/'}
                  className="inline-block bg-indigo-700 text-white px-8 py-4 rounded-full hover:bg-indigo-800 transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Analyze Another Video
                </motion.button>
                <motion.button
                  id="download-pdf"
                  onClick={async () => {
                    try {
                      const el = document.getElementById('results-capture');
                      if (!el) return;

                      // Dynamically load libraries from CDN if not present
                      const loadScript = (src: string) =>
                        new Promise<void>((resolve, reject) => {
                          const existing = document.querySelector(`script[src="${src}"]`);
                          if (existing) return resolve();
                          const s = document.createElement('script');
                          s.src = src;
                          s.async = true;
                          s.onload = () => resolve();
                          s.onerror = () => reject(new Error(`Failed to load ${src}`));
                          document.body.appendChild(s);
                        });

                      const w = window as any;
                      if (!w.html2canvas) {
                        await loadScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js');
                      }
                      if (!w.jspdf) {
                        await loadScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js');
                      }

                      const html2canvas = w.html2canvas as (element: HTMLElement, opts?: any) => Promise<HTMLCanvasElement>;
                      const { jsPDF } = (w.jspdf || {}) as { jsPDF: any };
                      if (!html2canvas || !jsPDF) {
                        throw new Error('Libraries not available');
                      }

                      const canvas = await html2canvas(el, {
                        scale: Math.min(2, window.devicePixelRatio || 1.5),
                        useCORS: true,
                        backgroundColor: '#dbc7fe',
                        windowWidth: el.scrollWidth,
                      });

                      const imgData = canvas.toDataURL('image/png');
                      const pdf = new jsPDF('l', 'mm', 'a4');
                      const pageWidth = pdf.internal.pageSize.getWidth();
                      const pageHeight = pdf.internal.pageSize.getHeight();

                      const imgWidth = pageWidth;
                      const imgHeight = (canvas.height * imgWidth) / canvas.width;

                      if (imgHeight <= pageHeight) {
                        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
                      } else {
                        // Paginate the tall canvas
                        const pxPerMm = canvas.width / imgWidth;
                        const pageHeightPx = pageHeight * pxPerMm;

                        let positionPx = 0;
                        const pageCanvas = document.createElement('canvas');
                        pageCanvas.width = canvas.width;
                        pageCanvas.height = Math.floor(pageHeightPx);
                        const pageCtx = pageCanvas.getContext('2d');
                        if (!pageCtx) throw new Error('Canvas context not available');

                        while (positionPx < canvas.height) {
                          pageCtx.clearRect(0, 0, pageCanvas.width, pageCanvas.height);
                          pageCtx.drawImage(
                            canvas,
                            0,
                            positionPx,
                            canvas.width,
                            Math.min(pageHeightPx, canvas.height - positionPx),
                            0,
                            0,
                            pageCanvas.width,
                            Math.min(pageHeightPx, canvas.height - positionPx)
                          );

                          const pageData = pageCanvas.toDataURL('image/png');
                          pdf.addImage(pageData, 'PNG', 0, 0, imgWidth, pageHeight);

                          positionPx += pageHeightPx;
                          if (positionPx < canvas.height) {
                            pdf.addPage('l');
                          }
                        }
                      }

                      pdf.save('analysis-results.pdf');
                    } catch (e) {
                      console.error('PDF generation failed', e);
                      alert('Failed to generate PDF. Please ensure dependencies are installed.');
                    }
                  }}
                  className="inline-block bg-[#80003a] text-white px-8 py-4 rounded-full hover:bg-[#6b012f] transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Download PDF
                </motion.button>
                <style jsx global>{`
                  /* Improve print fidelity */
                  html, body, #__next, #results-print-root {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                  }
                  @page {
                    size: A4 landscape;
                    margin: 12mm;
                  }
                  /* Avoid splitting cards/charts across pages */
                  .border-card, .rounded-xl, .shadow-xl, .recharts-wrapper {
                    break-inside: avoid;
                    page-break-inside: avoid;
                  }
                  @media print {
                    /* Hide interactive buttons in PDF */
                    #analyze-another,
                    #download-pdf {
                      display: none !important;
                    }
                    /* Disable animations and transforms */
                    * {
                      animation: none !important;
                      transition: none !important;
                    }
                    .reveal, .reveal-scale, .float {
                      transform: none !important;
                      opacity: 1 !important;
                    }
                    /* Ensure background color prints */
                    #results-print-root {
                      background: #dbc7fe !important;
                    }
                    /* Keep SVG/charts within page width */
                    svg {
                      max-width: 100% !important;
                      height: auto !important;
                    }
                  }
                `}</style>
              </div>
            </>
          ) : (
            !error && <p className="text-[#80003a] text-center">Loading results...</p>
          )}
        </div>
      </main>

      <footer className="relative w-full max-w-6xl mx-auto text-center py-8 text-[#80003a] text-sm">
        {new Date().getFullYear()} For Expert Interpretation and Advice, write to CommLabAUT@aut-edu.uz with the Report PDF.
      </footer>
    </div>
  );
}
