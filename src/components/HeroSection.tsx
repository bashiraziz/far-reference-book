/**
 * HeroSection - Eye-catching hero section with gradient and stats
 */

import React from 'react';
import styles from './HeroSection.module.css';

export function HeroSection(): JSX.Element {
  return (
    <div className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>
          Federal Acquisition Regulation (FAR) Reference Book
        </h1>
        <p className={styles.heroSubtitle}>
          Your comprehensive, AI-powered guide to all 53 Parts of the Federal Acquisition Regulations
        </p>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <div className={styles.statValue}>53</div>
            <div className={styles.statLabel}>FAR Parts</div>
          </div>
          <div className={styles.stat}>
            <div className={styles.statValue}>2000+</div>
            <div className={styles.statLabel}>Sections</div>
          </div>
          <div className={styles.stat}>
            <div className={styles.statValue}>AI</div>
            <div className={styles.statLabel}>Powered Search</div>
          </div>
        </div>
      </div>
    </div>
  );
}
