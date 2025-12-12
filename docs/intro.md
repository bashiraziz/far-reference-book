---
id: intro
title: Federal Acquisition Regulation (FAR) Reference
sidebar_label: Introduction
slug: /
---

import { HeroSection } from '@site/src/components/HeroSection';

<HeroSection />

:::caution ⚠️ Important: This is NOT an Official FAR Website

**This is an independent, open-source educational resource** created to make FAR content more accessible. While we strive for accuracy, this site should not be used as a substitute for official FAR documentation.

**For official FAR information and regulatory guidance, always consult:** [acquisition.gov](https://www.acquisition.gov/browse/index/far)

Always verify information with official sources and qualified legal counsel for matters related to federal acquisition and contracting.

:::

Welcome to the FAR Reference Book - your comprehensive guide to all 53 Parts of the Federal Acquisition Regulations.

:::tip 💬 Try the AI-Powered FAR Assistant

**Have a question about federal acquisition regulations?** Our intelligent chatbot can instantly search through all 53 FAR Parts to provide answers with precise citations.

**Click the pulsing purple button in the bottom-right corner to start chatting!**

Example questions you can ask:
- "What are the general contracting requirements?"
- "Explain the policy on contract modifications"
- "What are the rules for small business set-asides?"

:::

## About the FAR

The Federal Acquisition Regulation (FAR) is the primary regulation for use by all federal executive agencies in their acquisition of supplies and services with appropriated funds. The FAR System consists of the FAR, which is the primary document, and agency acquisition regulations that implement or supplement the FAR.

## Available Parts

This reference book contains **all 53 FAR Parts**, providing complete coverage of federal acquisition regulations. Use the sidebar navigation to explore any part and its sections.

## How to Use This Reference

- **AI Assistant**: Click the pulsing button in the bottom-right to ask questions and get instant answers with citations
- **Browse by Part**: Use the sidebar navigation to explore specific parts and sections
- **Search**: Use the search bar (top right) to find specific regulations, keywords, or topics
- **Cross-References**: Click on section references (e.g., [1.301](./part-1/1.301.md)) to navigate between related sections

## Technology Stack

This application is built with modern, scalable technologies:

### Frontend
- **[Docusaurus](https://docusaurus.io/)** - Static site generator for documentation
- **React 19** - UI component library with TypeScript
- **MDX** - Enhanced markdown with React components

### Backend & AI
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python web framework
- **[Qdrant](https://qdrant.tech/)** - Vector database for semantic search and RAG (Retrieval-Augmented Generation)
- **[Neon](https://neon.tech/)** - Serverless PostgreSQL for conversation storage
- **[OpenAI](https://openai.com/)** - Embeddings and language model for intelligent responses

### Infrastructure
- **[Railway](https://railway.app/)** - Cloud hosting platform for backend API
- **GitHub Pages** - Static site hosting for documentation

The AI assistant uses RAG technology to search through vector embeddings of all 53 FAR parts, retrieving relevant context and generating accurate answers with precise citations.
