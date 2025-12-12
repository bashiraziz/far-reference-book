/**
 * ProgressIndicator - Reading progress bar and estimated read time
 */

import React, { useEffect, useState } from 'react';
import './ProgressIndicator.css';

export function ProgressIndicator(): JSX.Element {
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY;

      const totalScroll = documentHeight - windowHeight;
      const progress = totalScroll > 0 ? (scrollTop / totalScroll) * 100 : 0;

      setScrollProgress(Math.min(100, Math.max(0, progress)));
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial calculation

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="progress-indicator">
      <div
        className="progress-bar"
        style={{ width: `${scrollProgress}%` }}
        role="progressbar"
        aria-valuenow={Math.round(scrollProgress)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Reading progress"
      />
    </div>
  );
}

export function ReadTimeEstimate(): JSX.Element | null {
  const [readTime, setReadTime] = useState<number>(0);

  useEffect(() => {
    // Calculate read time based on word count
    const article = document.querySelector('article');
    if (!article) return;

    const text = article.textContent || '';
    const wordCount = text.trim().split(/\s+/).length;

    // Average reading speed: 200-250 words per minute
    // Using 225 as a middle ground
    const minutes = Math.ceil(wordCount / 225);

    setReadTime(minutes);
  }, []);

  if (readTime === 0) return null;

  return (
    <div className="read-time-estimate">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
      <span>{readTime} min read</span>
    </div>
  );
}
