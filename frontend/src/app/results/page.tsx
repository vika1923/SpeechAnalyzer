"use client";
import Link from "next/link";

export default function Results() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-6">Results</h1>
      <p className="mb-4 subheadline">Your previous analysis results will appear here.</p>
      <Link href="/" className="text-blue-600 underline">Back to Home</Link>
    </div>
  );
}
