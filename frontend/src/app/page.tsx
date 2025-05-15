"use client";
import { useEffect, useState, useRef } from "react";

interface AnalysisResults {
  transcript: string;
  word_count: number;
  rate_of_speech_points: Record<string, number>;
  volume_points: Record<string, number>;
  tone_scores: Record<string, number>;
  parts_of_speech: Record<string, number>;
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
        setUploading(false);
        return;
      }
      const data = await res.json();
      setResults(data);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      setError("Could not connect to backend");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-center mb-8">Speech Analyzer</h1>
        <div className="max-w-2xl mx-auto">
          <div className="border-card border-deep p-8 mb-8">
            <h2 className="mb-6">Upload Your Video</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <input
                  type="file"
                  accept="video/*"
                  ref={fileInputRef}
                  className="w-full p-2 border rounded"
                  disabled={uploading}
                />
              </div>
              <button
                type="submit"
                className="w-full bg-primary text-primary-foreground py-3 px-6 rounded-full hover:opacity-90 disabled:opacity-50"
                disabled={uploading}
              >
                {uploading ? "Processing..." : "Analyze Speech"}
              </button>
            </form>
            {error && (
              <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded">
                {error}
              </div>
            )}
          </div>

          {results && (
            <div className="space-y-6">
              <div className="border-card border-deep p-6">
                <h3 className="mb-4">Transcript</h3>
                <p className="text-foreground">{results.transcript}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border-card border-mint p-6">
                  <h3 className="mb-2">Word Count</h3>
                  <p className="text-2xl font-bold">{results.word_count}</p>
                </div>

                <div className="border-card border-aqua p-6">
                  <h3 className="mb-2">Rate of Speech</h3>
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(results.rate_of_speech_points, null, 2)}
                  </pre>
                </div>

                <div className="border-card border-lime p-6">
                  <h3 className="mb-2">Volume Analysis</h3>
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(results.volume_points, null, 2)}
                  </pre>
                </div>

                <div className="border-card border-deep p-6">
                  <h3 className="mb-2">Tone Analysis</h3>
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(results.tone_scores, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="border-card border-burgundy p-6">
                <h3 className="mb-2">Parts of Speech</h3>
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(results.parts_of_speech, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
