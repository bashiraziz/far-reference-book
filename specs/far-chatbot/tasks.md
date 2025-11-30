# FAR Reference Book - RAG Chatbot Tasks

## Task Overview

**Feature**: FAR RAG Chatbot
**Version**: 1.0.0
**Status**: In Progress
**Last Updated**: 2025-11-30

## Task Status Legend

- ✅ **Completed**: Task finished and tested
- 🔄 **In Progress**: Currently being worked on
- ⏸️ **Blocked**: Waiting on dependency
- 📋 **Pending**: Not yet started
- ❌ **Cancelled**: No longer needed

---

## Phase 1: Foundation & Data Preparation

### Task 1.1: FAR Content Conversion ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 4 hours

**Description**: Convert FAR Parts 1-25 from DITA XML to Markdown

**Acceptance Criteria**:
- [x] DITA to Markdown converter script created
- [x] All 1,245 FAR sections converted
- [x] Markdown files have proper frontmatter (id, title, sidebar_label)
- [x] Files organized in `docs/part-{X}/` directories
- [x] Docusaurus can build without errors

**Test Cases**:
```
TC-1.1.1: Verify converted markdown syntax is valid
TC-1.1.2: Verify frontmatter matches section numbers
TC-1.1.3: Verify cross-references are preserved
TC-1.1.4: Run `npm run build` - should succeed
```

---

### Task 1.2: Vector Database Population 🔄
**Status**: 🔄 In Progress
**Owner**: Development Team
**Effort**: 30-45 minutes (automated)

**Description**: Populate Qdrant with FAR Parts 4-25 embeddings

**Acceptance Criteria**:
- [x] Part 4 chunks uploaded
- [ ] Parts 5-25 chunks uploaded
- [ ] All chunks have proper metadata
- [ ] Zero upload failures
- [ ] Verify total chunk count

**Test Cases**:
```
TC-1.2.1: Count chunks in Qdrant - should be 10,000-15,000
TC-1.2.2: Sample search for "cost principles" - returns relevant results
TC-1.2.3: Verify metadata fields (chapter, section, chunk_index)
TC-1.2.4: Check storage usage < 1GB
```

**Progress**:
- ✅ Part 4: Complete (14,850+ chunks)
- 🔄 Parts 5-25: In progress

---

### Task 1.3: Database Schema Setup ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 1 hour

**Description**: Create PostgreSQL tables for conversations and messages

**Acceptance Criteria**:
- [x] `conversations` table created
- [x] `messages` table created
- [x] Foreign key relationships established
- [x] Indexes added for performance
- [x] Migration script tested

**Test Cases**:
```
TC-1.3.1: Insert conversation - succeeds
TC-1.3.2: Insert message with FK - succeeds
TC-1.3.3: Query messages by conversation_id - returns correct results
TC-1.3.4: Test cascade delete (optional)
```

---

## Phase 2: Backend API Development

### Task 2.1: Health Check Endpoint ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 30 minutes

**Description**: Implement `/health` endpoint for monitoring

**Acceptance Criteria**:
- [x] GET /health returns 200
- [x] Response includes status: "healthy"
- [x] No authentication required
- [x] Logged in backend

**Test Cases**:
```
TC-2.1.1: curl https://backend/health - returns {"status":"healthy"}
TC-2.1.2: Verify response time < 100ms
TC-2.1.3: Works when other endpoints are down (graceful degradation)
```

---

### Task 2.2: Conversation Management Endpoints ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Implement conversation CRUD endpoints

**Endpoints**:
- POST /conversations
- GET /conversations/{id}
- GET /conversations/{id}/messages

**Acceptance Criteria**:
- [x] Create conversation - returns UUID
- [x] Get conversation - returns metadata
- [x] Get messages - returns array of messages
- [x] Proper error handling (404 for missing IDs)
- [x] Input validation with Pydantic

**Test Cases**:
```
TC-2.2.1: POST /conversations - returns conversation with UUID
TC-2.2.2: GET /conversations/{id} - returns same conversation
TC-2.2.3: GET /conversations/{id}/messages - returns empty array initially
TC-2.2.4: GET /conversations/invalid-uuid - returns 404
```

---

### Task 2.3: RAG Service Implementation ✅
**Status**: ✅ Completed (Needs CORS fix)
**Owner**: Development Team
**Effort**: 4 hours

**Description**: Implement core RAG pipeline

**Components**:
1. Embeddings Service (OpenAI)
2. Vector Store Service (Qdrant)
3. RAG Service (orchestration)
4. Database Service (persistence)

