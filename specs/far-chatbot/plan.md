# FAR Reference Book - RAG Chatbot Implementation Plan

## Plan Overview

**Feature**: FAR RAG Chatbot
**Version**: 1.0.0
**Status**: In Progress
**Last Updated**: 2025-12-05

## Executive Summary

This plan outlines the architecture and implementation strategy for embedding an intelligent RAG chatbot into the FAR Reference Book. The chatbot will allow users to ask questions about Federal Acquisition Regulations and receive AI-generated answers with source citations.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Docusaurus (GitHub Pages)                                │  │
│  │  - FAR Content Pages                                      │  │
│  │  - OpenAI ChatKit Component                               │  │
│  └──────────────────┬───────────────────────────────────────┘  │
└─────────────────────┼──────────────────────────────────────────┘
                      │ HTTPS/REST API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Railway)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer                                                │  │
│  │  - /conversations, /messages, /chat, /health             │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Services Layer                                           │  │
│  │  - RAG Service: Query → Retrieve → Generate              │  │
│  │  - Database Service: Conversation persistence            │  │
│  │  - Vector Store Service: Semantic search                 │  │
│  │  - Embeddings Service: Text → Vector                     │  │
│  └──────┬──────────────┬───────────────┬────────────────────┘  │
└─────────┼──────────────┼───────────────┼─────────────────────────┘
          │              │               │
          ▼              ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │ OpenAI  │   │  Qdrant  │   │   Neon   │
    │   API   │   │  Cloud   │   │ Postgres │
    └─────────┘   └──────────┘   └──────────┘
  Embeddings +     Vector DB      Conversations
  Completions      (FAR chunks)   + Messages
```

### Component Breakdown

#### 1. Frontend (Docusaurus + ChatKit)

**Technology**:
- Docusaurus 3.x (Static Site Generator)
- React 18+
- OpenAI ChatKit SDK
- TypeScript

**Responsibilities**:
- Serve FAR content as markdown pages
- Embed ChatKit component
- Handle user interactions
- Display chat messages and sources
- Manage UI state

**Key Files**:
- `src/components/ChatInterface.tsx` - Chat UI wrapper
- `src/services/chatApi.ts` - API client
- `docusaurus.config.ts` - Site configuration

#### 2. Backend API (FastAPI)

**Technology**:
- FastAPI 0.115+
- Python 3.11+
- Pydantic for data validation
- Async/await for I/O

**Responsibilities**:
- Handle chat requests
- Orchestrate RAG pipeline
- Manage conversations
- Validate inputs
- Return structured responses

**Key Endpoints**:

```python
POST   /conversations              # Create conversation
GET    /conversations/{id}         # Get conversation
GET    /conversations/{id}/messages # Get message history
POST   /chat/{id}/messages/simple  # Send message, get response
GET    /health                     # Health check
```

#### 3. RAG Service

**Purpose**: Core business logic for question answering

**Flow**:
```
User Question
    ↓
1. Generate Query Embedding (OpenAI)
    ↓
2. Vector Search (Qdrant) - Top 5 chunks
    ↓
3. Build Context Prompt
    ↓
4. LLM Completion (OpenAI)
    ↓
5. Parse & Format Response
    ↓
Return: {answer, sources[]}
```

**Key Functions**:
- `answer_question(question, selected_text, conversation_id)`
- `_retrieve_context(query_embedding, top_k=5)`
- `_generate_answer(context, question)`
- `_format_sources(chunks)`

#### 4. Vector Store Service (Qdrant)

**Purpose**: Semantic search over FAR content

**Schema**:
```python
{
  "id": "uuid",
  "vector": [512 dimensions],  # text-embedding-3-small (reduced dimensions)
  "payload": {
    "text": "chunk content",
    "chapter": 4,
    "section": "4.1001",
    "chunk_index": 0,
    "source_file": "path/to/file.md"
  }
}
```

**Operations**:
- `create_collection()` - Initialize collection
- `upsert_points(points)` - Bulk upload
- `search(vector, limit, score_threshold)` - Semantic search

#### 5. Database Service (Neon Postgres)

**Purpose**: Persist conversation history

**Schema**:

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    source VARCHAR(255),
    metadata JSONB
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20),  -- 'user' or 'assistant'
    content TEXT,
    selected_text TEXT,
    sources JSONB,
    token_count INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Operations**:
- `create_conversation(source, metadata)`
- `save_message(conversation_id, role, content, sources)`
- `get_messages(conversation_id)`
- `get_conversation(id)`

#### 6. Embeddings Service

**Purpose**: Convert text to vectors

**Model**: OpenAI `text-embedding-3-small` (512 dimensions - optimized for storage)

**Functions**:
- `generate_embedding(text)` - Single text
- `generate_embeddings_batch(texts)` - Batch processing

**Optimization**:
- Batch requests for efficiency
- Reduced dimensions (512 instead of 1536) for storage efficiency
- Cache for repeated queries (future)
- Handle rate limits gracefully

## Data Flow

### Query Processing Flow

```
1. USER TYPES QUESTION
   ↓
