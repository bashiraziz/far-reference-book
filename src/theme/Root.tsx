/**
 * Root component - Wraps the entire Docusaurus app.
 *
 * This is where we inject global components like the ChatWidget, ProgressIndicator, and TextToSpeech.
 */

import React from 'react';
import { ChatWidget } from '../components/chatbot/ChatWidget';
import { ProgressIndicator } from '../components/ProgressIndicator';
import { TextToSpeech } from '../components/TextToSpeech';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <>
      <ProgressIndicator />
      {children}
      <ChatWidget />
      <TextToSpeech />
    </>
  );
}