**Acceptance Criteria**:
- [x] Generate embeddings for user questions
- [x] Search Qdrant for top 5 relevant chunks
- [x] Build prompt with context
- [x] Call OpenAI for answer generation
- [x] Parse and format sources
- [x] Save messages to database

**Test Cases**:
```
TC-2.3.1: Question about Part 3 - returns relevant answer
TC-2.3.2: Verify 5 sources returned
TC-2.3.3: Sources have required fields (chapter, section, excerpt)
TC-2.3.4: Response time < 2 seconds (p95)
TC-2.3.5: Invalid question - handles gracefully
```

---

### Task 2.4: Chat Endpoint ✅
**Status**: ✅ Completed (Needs CORS fix)
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Implement POST /chat/{id}/messages/simple endpoint

**Acceptance Criteria**:
- [x] Accepts conversation_id, content, optional selected_text
- [x] Returns user_message and assistant_message
- [x] Sources included in assistant_message
- [x] Conversation history persisted
- [x] Error handling for all failure modes

**Test Cases**:
```
TC-2.4.1: Send message - get response with sources
TC-2.4.2: Send message with selected_text - context prioritized
TC-2.4.3: Multiple messages in same conversation - history maintained
TC-2.4.4: Empty content - returns 400 error
TC-2.4.5: Content > 500 chars - returns 400 error
```

---

### Task 2.5: CORS Configuration 🔄
**Status**: 🔄 In Progress (Testing needed)
**Owner**: Development Team
**Effort**: 1 hour

**Description**: Fix CORS to allow GitHub Pages origin

**Acceptance Criteria**:
- [x] CORS_ORIGINS env var reads comma-separated string
- [x] Settings parse to list of origins
- [x] Middleware configured with parsed list
- [ ] Tested from production GitHub Pages
- [ ] OPTIONS requests handled correctly

**Test Cases**:
```
TC-2.5.1: Fetch from https://bashiraziz.github.io - succeeds
TC-2.5.2: Fetch from unauthorized origin - fails with CORS error
TC-2.5.3: OPTIONS preflight - returns correct headers
TC-2.5.4: Multiple origins in env var - all work
```

**Current Issue**: CORS_ORIGINS in Railway was set as JSON array instead of comma-separated string

**Fix Applied**:
```
Before: ["https://bashiraziz.github.io"]
After:  https://bashiraziz.github.io,http://localhost:3000
```

---

## Phase 3: Frontend Development

### Task 3.1: Chat API Client ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Create TypeScript API client for chatbot

**File**: `src/services/chatApi.ts`

**Acceptance Criteria**:
- [x] TypeScript interfaces defined
- [x] API_BASE_URL configurable
- [x] Methods: createConversation, getMessages, sendMessage
- [x] Error handling with try/catch
- [x] Type-safe responses

**Test Cases**:
```
TC-3.1.1: createConversation() - returns Conversation object
TC-3.1.2: sendMessage() - returns ChatResponse with sources
TC-3.1.3: Network error - throws descriptive error
TC-3.1.4: 404 response - throws with detail message
```

---

### Task 3.2: Basic Chat Interface ✅
**Status**: ✅ Completed (Needs testing with CORS fix)
**Owner**: Development Team
**Effort**: 4 hours

**Description**: Create React component for chat UI

**Components**:
- ChatInterface (main container)
- MessageList (displays messages)
- InputBox (user input)
- SourceCard (source citations)

**Acceptance Criteria**:
- [x] Users can type and send messages
- [x] Messages display in conversation view
- [x] Sources display with each assistant message
- [x] Loading state while processing
- [x] Error messages for failures
- [x] Mobile responsive

**Test Cases**:
```
TC-3.2.1: Type message, click send - appears in chat
TC-3.2.2: Receive response - displays with sources
TC-3.2.3: Click source - navigates to FAR section
TC-3.2.4: Network error - shows error message
TC-3.2.5: Resize to mobile - UI adapts correctly
```

---

### Task 3.3: OpenAI ChatKit Integration 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 4-6 hours

**Description**: Replace basic chat UI with OpenAI ChatKit

**Subtasks**:
1. Install ChatKit SDK: `npm install @openai/chatkit-js`
2. Configure domain allowlist in OpenAI dashboard
3. Generate client token
4. Create ChatKit component wrapper
5. Style to match Docusaurus theme
6. Connect to existing backend API

**Acceptance Criteria**:
- [ ] ChatKit SDK installed
- [ ] Domain allowlist configured
- [ ] Chat interface renders
- [ ] Messages send/receive through existing API
- [ ] Custom styling applied
- [ ] Works on mobile

