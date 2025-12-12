# FAR Chatbot Testing Guide

Complete testing plan for the FAR Reference Book chatbot with RAG capabilities.

---

## Quick Test (5 minutes)

### Basic Chatbot Test
1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. Open frontend (choose one):
   - **Docusaurus with chatbot:** `npm run start` (http://localhost:3000)
   - **Standalone chatbot:** Open `index.html` in browser

3. Test these 3 queries:
   - "What is FAR?"
   - "What are the sealed bidding procedures?"
   - "Explain cost accounting standards"

**Expected:** Chatbot responds with relevant FAR content and citations.

---

## Comprehensive Test Suite (30 minutes)

### Test Categories

#### 1. Basic Retrieval Tests
Test if chatbot can find specific FAR sections.

**Test Queries:**
```
1. "What does FAR Part 1 cover?"
2. "What is the simplified acquisition threshold?"
3. "Define commercial item"
4. "What are the requirements for cost accounting standards?"
5. "Explain sealed bidding procedures"
```

**Expected Results:**
- Relevant section content returned
- Proper citations (Part.Section format)
- Contextually accurate responses

---

#### 2. Multi-Section Tests
Test if chatbot can synthesize information from multiple sections.

**Test Queries:**
```
1. "What are the different types of contracts available?"
2. "Compare sealed bidding and negotiated procurement"
3. "What are the small business programs?"
4. "Explain contractor responsibility determination"
```

**Expected Results:**
- Information from multiple sections
- Coherent synthesis
- Multiple part citations

---

#### 3. Specific Section Tests
Test precise section retrieval.

**Test Queries:**
```
1. "What is FAR 52.219-9?"
2. "Show me FAR 15.404"
3. "What does section 31.205-6 say?"
4. "Explain FAR Part 12 Subpart 12.3"
```

**Expected Results:**
- Exact section content
- Accurate citations
- No hallucination

---

#### 4. Complex Questions
Test reasoning and understanding.

**Test Queries:**
```
1. "When should I use a fixed-price contract vs cost-reimbursement?"
2. "What are the labor law requirements for government contracts?"
3. "How do I determine if something qualifies as a commercial item?"
4. "What environmental regulations apply to federal acquisitions?"
```

**Expected Results:**
- Multi-part answers
- Logical flow
- Policy explanations with citations

---

#### 5. Edge Cases
Test system limits and handling of difficult queries.

**Test Queries:**
```
1. "What is Part 20?" (Reserved part - should handle gracefully)
2. "Tell me about FAR Part 100" (Doesn't exist)
3. "asdfghjkl" (Gibberish)
4. "What is the weather today?" (Out of scope)
```

**Expected Results:**
- Graceful handling of missing content
- "I don't have information about..." responses
- No crashes or errors

---

## Automated Testing Script

### Quick Automated Test

Run the test script:
```bash
cd backend
python scripts/test_chatbot_production.py
```

This will:
1. Connect to Qdrant
2. Test vector search
3. Run sample queries
4. Report results

---

## Manual Testing Checklist

### Pre-Test Setup
- [ ] Backend server running (port 8000)
- [ ] Frontend accessible (port 3000 or index.html)
- [ ] Qdrant collection has 17,746 points
- [ ] OpenAI API key configured

### Functionality Tests
- [ ] Chatbot widget appears on page
- [ ] Chat window opens/closes smoothly
- [ ] Messages send successfully
- [ ] Responses appear within 5 seconds
- [ ] Citations include Part.Section format
- [ ] Follow-up questions work
- [ ] Context maintained across messages

### Content Quality Tests
- [ ] Answers are accurate to FAR content
- [ ] No hallucinated information
- [ ] Citations are correct
- [ ] Multi-section queries synthesize well
- [ ] Technical terms explained correctly

### Error Handling Tests
- [ ] Invalid queries handled gracefully
- [ ] Network errors show user-friendly message
- [ ] Timeout handled appropriately
- [ ] Rate limits handled (if applicable)

### Performance Tests
- [ ] Response time < 5 seconds
- [ ] No lag in UI
- [ ] Handles rapid-fire queries
- [ ] Memory doesn't grow excessively

---

## Expected Performance Metrics

### Response Times
- **Simple queries:** 1-3 seconds
- **Complex queries:** 3-5 seconds
- **Multi-section:** 4-6 seconds

### Accuracy
- **Section retrieval:** 95%+ accuracy
- **Content relevance:** 90%+ relevant chunks
- **Citation accuracy:** 100% (should always cite correctly)

### Availability
- **Uptime:** 99%+ (dependent on backend/Qdrant)
- **Error rate:** < 1%

---

## Test Results Template

```markdown
## Test Session: [Date/Time]

### Environment
- Backend: Running / Not Running
- Frontend: Docusaurus / Standalone
- Qdrant Points: [count]

### Test Results

#### Basic Retrieval (Pass/Fail)
1. "What is FAR?" - [Result]
2. "Sealed bidding procedures" - [Result]
3. "Commercial item definition" - [Result]

#### Multi-Section (Pass/Fail)
1. "Types of contracts" - [Result]
2. "Small business programs" - [Result]

#### Specific Sections (Pass/Fail)
1. "FAR 52.219-9" - [Result]
2. "FAR 15.404" - [Result]

#### Edge Cases (Pass/Fail)
1. "Part 20" - [Result]
2. Gibberish query - [Result]

### Issues Found
- [List any problems]

### Performance
- Average response time: [X] seconds
- Slowest query: [query] - [X] seconds
- Fastest query: [query] - [X] seconds

### Overall Assessment
- Pass / Fail
- Notes: [observations]
```

---

## Common Issues & Solutions

### Issue: No Response from Chatbot
**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check Qdrant connection in logs
3. Verify OpenAI API key is valid

### Issue: Irrelevant Responses
**Solution:**
1. Check Qdrant has correct data: `python scripts/check_qdrant_collections.py`
2. Verify chunk size/overlap settings
3. Check embedding model is consistent

### Issue: Slow Responses
**Solution:**
1. Check Qdrant query performance
2. Verify network latency to OpenAI
3. Reduce number of chunks retrieved (MAX_CHUNK_RETRIEVAL)

### Issue: Citations Missing
**Solution:**
1. Check metadata in Qdrant points
2. Verify backend formatting in chat endpoint
3. Review prompt template

---

## Advanced Testing

### Load Testing
```bash
# Run 100 concurrent queries
cd backend
python scripts/load_test_chatbot.py --queries 100 --concurrent 10
```

### Quality Assurance
```bash
# Run QA suite with ground truth answers
cd backend
python scripts/qa_test_suite.py
```

### Vector Search Quality
```bash
# Test vector search accuracy
cd backend
python scripts/test_vector_search.py
```

---

## Success Criteria

The chatbot passes testing if:

1. ✅ All basic retrieval queries return relevant content
2. ✅ Citations are accurate and properly formatted
3. ✅ Response time < 5 seconds for 95% of queries
4. ✅ No crashes or errors during testing
5. ✅ Edge cases handled gracefully
6. ✅ Multi-section synthesis is coherent
7. ✅ Context maintained across conversation
8. ✅ No hallucinated information

---

## Next Steps After Testing

### If Tests Pass
1. Deploy to production
2. Monitor performance metrics
3. Collect user feedback
4. Iterate on improvements

### If Tests Fail
1. Document specific failures
2. Check logs for errors
3. Review Qdrant data quality
4. Adjust chunking/embedding strategy
5. Re-test after fixes

---

## Quick Reference Commands

```bash
# Start backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Start frontend
npm run start

# Check Qdrant status
cd backend && python scripts/check_qdrant_collections.py

# Run automated tests
cd backend && python scripts/test_chatbot_production.py

# View logs
tail -f backend/logs/app.log
```

---

## Contact & Support

- Documentation: `/docs`
- Issues: Create issue in GitHub
- Logs: `backend/logs/`
- Config: `backend/.env`
