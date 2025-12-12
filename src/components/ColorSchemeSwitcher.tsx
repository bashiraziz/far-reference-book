/**
 * ColorSchemeSwitcher - Allows testing different color schemes
 * Temporary component for evaluating color options
 */

import React, { useState, useEffect } from 'react';
import styles from './ColorSchemeSwitcher.module.css';

const COLOR_SCHEMES = {
  default: {
    name: 'Default Green',
    light: {
      primary: '#2e8555',
      dark: '#29784c',
      darker: '#277148',
      darkest: '#205d3b',
      lightVal: '#33925d',
      lighter: '#359962',
      lightest: '#3cad6e',
    },
    dark: {
      primary: '#25c2a0',
      dark: '#21af90',
      darker: '#1fa588',
      darkest: '#1a8870',
      lightVal: '#29d5b0',
      lighter: '#32d8b4',
      lightest: '#4fddbf',
    },
  },
  govBlue: {
    name: 'Government Blue',
    light: {
      primary: '#1e40af',
      dark: '#1e3a8a',
      darker: '#1e3a8a',
      darkest: '#172554',
      lightVal: '#2563eb',
      lighter: '#3b82f6',
      lightest: '#60a5fa',
    },
    dark: {
      primary: '#3b82f6',
      dark: '#2563eb',
      darker: '#1d4ed8',
      darkest: '#1e40af',
      lightVal: '#60a5fa',
      lighter: '#93c5fd',
      lightest: '#bfdbfe',
    },
  },
  modernIndigo: {
    name: 'Modern Indigo',
    light: {
      primary: '#4f46e5',
      dark: '#4338ca',
      darker: '#3730a3',
      darkest: '#312e81',
      lightVal: '#6366f1',
      lighter: '#818cf8',
      lightest: '#a5b4fc',
    },
    dark: {
      primary: '#818cf8',
      dark: '#6366f1',
      darker: '#4f46e5',
      darkest: '#4338ca',
      lightVal: '#a5b4fc',
      lighter: '#c7d2fe',
      lightest: '#e0e7ff',
    },
  },
  sophisticatedSlate: {
    name: 'Sophisticated Slate',
    light: {
      primary: '#475569',
      dark: '#334155',
      darker: '#1e293b',
      darkest: '#0f172a',
      lightVal: '#64748b',
      lighter: '#94a3b8',
      lightest: '#cbd5e1',
    },
    dark: {
      primary: '#0ea5e9',
      dark: '#0284c7',
      darker: '#0369a1',
      darkest: '#075985',
      lightVal: '#38bdf8',
      lighter: '#7dd3fc',
      lightest: '#bae6fd',
    },
  },
  legalPro: {
    name: 'Legal Professional',
    light: {
      primary: '#1e3a8a',
      dark: '#1e40af',
      darker: '#1d4ed8',
      darkest: '#172554',
      lightVal: '#2563eb',
      lighter: '#3b82f6',
      lightest: '#60a5fa',
    },
    dark: {
      primary: '#93c5fd',
      dark: '#60a5fa',
      darker: '#3b82f6',
      darkest: '#2563eb',
      lightVal: '#bfdbfe',
      lighter: '#dbeafe',
      lightest: '#eff6ff',
    },
  },
};

export function ColorSchemeSwitcher(): JSX.Element {
  const [selectedScheme, setSelectedScheme] = useState<keyof typeof COLOR_SCHEMES>('default');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('color-scheme-test');
    if (saved && saved in COLOR_SCHEMES) {
      setSelectedScheme(saved as keyof typeof COLOR_SCHEMES);
    }
  }, []);

  useEffect(() => {
    const scheme = COLOR_SCHEMES[selectedScheme];
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const colors = isDark ? scheme.dark : scheme.light;

    document.documentElement.style.setProperty('--ifm-color-primary', colors.primary);
    document.documentElement.style.setProperty('--ifm-color-primary-dark', colors.dark);
    document.documentElement.style.setProperty('--ifm-color-primary-darker', colors.darker);
    document.documentElement.style.setProperty('--ifm-color-primary-darkest', colors.darkest);
    document.documentElement.style.setProperty('--ifm-color-primary-light', colors.lightVal);
    document.documentElement.style.setProperty('--ifm-color-primary-lighter', colors.lighter);
    document.documentElement.style.setProperty('--ifm-color-primary-lightest', colors.lightest);

    localStorage.setItem('color-scheme-test', selectedScheme);
  }, [selectedScheme]);

  const handleChange = (scheme: keyof typeof COLOR_SCHEMES) => {
    setSelectedScheme(scheme);
  };

  return (
    <div className={styles.container}>
      <button
        className={styles.toggleButton}
        onClick={() => setIsOpen(!isOpen)}
        title="Test Color Schemes"
      >
        🎨
      </button>

      {isOpen && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <h3>Test Color Schemes</h3>
            <button className={styles.closeButton} onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className={styles.options}>
            {(Object.keys(COLOR_SCHEMES) as Array<keyof typeof COLOR_SCHEMES>).map((key) => (
              <label key={key} className={styles.option}>
                <input
                  type="radio"
                  name="colorScheme"
                  value={key}
                  checked={selectedScheme === key}
                  onChange={() => handleChange(key)}
                />
                <span className={styles.swatch} style={{ background: COLOR_SCHEMES[key].light.primary }}></span>
                <span className={styles.label}>{COLOR_SCHEMES[key].name}</span>
              </label>
            ))}
          </div>
          <p className={styles.note}>
            Toggle dark/light mode to see both versions. Changes are temporary for testing.
          </p>
        </div>
      )}
    </div>
  );
}
