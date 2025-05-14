"use client";
import Link from "next/link";

export default function About() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-background">
      <div className="reveal-scale max-w-4xl w-full">
        <div className="border-card border-deep bg-white p-8 space-y-6">
          <h1 className="text-highlight">About</h1>
          <p className="subheadline text-muted-foreground">
            Speech Analyzer is a tool for analyzing spoken English from video. 
            Upload a video to get instant feedback on your speech!
          </p>
          <div className="float">
            <Link 
              href="/" 
              className="inline-block bg-primary text-primary-foreground px-6 py-3 rounded-full hover:opacity-90 transition-opacity"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Add this script at runtime to handle reveal animations
if (typeof window !== 'undefined') {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
      }
    });
  });

  setTimeout(() => {
    document.querySelectorAll('.reveal-scale').forEach((element) => {
      observer.observe(element);
      element.classList.add('active');
    });
  }, 100);
}