2. Frontend sends: POST /chat/{id}/messages/simple
   {
     "content": "What is FAR Part 4?",
     "selected_text": null  # or highlighted text
   }
   ↓
3. Backend validates request
   ↓
4. Save user message to database
   ↓
5. Generate question embedding
   OpenAI API: embeddings.create(
     model="text-embedding-3-small",
     input="What is FAR Part 4?"
   )
   ↓
6. Search Qdrant for relevant chunks
   Qdrant.search(
     collection="far_content",
     query_vector=[...512 dims...],
     limit=5,
     score_threshold=0.5
   )
   ↓
7. Build prompt with context
   "You are an expert on FAR. Answer based on:
    Context 1: [chunk text]
    Context 2: [chunk text]
    ...
    Question: What is FAR Part 4?"
   ↓
8. Generate answer
   OpenAI API: chat.completions.create(
     model="gpt-4o-mini",
     messages=[...],
     max_tokens=1000
   )
   ↓
9. Extract sources from chunks
   sources = [{
     "chapter": 4,
     "section": "4.100",
     "excerpt": "...",
     "relevance_score": 0.92
   }]
   ↓
10. Save assistant message to database
   ↓
11. Return response
   {
     "user_message": {...},
     "assistant_message": {
       "content": "FAR Part 4 covers...",
       "sources": [...]
     }
   }
   ↓