**Test Cases**:
```
TC-3.3.1: ChatKit component renders without errors
TC-3.3.2: Send message through ChatKit - backend receives it
TC-3.3.3: Receive response - ChatKit displays it
TC-3.3.4: Custom theme applied - matches Docusaurus colors
TC-3.3.5: Domain allowlist - only works from approved domains
```

**Reference**: [ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)

---

### Task 3.4: Selected Text Feature 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 3 hours

**Description**: Allow users to select text on FAR pages and ask questions

**Implementation**:
1. Detect text selection with `window.getSelection()`
2. Show "Ask about this" button near selection
3. Populate chat with selected text as context
4. Send `selected_text` field to backend

**Acceptance Criteria**:
- [ ] User selects text - button appears
- [ ] Click button - opens chat with context
- [ ] Send question - backend receives selected_text
- [ ] Answer prioritizes selected section

**Test Cases**:
```
TC-3.4.1: Select text - "Ask about this" button appears
TC-3.4.2: Click button - chat opens with text shown
TC-3.4.3: Ask question - answer relates to selection
TC-3.4.4: Deselect text - button disappears
TC-3.4.5: Select from multiple paragraphs - all captured
```

---

### Task 3.5: Responsive Design 📋
**Status**: 📋 Pending (Depends on ChatKit integration)
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Ensure chat works well on all devices

**Breakpoints**:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Acceptance Criteria**:
- [ ] Mobile: Chat takes full screen when opened
- [ ] Tablet: Chat in sidebar (40% width)
- [ ] Desktop: Chat in fixed bottom-right corner
- [ ] Touch-friendly tap targets (min 44px)
- [ ] Keyboard navigation works

**Test Cases**:
```
TC-3.5.1: Open chat on iPhone - full screen, usable
TC-3.5.2: Open chat on iPad - sidebar view
TC-3.5.3: Open chat on desktop - bottom-right corner
TC-3.5.4: Keyboard navigation - can tab through elements
TC-3.5.5: Screen reader - announces messages correctly
```

---

## Phase 4: Deployment & Testing

### Task 4.1: Frontend Deployment ✅
**Status**: ✅ Completed
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Deploy Docusaurus site to GitHub Pages

**Acceptance Criteria**:
- [x] GitHub Actions workflow configured
- [x] Builds on push to main branch
- [x] Deploys to `bashiraziz.github.io/far-reference-book/`
- [x] All FAR parts accessible
- [x] No broken links

**Test Cases**:
```
TC-4.1.1: Visit site - loads without errors
TC-4.1.2: Navigate to Part 4 - pages render correctly
TC-4.1.3: Check browser console - no errors
TC-4.1.4: Test on mobile - responsive design works
```

---

### Task 4.2: Backend Deployment ✅
**Status**: ✅ Completed (Monitoring needed)
**Owner**: Development Team
**Effort**: 3 hours

**Description**: Deploy FastAPI backend to Railway

**Acceptance Criteria**:
- [x] nixpacks.toml configured
- [x] requirements.txt complete
- [x] Environment variables set in Railway
- [x] PostgreSQL linked
- [x] Public domain generated
- [x] Health check returns 200

**Test Cases**:
```
TC-4.2.1: curl https://far-reference-book-production.up.railway.app/health - 200
TC-4.2.2: Check Railway logs - no errors
TC-4.2.3: POST /conversations - works
TC-4.2.4: CORS from GitHub Pages - allowed
```

**Domain**: `far-reference-book-production.up.railway.app`

---

### Task 4.3: End-to-End Testing 📋
**Status**: 📋 Pending (Blocked by CORS fix)
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Test complete user flows in production

**Test Scenarios**:
1. First-time user flow
2. Multi-turn conversation
3. Selected text query
4. Error handling
5. Mobile usage

**Acceptance Criteria**:
- [ ] All user stories from spec.md work
- [ ] No console errors
- [ ] Sources clickable and correct
- [ ] Response times acceptable
- [ ] Errors handled gracefully

**Test Cases**:
```
TC-4.3.1: Ask "What is FAR Part 4?" - get answer with sources
TC-4.3.2: Follow-up question - maintains context
TC-4.3.3: Select text, ask question - contextual answer
TC-4.3.4: Disconnect internet - error message shown
TC-4.3.5: Use on mobile - all features work
```

---

### Task 4.4: Performance Optimization 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 3 hours

**Description**: Ensure performance targets are met

**Targets**:
- Page load: < 3 seconds
- Chat response: < 2 seconds (p95)
- Vector search: < 500ms
- Embedding generation: < 1 second

