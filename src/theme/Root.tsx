/**
 * Root component - Wraps the entire Docusaurus app.
 *
 * This is where we inject global components like the ChatWidget.
 */

import React from 'react';
import { ChatWidget } from '../components/chatbot/ChatWidget';
import { ColorSchemeSwitcher } from '../components/ColorSchemeSwitcher';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <>
      {children}
      <ChatWidget />
      <ColorSchemeSwitcher />
    </>
  );
}