12. Frontend displays answer + sources
```

## Key Architectural Decisions

### AD-001: Vector Database Choice - Qdrant

**Decision**: Use Qdrant Cloud for vector storage

**Rationale**:
- Free tier provides 1GB storage (sufficient for FAR content)
- Excellent Python SDK
- Fast similarity search (<500ms)
- Cloud-hosted (no infrastructure management)

**Alternatives Considered**:
- Pinecone: More expensive, less generous free tier
- Weaviate: More complex setup
- PostgreSQL + pgvector: Requires managing Postgres extension

**Trade-offs**:
- ✅ Easy setup and deployment
- ✅ Good performance
- ❌ Storage limit (1GB)
- ❌ Vendor lock-in

### AD-002: Embedding Model - text-embedding-3-small (512 dimensions)

**Decision**: Use OpenAI's text-embedding-3-small model with reduced dimensions (512 instead of 1536)

**Rationale**:
- 512 dimensions significantly reduces storage (3x smaller)
- Still maintains good retrieval quality
- Faster than larger models
- Lower cost
- Fits within Qdrant 1GB free tier for all FAR content

**Alternatives Considered**:
- text-embedding-3-large: Higher quality but slower, more expensive
- text-embedding-ada-002: Older model, similar performance
- Full 1536 dimensions: Better quality but exceeds storage limits

**Trade-offs**:
- ✅ Fast embedding generation
- ✅ Lower API costs
- ✅ Much smaller storage footprint (~512MB for all FAR)
- ✅ Fits within free tier limits
- ❌ Slightly lower quality than full 1536 dimensions
- ❌ Slightly lower quality than large model

### AD-003: Chunking Strategy - 600 chars with 150 overlap

**Decision**: Chunk documents into 600-character segments with 150-character overlap

**Rationale**:
- Balances context preservation and granularity
- Smaller chunks = better retrieval precision
- Fits within OpenAI context window comfortably
- Overlap ensures sentences aren't split awkwardly
- Optimized for storage efficiency within 1GB limit

**Alternatives Considered**:
- 800-1000 chars: Too large, loses precision
- 400 chars: Too small, loses context
- Sentence-based: Inconsistent chunk sizes

**Trade-offs**:
- ✅ Better retrieval precision
- ✅ Optimized storage usage
- ✅ Preserves context across chunks
- ✅ More granular search results
- ❌ Some redundancy from overlap
- ❌ More chunks to process

### AD-004: LLM Model - GPT-4o-mini

**Decision**: Use GPT-4o-mini for answer generation

**Rationale**:
- Fast response times (1-2 seconds)
- Lower cost than GPT-4
- Better quality than GPT-3.5-turbo
- Improved instruction following
- Cost-effective for production use

**Alternatives Considered**:
- GPT-3.5-turbo: Cheaper but lower quality
- GPT-4: Higher quality but slower and more expensive
- Open-source models: Hosting complexity, lower quality

**Trade-offs**:
- ✅ Fast responses
- ✅ Lower costs than full GPT-4
- ✅ Better quality than GPT-3.5-turbo
- ✅ Good instruction following
- ❌ Slightly less accurate than GPT-4 full version

### AD-005: Frontend Framework - OpenAI ChatKit + Docusaurus

**Decision**: Integrate OpenAI ChatKit into existing Docusaurus site

**Rationale**:
- ChatKit provides polished UI out of the box
- Docusaurus is static and GitHub Pages compatible
- React-based (both use React)
- Easy integration

**Alternatives Considered**:
- Custom React chat UI: More work, less polished
- Next.js: Requires server for SSR, incompatible with GitHub Pages
- Streamlit: Python-only, not suitable for production docs site

**Trade-offs**:
- ✅ Professional UI instantly
- ✅ Maintained by OpenAI
- ✅ Works with static hosting
- ❌ Less customization flexibility
- ❌ Dependency on OpenAI's SDK

### AD-006: Deployment - GitHub Pages + Railway

**Decision**: Deploy frontend to GitHub Pages, backend to Railway

**Rationale**:
- GitHub Pages: Free, automatic deployment, good for static sites
- Railway: Easy Python deployment, free tier, PostgreSQL included
- Both meet project requirements
- Simple CI/CD with GitHub Actions

**Alternatives Considered**:
- Vercel: Better for Next.js, overkill for Docusaurus
- Heroku: Less generous free tier
- AWS/GCP: Too complex for this project

**Trade-offs**:
- ✅ Zero cost (within free tiers)
- ✅ Automatic deployments
- ✅ Easy to set up
- ❌ Free tier limitations
- ❌ Cold starts on Railway

## Interfaces and Contracts

### API Contract

**POST /chat/{conversation_id}/messages/simple**

Request:
```typescript
{
  content: string;        // User's question (max 500 chars)
  selected_text?: string; // Optional highlighted text (max 2000 chars)
}
```

Response:
```typescript
{
  user_message: {
    id: string;
    conversation_id: string;
    role: "user";
    content: string;
    selected_text: string | null;
    created_at: string;
  };
  assistant_message: {
    id: string;
    conversation_id: string;
    role: "assistant";
    content: string;
    sources: Array<{
      chunk_id: string;
      chapter: number;
      section: string;
      page?: number;
      relevance_score: number;
      excerpt: string;  // First 200 chars
    }>;
    token_count: number;
    processing_time_ms: number;
    created_at: string;
  };
}
```

Error Response:
```typescript
{
  detail: string;  // Error message
}
```

Status Codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Conversation not found
- 500: Internal Server Error

### Environment Variables

**Backend (.env)**:
```bash
# Required
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...qdrant.cloud
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=far_content
DATABASE_URL=postgresql://...neon.tech/...
CORS_ORIGINS=https://bashiraziz.github.io,http://localhost:3000

# Optional
LOG_LEVEL=INFO
API_TITLE=FAR Reference Book API
API_VERSION=1.0.0
```

**Frontend (docusaurus.config.ts)**:
```typescript
customFields: {
  backendUrl: process.env.BACKEND_URL || 'https://far-reference-book-production.up.railway.app'
}
```

## Non-Functional Requirements Implementation

### Performance

**Target**: < 2 seconds end-to-end response time

**Strategy**:
1. **Parallel Processing**: Run embedding generation and database save concurrently
2. **Batch Embeddings**: Process multiple chunks at once during population
3. **Index Optimization**: Qdrant HNSW index for fast vector search
4. **Streaming**: Stream LLM responses (future enhancement)

**Monitoring**:
- Track `processing_time_ms` for each message
- Log slow queries (>2s)
- Alert if p95 exceeds 3 seconds

### Reliability

**Target**: 99% uptime, <1% error rate

**Strategy**:
1. **Retry Logic**: Retry OpenAI API calls on transient failures (max 3 attempts)
2. **Circuit Breaker**: Stop calling failed services temporarily
3. **Graceful Degradation**: Show friendly error messages, don't crash
4. **Health Checks**: `/health` endpoint for monitoring

**Error Handling**:
```python
try:
    # API call
except OpenAIRateLimitError:
    # Queue request, inform user
except OpenAIAPIError as e:
    # Log error, return friendly message
    logger.error(f"OpenAI API error: {e}")
    raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
```

### Security

**CORS**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Only GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Input Validation**:
```python
class SendMessageRequest(BaseModel):
    content: str = Field(..., max_length=500)
    selected_text: Optional[str] = Field(None, max_length=2000)