**Optimizations**:
- [ ] Enable Docusaurus production build optimizations
- [ ] Minimize bundle size (code splitting)
- [ ] Optimize images
- [ ] Add loading states
- [ ] Implement request debouncing

**Test Cases**:
```
TC-4.4.1: Measure page load with Lighthouse - score > 90
TC-4.4.2: Measure chat response time - p95 < 2s
TC-4.4.3: Check bundle size - < 500KB
TC-4.4.4: Test with slow 3G - still usable
```

---

## Phase 5: Documentation & Polish

### Task 5.1: User Documentation 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Write user-facing documentation

**Documents**:
1. Chat usage guide
2. FAQ
3. Limitations/disclaimers
4. Contact/feedback

**Acceptance Criteria**:
- [ ] "How to use the chatbot" page created
- [ ] FAQ with common questions
- [ ] Clear disclaimer about AI-generated content
- [ ] Link to report issues

**Location**: `docs/chatbot-guide.md`

---

### Task 5.2: API Documentation 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 1 hour

**Description**: Auto-generate API docs with FastAPI

**Acceptance Criteria**:
- [ ] OpenAPI schema available at /docs
- [ ] All endpoints documented
- [ ] Request/response schemas shown
- [ ] Example requests provided

**Test Cases**:
```
TC-5.2.1: Visit /docs - Swagger UI loads
TC-5.2.2: Try endpoint from Swagger - works
TC-5.2.3: Schemas match actual API behavior
```

---

### Task 5.3: Code Cleanup 📋
**Status**: 📋 Pending
**Owner**: Development Team
**Effort**: 2 hours

**Description**: Clean up code for production readiness

**Checklist**:
- [ ] Remove console.logs from frontend
- [ ] Remove commented-out code
- [ ] Add JSDoc comments to complex functions
- [ ] Format code with prettier/black
- [ ] Fix linter warnings

**Acceptance Criteria**:
- [ ] No console.logs in production build
- [ ] ESLint/Pylint pass with no warnings
- [ ] Code formatted consistently
- [ ] Complex functions have comments

---

## Bonus Features (Optional)

### Bonus Task 1: Better-Auth Integration 📋
**Status**: 📋 Pending
**Points**: Up to 50 bonus points

**Description**: Add user authentication with better-auth.com

**Features**:
- Sign up / Sign in
- User profile
- Background questionnaire (software/hardware experience)
- Persist user preferences

**Effort**: 8-10 hours

---

### Bonus Task 2: Content Personalization 📋
**Status**: 📋 Pending
**Points**: Up to 50 bonus points

**Description**: Personalize content based on user background

**Features**:
- "Personalize" button at start of each chapter
- Adjust explanation depth based on user background
- Highlight relevant sections for user's role

**Effort**: 6-8 hours

---

### Bonus Task 3: Urdu Translation 📋
**Status**: 📋 Pending
**Points**: Up to 50 bonus points

**Description**: Translate content to Urdu on demand

**Features**:
- "Translate to Urdu" button per chapter
- Use OpenAI or Google Translate API
- Cache translations

**Effort**: 4-6 hours

---

### Bonus Task 4: Reusable Subagents/Skills 📋
**Status**: 📋 Pending
**Points**: Up to 50 bonus points

**Description**: Create Claude Code subagents for reusable intelligence

**Examples**:
- FAR content updater agent
- Citation validator agent
- Documentation generator agent

**Effort**: 10-12 hours

---

## Task Dependencies

```
Phase 1 (Foundation)
  └─> Phase 2 (Backend API)
       ├─> Phase 3 (Frontend)
       │     └─> Phase 4 (Deployment)
       │           └─> Phase 5 (Documentation)
       │
       └─> Bonus Features (Optional, parallel)
```

**Critical Path**: 1.2 → 2.5 → 4.3

---

## Summary

**Total Tasks**: 21 core tasks + 4 bonus features
**Completed**: 11 ✅
**In Progress**: 2 🔄
**Pending**: 8 📋
**Blocked**: 0 ⏸️

**Estimated Remaining Effort**: 20-25 hours

**Next Priority Tasks**:
1. 🔄 Complete vector database population (Task 1.2)
2. ✅ Fix and test CORS configuration (Task 2.5)
3. 🚀 Integrate OpenAI ChatKit (Task 3.3)
4. ✅ End-to-end testing (Task 4.3)

**Current Blockers**:
- Task 4.3 blocked by Task 2.5 (CORS testing)

---

## Version History

- **v1.0.0** (2025-11-30): Initial tasks breakdown
