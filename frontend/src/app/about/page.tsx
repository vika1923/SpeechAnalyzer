"use client";
import Link from "next/link";

export default function About() {
  return (
    // Main container for the page, using custom background color and padding.
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-cream">
      {/* Container for the content, applying a reveal animation. */}
      <div className="reveal-scale max-w-4xl w-full">
        {/* Content card with custom border, background, and spacing. */}
        <div className="border-2 border-deepgreen bg-mintgreen p-8 space-y-6 rounded-lg shadow-lg">
          {/* Main heading with a custom highlight color. */}
          <h1 className="text-blueaccent text-4xl font-bold">About Speech Analyzer</h1>
          {/* Subheadline text with a muted foreground color for readability. */}
          <p className="subheadline text-blackbase text-lg">
            Speech Analyzer is a cutting-edge tool designed for analyzing spoken English from video.
            Simply upload your video to receive instant, insightful feedback on your speech patterns,
            pronunciation, and fluency!
          </p>
          {/* Link to navigate back to the home page. */}
          <div className="float mt-8">
            <Link
              href="/"
              className="inline-block bg-burgundy text-cream px-8 py-4 rounded-full hover:bg-gold transition-colors duration-300 ease-in-out text-lg font-semibold shadow-md"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// This script handles the 'reveal-scale' animation at runtime.
// It observes elements with the 'reveal-scale' class and adds an 'active' class
// when they become visible in the viewport, triggering CSS transitions.
if (typeof window !== 'undefined') {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Add 'active' class when the element enters the viewport
        entry.target.classList.add('active');
      } else {
        // Optionally remove 'active' class when it leaves, if you want it to re-animate on scroll back
        // entry.target.classList.remove('active');
      }
    });
  }, {
    // Options for the IntersectionObserver
    threshold: 0.1 // Trigger when 10% of the element is visible
  });

  // A small delay to ensure the DOM is ready and styles are applied before observing.
  setTimeout(() => {
    document.querySelectorAll('.reveal-scale').forEach((element) => {
      observer.observe(element);
      // Also add 'active' immediately for elements that are already in view on load
      element.classList.add('active');
    });
  }, 100);
}

/*
  CSS for reveal-scale animation (add to your global CSS or component-specific styles):

  .reveal-scale {
    opacity: 0;
    transform: scale(0.9);
    transition: opacity 0.8s ease-out, transform 0.8s ease-out;
  }

  .reveal-scale.active {
    opacity: 1;
    transform: scale(1);
  }
*/
