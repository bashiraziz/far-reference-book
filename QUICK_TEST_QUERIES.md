# Quick Test Queries for FAR Chatbot

Copy and paste these queries into your chatbot to test different capabilities.

---

## ✅ Basic FAR Questions (Expected: Quick, accurate responses)

```
What is FAR?
```

```
What does FAR stand for?
```

```
What is the purpose of the Federal Acquisition Regulation?
```

---

## 📋 Specific Section Queries (Expected: Exact section content)

```
What is FAR 52.219-9?
```

```
Explain FAR 15.404
```

```
What does section 31.205-6 cover?
```

```
Show me FAR Part 12 Subpart 12.3
```

---

## 🔍 Definition Queries (Expected: Clear definitions with context)

```
Define commercial item
```

```
What is a commercial service?
```

```
What is the simplified acquisition threshold?
```

```
Define cost accounting standards
```

```
What is a fixed-price contract?
```

---

## 📊 Comparison Queries (Expected: Multi-section synthesis)

```
What are the different types of contracts available?
```

```
Compare sealed bidding and negotiated procurement
```

```
What's the difference between fixed-price and cost-reimbursement contracts?
```

```
Compare commercial item acquisition vs traditional acquisition
```

---

## 🎯 Procedural Queries (Expected: Step-by-step guidance)

```
What are sealed bidding procedures?
```

```
How do I determine if something qualifies as a commercial item?
```

```
What are the requirements for using simplified acquisition procedures?
```

```
What is the process for contractor responsibility determination?
```

---

## 💼 Policy Queries (Expected: Comprehensive policy explanations)

```
What are the small business programs?
```

```
What labor laws apply to government contracts?
```

```
What environmental regulations apply to federal acquisitions?
```

```
What are the socioeconomic programs in FAR?
```

---

## 🔢 Complex Analysis Queries (Expected: Multi-part detailed answers)

```
When should I use a fixed-price contract vs cost-reimbursement?
```

```
What factors determine contractor responsibility?
```

```
How does the government evaluate price reasonableness?
```

```
What are the requirements for cost accounting standards?
```

---

## 📚 Part-Specific Queries (Test coverage of different FAR parts)

```
What does FAR Part 1 cover?
```

```
What is in FAR Part 12?
```

```
Explain FAR Part 15
```

```
What does Part 52 contain?
```

```
What is FAR Part 31 about?
```

---

## 🚨 Edge Cases (Expected: Graceful handling)

### Reserved Parts
```
What is FAR Part 20?
```

```
Tell me about Part 21
```

### Non-existent Content
```
What is FAR Part 100?
```

```
Show me section 99.999
```

### Out of Scope
```
What is the weather today?
```

```
Tell me a joke
```

---

## 🎯 Quality Check Queries

### Should cite specific sections
```
What are the requirements for using sealed bidding?
```
**Expected Citation:** Part 14

### Should cite multiple sections
```
What types of contracts does the government use?
```
**Expected Citations:** Part 16 (multiple sections)

### Should provide comprehensive answer
```
What are the labor law requirements for government contracts?
```
**Expected Citations:** Part 22 (multiple sections)

---

## 📊 Testing Checklist

After running queries, verify:

- [ ] Responses are relevant to the query
- [ ] Citations include Part.Section format (e.g., "Part 12.101")
- [ ] No hallucinated information
- [ ] Response time < 5 seconds
- [ ] Technical terms are explained correctly
- [ ] Multi-section queries synthesize information logically
- [ ] Edge cases handled gracefully without errors
- [ ] Follow-up questions maintain context

---

## Expected Response Format

A good chatbot response should include:

1. **Direct Answer** - Immediate response to the question
2. **Context** - Relevant background information
3. **Citations** - Specific FAR part/section references
4. **Examples** (if applicable) - Clarifying examples

### Example Good Response

**Query:** "What is a commercial item?"

**Expected Response:**
```
A commercial item is any item, other than real property, that is of a
type customarily used by the general public or by non-governmental
entities for purposes other than governmental purposes, and has been
sold, leased, or licensed to the general public.

Commercial items also include items evolved from a commercial item or
minor modifications to a commercial item made to meet government
requirements.

The acquisition of commercial items is governed by FAR Part 12, which
provides streamlined procedures to take advantage of commercial marketplace
practices and reduce administrative burden.

**Reference:** FAR Part 2.101 (Definitions), FAR Part 12 (Acquisition of
Commercial Products and Commercial Services)
```

---

## Performance Benchmarks

### Response Time
- Simple queries: 1-3 seconds
- Complex queries: 3-5 seconds
- Multi-section synthesis: 4-6 seconds

### Relevance
- Top result relevance score: > 0.70
- All results relevant: > 0.60

### Accuracy
- Citation accuracy: 100%
- Content accuracy: > 95%

---

## Automated Testing

Run the comprehensive test suite:

```bash
cd backend
python scripts/comprehensive_test_suite.py
```

This will:
- Test Qdrant connection
- Verify vector search
- Run sample queries
- Measure performance
- Test edge cases
- Generate test report

---

## Manual Testing Tips

1. **Start Simple** - Test basic queries first
2. **Verify Citations** - Check that cited sections actually exist
3. **Test Follow-ups** - Ask related questions to test context
4. **Try Edge Cases** - Test with unusual queries
5. **Check Performance** - Note any slow responses
6. **Document Issues** - Keep notes on any problems

---

## Common Issues

### Issue: Irrelevant Responses
**Check:** Are you querying about FAR content? Out-of-scope queries may return odd results.

### Issue: No Citations
**Check:** Backend may not be formatting responses correctly. Check logs.

### Issue: Slow Responses
**Check:** Network latency to Qdrant or OpenAI. Check response times in logs.

### Issue: Hallucinated Content
**Check:** This should not happen with RAG. Report immediately if it does.

---

## Next Steps After Testing

If tests pass:
1. ✅ Mark chatbot as production-ready
2. ✅ Deploy to production environment
3. ✅ Monitor real user interactions
4. ✅ Collect feedback for improvements

If tests fail:
1. ❌ Document specific failures
2. ❌ Review Qdrant data quality
3. ❌ Check embedding/retrieval pipeline
4. ❌ Re-test after fixes
