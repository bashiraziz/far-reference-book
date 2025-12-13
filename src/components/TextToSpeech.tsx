import React, { useState, useEffect, useRef } from 'react';
import './TextToSpeech.css';

export function TextToSpeech(): JSX.Element {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.0);
  const [isExpanded, setIsExpanded] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Check if speech synthesis is supported
  const isSpeechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  const getArticleText = (): string => {
    // Get main article content, excluding navigation and other UI elements
    const article = document.querySelector('article');
    if (!article) return '';

    // Clone the article to avoid modifying the original
    const clone = article.cloneNode(true) as HTMLElement;

    // Remove elements we don't want to read
    const selectorsToRemove = [
      'nav',
      '.breadcrumbs',
      '.theme-doc-toc-mobile',
      '.theme-doc-footer',
      '.pagination-nav',
      'button',
      '.hash-link',
      'script',
      'style',
    ];

    selectorsToRemove.forEach(selector => {
      clone.querySelectorAll(selector).forEach(el => el.remove());
    });

    return clone.textContent?.trim() || '';
  };

  const handlePlay = () => {
    if (!isSpeechSupported) {
      alert('Text-to-speech is not supported in your browser.');
      return;
    }

    const text = getArticleText();
    if (!text) {
      alert('No content found to read.');
      return;
    }

    // If already paused, just resume
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    // Create new utterance
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = speechRate;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsPlaying(false);
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const handlePause = () => {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
    setIsPaused(false);
  };

  const handleRateChange = (newRate: number) => {
    setSpeechRate(newRate);

    // If currently playing, restart with new rate
    if (isPlaying || isPaused) {
      handleStop();
      setTimeout(() => {
        handlePlay();
      }, 100);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isSpeechSupported) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!isSpeechSupported) {
    return null; // Don't render if not supported
  }

  return (
    <div className={`text-to-speech ${isExpanded ? 'expanded' : ''}`}>
      <button
        className="tts-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-label="Toggle audio reader"
        title="Listen to page content"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
        </svg>
      </button>

      {isExpanded && (
        <div className="tts-controls">
          <div className="tts-buttons">
            {!isPlaying && !isPaused && (
              <button onClick={handlePlay} className="tts-btn tts-play" title="Play">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              </button>
            )}

            {isPlaying && (
              <button onClick={handlePause} className="tts-btn tts-pause" title="Pause">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
              </button>
            )}

            {isPaused && (
              <button onClick={handlePlay} className="tts-btn tts-resume" title="Resume">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              </button>
            )}

            <button onClick={handleStop} className="tts-btn tts-stop" title="Stop" disabled={!isPlaying && !isPaused}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <rect x="5" y="5" width="14" height="14" />
              </svg>
            </button>
          </div>

          <div className="tts-rate-control">
            <label htmlFor="speech-rate">Speed:</label>
            <select
              id="speech-rate"
              value={speechRate}
              onChange={(e) => handleRateChange(parseFloat(e.target.value))}
              className="tts-rate-select"
            >
              <option value="0.5">0.5x</option>
              <option value="0.75">0.75x</option>
              <option value="1">1x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="1.75">1.75x</option>
              <option value="2">2x</option>
            </select>
          </div>

          {(isPlaying || isPaused) && (
            <div className="tts-status">
              {isPlaying && <span className="status-indicator playing">Playing</span>}
              {isPaused && <span className="status-indicator paused">Paused</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
