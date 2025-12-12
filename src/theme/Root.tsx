/**
 * Root component - Wraps the entire Docusaurus app.
 *
 * This is where we inject global components like the ChatWidget and DisclaimerModal.
 */

import React from 'react';
import { ChatWidget } from '../components/chatbot/ChatWidget';
import { DisclaimerModal } from '../components/DisclaimerModal';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <>
      <DisclaimerModal />
      {children}
      <ChatWidget />
    </>
  );
}
