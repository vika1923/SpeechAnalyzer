/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import Image from "next/image";
import { useEffect, useState, useRef } from "react";

export default function Home() {
  const [backendMessage, setBackendMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/hello")
      .then((res) => res.json())
      .then((data) => setBackendMessage(data.message))
      .catch(() => setBackendMessage("Could not connect to backend"));
  }, []);

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
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />
        <ol className="list-inside list-decimal text-sm/6 text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          <li className="mb-2 tracking-[-.01em]">
            Get started by editing{" "}
            <code className="bg-black/[.05] dark:bg-white/[.06] px-1 py-0.5 rounded font-[family-name:var(--font-geist-mono)] font-semibold">
              src/app/page.tsx
            </code>
            .
          </li>
          <li className="tracking-[-.01em]">
            Save and see your changes instantly.
          </li>
        </ol>
        <div className="mb-4 text-center text-base text-blue-600">
          Backend says: {backendMessage}
        </div>
        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
            href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={20}
              height={20}
            />
            Deploy now
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
            href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Read our docs
          </a>
        </div>
        <div className="flex flex-col items-center justify-center min-h-screen p-8">
          <h1 className="text-2xl font-bold mb-4">Video Upload & Analysis</h1>
          <div className="mb-4 text-blue-600">Backend says: {backendMessage}</div>
          <form onSubmit={handleUpload} className="flex flex-col gap-4 w-full max-w-md items-center">
            <input
              type="file"
              accept="video/*"
              ref={fileInputRef}
              className="block"
              disabled={uploading}
            />
            <button
              type="submit"
              className="rounded bg-blue-600 text-white px-4 py-2 disabled:opacity-50"
              disabled={uploading}
            >
              {uploading ? "Uploading..." : "Upload Video"}
            </button>
          </form>
          {error && <div className="text-red-600 mt-2">{error}</div>}
          {results && (
            <div className="mt-6 w-full grid gap-4 grid-cols-1 md:grid-cols-2">
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Transcript</h2>
                <p className="text-sm whitespace-pre-wrap break-words">{results.transcript}</p>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Word Count</h2>
                <p className="text-2xl font-bold">{results.word_count}</p>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Rate of Speech</h2>
                <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(results.rate_of_speech_points, null, 2)}</pre>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Volume Points</h2>
                <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(results.volume_points, null, 2)}</pre>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Tone Scores</h2>
                <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(results.tone_scores, null, 2)}</pre>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow">
                <h2 className="font-bold mb-2 text-highlight">Custom Tone Results</h2>
                <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(results.custom_tone_results, null, 2)}</pre>
              </div>
              <div className="bg-white border-card border-deep p-4 rounded-xl shadow md:col-span-2">
                <h2 className="font-bold mb-2 text-highlight">Parts of Speech</h2>
                <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(results.parts_of_speech, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