```

**SQL Injection Prevention**:
- Use parameterized queries via asyncpg
- Never concatenate user input into SQL

**XSS Prevention**:
- Sanitize all user input
- React escapes by default
- Don't use `dangerouslySetInnerHTML`

### Scalability

**Current Limits**:
- Qdrant: 1GB storage (~50K-100K chunks)
- Neon: 10GB storage, 100 hours compute
- OpenAI: Rate limits depend on tier

**Future Scaling**:
1. **Caching**: Cache common questions to reduce API calls
2. **CDN**: Use CloudFlare for static assets
3. **Upgrade Tiers**: Move to paid plans if needed
4. **Horizontal Scaling**: Railway supports multiple instances

## Testing Strategy

### Unit Tests

**Backend**:
- `test_embeddings_service.py` - Embedding generation
- `test_vector_store.py` - Qdrant operations
- `test_rag_service.py` - RAG pipeline logic
- `test_database.py` - Database operations

**Frontend**:
- `ChatInterface.test.tsx` - Component rendering
- `chatApi.test.ts` - API client

### Integration Tests

- Test full API endpoints
- Test RAG pipeline end-to-end
- Test database persistence
- Test CORS configuration

### E2E Tests (Manual)

- Ask question → Verify answer + sources
- Select text → Ask question → Verify context used
- Multiple messages → Verify conversation persists
- Error scenarios → Verify graceful handling

## Deployment Strategy

### Frontend Deployment (GitHub Pages)

**Trigger**: Push to `main` branch

**Process**:
1. GitHub Actions workflow triggers
2. Install dependencies (`npm ci`)
3. Build Docusaurus (`npm run build`)
4. Upload to GitHub Pages
5. Available at `https://bashiraziz.github.io/far-reference-book/`

**Config** (`.github/workflows/deploy.yml`):
```yaml
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./build
```

### Backend Deployment (Railway)

**Trigger**: Push to `main` branch (auto-deploy enabled)

**Process**:
1. Railway detects commit
2. Builds Docker container (Nixpacks)
3. Installs dependencies (`pip install -r requirements.txt`)
4. Starts server (`uvicorn api.main:app`)
5. Available at `https://far-reference-book-production.up.railway.app`

**Config** (`nixpacks.toml`):
```toml
[phases.setup]
nixPkgs = ["python311", "python311Packages.pip"]

[phases.install]
cmds = ["cd backend && pip install -r requirements.txt"]

[start]
cmd = "cd backend && python3.11 -m uvicorn api.main:app --host 0.0.0.0 --port $PORT"
```

## Monitoring and Observability

### Logging

**Backend**:
- Structured logging via Python `logging` module
- Log levels: INFO (normal), WARNING (degraded), ERROR (failures)
- Include: timestamp, level, logger name, message
- Track: request IDs, processing times, error details

**Example**:
```python
logger.info(f"Processing question: {question[:50]}...")
logger.warning(f"Vector search returned only {len(chunks)} chunks")
logger.error(f"OpenAI API call failed: {e}")
```

### Metrics to Track

1. **Response Time**: p50, p95, p99 latencies
2. **Error Rate**: % of 5xx responses
3. **API Usage**: OpenAI tokens consumed
4. **Vector Search**: Average relevance scores
5. **Conversation Length**: Messages per conversation

### Alerts (Future)

- Error rate > 5%
- p95 latency > 5 seconds
- OpenAI quota > 80%
- Qdrant storage > 800MB

## Risks and Mitigations

See [spec.md](./spec.md) for detailed risk analysis.

## Next Steps

1. ✅ **Complete Vector Database Population** (In Progress)
2. **Fix CORS Issues** (verify in production)
3. **Integrate OpenAI ChatKit**
   - Install SDK
   - Create ChatKit component
   - Style to match theme
4. **End-to-End Testing**
   - Test all user stories
   - Verify source citations
   - Check mobile responsiveness
5. **Documentation**
   - User guide
   - API documentation
   - Deployment instructions
6. **Bonus Features** (Optional)
   - Better-auth.com integration
   - Content personalization
   - Urdu translation

## Appendix

### Technology Versions

- Python: 3.11+
- FastAPI: 0.115.5
- OpenAI SDK: 1.55.3
- Qdrant Client: 1.12.1
- Node.js: 20.x
- React: 18.x
- Docusaurus: 3.x

### Reference Links

- [OpenAI ChatKit](https://platform.openai.com/docs/guides/chatkit)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Railway Docs](https://docs.railway.app/)
- [Neon Docs](https://neon.tech/docs)
