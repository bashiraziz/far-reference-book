/**
 * DisclaimerModal component - Shows a disclaimer on first visit
 * Uses localStorage to track acknowledgment
 */

import React, { useState, useEffect } from 'react';
import styles from './DisclaimerModal.module.css';

const DISCLAIMER_KEY = 'far-disclaimer-acknowledged';

export function DisclaimerModal(): JSX.Element | null {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has already acknowledged the disclaimer
    const hasAcknowledged = localStorage.getItem(DISCLAIMER_KEY);
    if (!hasAcknowledged) {
      setIsVisible(true);
    }
  }, []);

  const handleAcknowledge = () => {
    localStorage.setItem(DISCLAIMER_KEY, 'true');
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2>⚠️ Important Disclaimer</h2>
        </div>
        <div className={styles.content}>
          <p>
            <strong>This is NOT an official Federal Acquisition Regulation (FAR) website.</strong>
          </p>
          <p>
            This FAR Reference Book is an independent, open-source educational resource created to make FAR content more accessible. While we strive for accuracy, this site should not be used as a substitute for official FAR documentation.
          </p>
          <p>
            For official FAR information, please visit:{' '}
            <a
              href="https://www.acquisition.gov/browse/index/far"
              target="_blank"
              rel="noopener noreferrer"
            >
              acquisition.gov
            </a>
          </p>
          <p className={styles.warning}>
            Always consult official sources and qualified legal counsel for matters related to federal acquisition and contracting.
          </p>
        </div>
        <div className={styles.footer}>
          <button
            className={styles.acknowledgeButton}
            onClick={handleAcknowledge}
          >
            I Understand and Acknowledge
          </button>
        </div>
      </div>
    </div>
  );
}
