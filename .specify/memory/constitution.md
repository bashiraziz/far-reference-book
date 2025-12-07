# FAR Reference Book Constitution

## Core Principles

### I. Project Requirements

This is a unified book project using Claude Code and Spec-Kit Plus. The core deliverables are:

1. **AI/Spec-Driven Book Creation**: Write a book using Docusaurus and deploy it to GitHub Pages. Using Spec-Kit Plus (https://github.com/panaversity/spec-kit-plus/) and Claude Code (https://www.claude.com/product/claude-code) to create the Federal Acquisition Regulation (FAR) reference book.

2. **Integrated RAG Chatbot Development**: Build and embed a Retrieval-Augmented Generation (RAG) chatbot within the published book. This chatbot, utilizing the OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres database, and Qdrant Cloud Free Tier, must be able to answer user questions about the book's content, including answering questions based only on text selected by the user.

3. **Base Functionality**: Core implementation worth 100 points for complete functionality.

4. **Bonus Features Available**:
   - Up to 50 bonus points for creating and using reusable intelligence via Claude Code Subagents and Agent Skills
   - Up to 50 bonus points for implementing Signup/Signin using https://www.better-auth.com/ with user background questionnaire
   - Up to 50 bonus points for personalized content feature (per chapter button)
   - Up to 50 bonus points for Urdu translation feature (per chapter button)

### II. Technology Stack (NON-NEGOTIABLE)

**Frontend**:
- Docusaurus for static site generation
- React for interactive components
- Deployed to GitHub Pages
- OpenAI ChatKit for chat interface

**Backend**:
- FastAPI for REST API
- Python 3.11+
- Deployed to Railway (production)

**Databases**:
- Neon Serverless Postgres for conversation/user data
- Qdrant Cloud Free Tier for vector embeddings

**AI/ML**:
- OpenAI API for embeddings (text-embedding-3-small)
- OpenAI API for chat completions (GPT-4 or GPT-3.5-turbo)
- RAG architecture with vector search

### III. Code Quality Standards

**Python Backend**:
- Type hints required for all functions
- Pydantic models for data validation
- Async/await for I/O operations
- Proper error handling with custom exceptions
- Logging at appropriate levels (INFO, WARNING, ERROR)

**TypeScript/JavaScript Frontend**:
- TypeScript for type safety
- ESLint for code quality
- Proper error boundaries in React
- Accessible UI components

**Testing**:
- Unit tests for core business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows

### IV. Documentation Requirements

**Code Documentation**:
- Docstrings for all public functions/classes
- README.md in each major directory
- API documentation (OpenAPI/Swagger)

**User Documentation**:
- FAR content properly formatted in Markdown
- Chatbot usage instructions
- Contribution guidelines

**Spec-Driven Development**:
- Constitution defines project principles
- Spec documents define features
- Plan documents define architecture
- Tasks documents define implementation steps

### V. Data Management

**Content**:
- FAR Parts 1-53 in DITA XML format
- Converted to Markdown for Docusaurus
- Chunked and embedded for vector search

**Vector Database**:
- 800-character chunks with 150-character overlap
- Metadata: chapter, section, chunk_index, source_file
- Top-k retrieval (k=5) for relevant context

**Conversation Storage**:
- Conversations table with metadata
- Messages table with user/assistant roles
- Source attribution for RAG responses

### VI. Security & Privacy

**API Keys**:
- All secrets in environment variables
- Never commit .env files
- Use Railway/GitHub Secrets for production

**CORS**:
- Configured for GitHub Pages origin
- Comma-separated string format for multiple origins

**Data Privacy**:
- No personal data collected without consent
- User conversations stored securely
- Optional authentication for bonus features

### VII. Deployment Strategy

**CI/CD**:
- GitHub Actions for frontend deployment
- Automatic deployment to GitHub Pages on main branch push
- Railway automatic deployment on backend changes

**Environments**:
- Development: Local (localhost:3000 frontend, localhost:8080 backend)
- Production: GitHub Pages + Railway

**Monitoring**:
- Backend logs via Railway dashboard
- Frontend errors via browser console
- API response times tracked

## Architecture Standards

### RAG Pipeline

1. **User Query** → Frontend chat interface
2. **Query Processing** → Backend receives question
3. **Vector Search** → Qdrant retrieves top 5 relevant chunks
4. **Context Building** → Combine chunks with metadata
5. **LLM Generation** → OpenAI generates answer with sources
6. **Response Delivery** → Return answer + source citations
7. **If the "I do not answer" or "there is no relevant FAR content provided" message is returned, then the user should be prompted to select a text**
8. **If the quadrant does not have the relevent material to answer the question, then the Docuraurus should be used for reference and answer the question based on the selected text**
9. **Answer to the question should not come from beyond the Qdrant and Docusaurus**

### API Design

**RESTful Endpoints**:
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get conversation details
- `GET /conversations/{id}/messages` - Get message history
- `POST /chat/{id}/messages/simple` - Send message and get response
- `GET /health` - Health check endpoint

**Response Format**:
```json
{
  "user_message": {...},
  "assistant_message": {
    "content": "...",
    "sources": [...]
  }
}
```

### Frontend Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Docusaurus pages
├── services/       # API clients
└── styles/         # CSS modules
```

### Backend Structure

```
backend/
├── api/            # FastAPI routes
├── config/         # Settings and logging
├── models/         # Pydantic models
├── services/       # Business logic
└── scripts/        # Data processing scripts
```

## Development Workflow

### Feature Development

1. **Spec Creation**: Document requirements in `specs/{feature}/spec.md`
2. **Planning**: Architecture decisions in `specs/{feature}/plan.md`
3. **Task Breakdown**: Implementation steps in `specs/{feature}/tasks.md`
4. **Implementation**: Code with tests
5. **Review**: Code review and testing
6. **Deploy**: Merge to main, auto-deploy

### Git Workflow

**Branches**:
- `main` - Production-ready code
- Feature branches for new development

**Commit Messages**:
- Clear, descriptive messages
- Reference issue numbers when applicable
- Co-authored with Claude when using AI assistance

**Pull Requests**:
- Required for merging to main
- Include description of changes
- Link to related spec/plan documents

## Quality Gates

### Before Deployment

✅ All tests passing
✅ No console errors in frontend
✅ Backend health check returns 200
✅ CORS configured correctly
✅ Environment variables set
✅ Documentation updated

### Performance Targets

- **Page Load**: < 3 seconds
- **API Response**: < 2 seconds for chat queries
- **Vector Search**: < 500ms
- **Embedding Generation**: < 1 second per batch

## Governance

**Constitution Authority**:
- This constitution supersedes all other practices
- Amendments require documentation and justification
- Version controlled in git

**Compliance**:
- All PRs must comply with constitution principles
- Code reviews verify adherence
- Complexity must be justified with ADRs

**Evolution**:
- Constitution evolves with project needs
- Changes documented with rationale
- Breaking changes require migration plan

---

**Version**: 1.0.0
**Ratified**: 2025-11-30
**Last Amended**: 2025-12-05
**Project**: FAR Reference Book
**Technology**: Claude Code + Spec-Kit Plus + Docusaurus + FastAPI + OpenAI, Qdrant, Neon, GitHub Pages, Railway, OpenAI ChatKit, Better Auth