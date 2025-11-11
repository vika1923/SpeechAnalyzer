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
          <h1 className="text-blueaccent text-4xl font-bold">CommAI - CommLabAUT Team</h1>
          {/* Subheadline text with a muted foreground color for readability. */}
          <div className="flex justify-between items-center">
            <div>
              <p className="subheadline text-blackbase text-lg">
                A Joint Project by CommLabAUT and AI2 Lab
              </p>
              <p className="subheadline text-blackbase text-lg">
                <b> Development Team: </b>
              </p>
              <p className="subheadline text-blackbase text-lg">
                Bahodir Madatov, Viktoriya Kim, Almaz Umbetov
              </p>
              <p className="subheadline text-blackbase text-lg">
                Students of BS Software Engineering (20242028)
              </p>
              <p className="subheadline text-blackbase text-lg">
                <b>Concept and Academic Expertise:</b> Parveen Kumar
              </p>
              <p className="subheadline text-blackbase text-lg">
                <b>Outreach Support</b>: Asilbegim Nasirova
              </p>
              <p className="subheadline text-blackbase text-lg">
                <b>Resource Assistance</b>: AI2 Lab
              </p>
            </div>
            <div>
<p><b>CommLabAUT</b></p>
<p>Communication Lab - American University of Technology</p>
<p>Center for English Language and Communication</p>

<p>Inspired by CommLabASU at Arizona State University, USA, this is a <b>ONE-Place for Comprehensive </b><b>Training</b><b> o</b><b>f</b><b> Communication Skills, Public Speaking</b>, <b>English Language and Career Readiness</b>.</p>

<p>AUT has established this model unit as a pioneering place and has adopted the Methodologies, Strategies and Quality Assurance, committed at CommLabASU. We is proud to mention that the CommLabAUT is the first of its kind CommLab in all Cintana-ASU Partner institutions. We are now sharing this model with other Cintana-ASU Partners.</p>

<p><b>Academic Integration:</b></p>
<p>Dedicated place for <b>Practice and Project Work for Public Speaking Course (COM 225)</b> in all Undergraduate Programs at AUT</p>
<p>Preparation for <b>Academic Presentations </b>(Tasks given in all courses) with <b>feedback</b> from CommLabAUT Mentors</p>
<p><b>Podcast</b> <b>Assignments</b> and distribution on <b>Spotify, Apple Podcasts, Yandex Music, Amazon Music</b></p>
<p>Recording Presentations/Public Speaking and Getting Individual Feedback</p>
<p><b>ASU Global Launch English Certificates</b> (Free) for All AUT Students</p>
<p><b>Learning Townhall Certificate Course </b>(Free and Short Duration) for Business School students (Bachelors and Masters)</p>
<p><b>Internship Program for AUT Students</b> to give them professional exposure of working on projects</p>

<p><b>Professional and Career Development:</b></p>
<p><b>Public Speaking</b> Master classes, short courses, and competitive mentoring</p>
<p><b>Resume Making</b> Masterclasses, Reviews, and personal guidance</p>
<p>Job and Internship <b>Interviews</b> Preparation, including Mock Interviews</p>
<p><b>Scholarship Interviews</b>/Grants Interviews Guidance</p>
<p>Preparation Support for Model United Nations <b>(MUN), TEDx </b>Talks, Motivation Letter/Personal Statements</p>
<p><b>Grammarly</b> for all Students for assistance in English learning</p>
<p><b>English Speaking Club</b>, Books and Movie Reviews, IELTS/TOEFL Tips</p>

<p><b>Outreach Activities:</b></p>
<p><b>Organising Faculty Development Programs/Master Classes</b> on Public Speaking, Presentation Skills, and English Language Competency</p>
<p><b>Business English</b> and English for Specific Purposes (ESP)</p>
<p><b>Upskilling and Feedback-based Analysis Sessions</b> for AUT Partners (Industry and Academics)</p>
<p><b>AUT Preparatory Course and Remedial Course</b> in English Language - Curriculum and Content Designing</p>
<p><b>Career/academic counselling</b> for School Students/Parents</p>

<p><b>Innovation in CommLabAUT:</b></p>
<p>Setting up <b>'CommLab Podcasts'</b> - Yaxshi Conversations!</p>
<p><b>Public Speaking Assessment Tool</b> - "Comm-AI" to analyze Speeches and give personalised feedback for improvement</p>
<p><b>Resume, Interviews, Public Speaking and Presentation Analysis Rubrics</b> for practice</p>
<p>Photos of CommLab Poster as designed by Alex – Attahced and are in Marketing team database.</p>
<p>Photos with Students in the suggested (attached format can be clicked by marketing).</p>
<p><a href="https://newcollege.asu.edu/commlabasu">https://newcollege.asu.edu/commlabasu</a> can be added as Hyperlink where CommLabASU is mentioned.</p>
            </div>
            <div className="ml-8">
              <img src="/team.jpg" alt="Team photo" className="rounded-lg shadow-lg" width="350" />
            </div>
          </div>
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
