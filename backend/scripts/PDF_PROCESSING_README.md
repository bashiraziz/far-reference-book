# FAR PDF Processing Guide

Complete workflow for downloading and processing all 53 FAR parts from PDFs into Docusaurus markdown.

## Overview

This folder contains scripts to:
1. **Find PDF URLs** - Scrape acquisition.gov to find download links
2. **Download PDFs** - Download all 53 parts automatically
3. **Extract & Parse** - Convert PDFs to markdown sections
4. **Upload to Qdrant** - Index in vector database for chatbot

## Quick Start

```bash
# 1. Find PDF URLs (optional - URLs are attempted automatically)
python backend/scripts/find_pdf_urls.py

# 2. Download and process all PDFs
python backend/scripts/download_and_process_all_pdfs.py

# 3. Review output in docs/part-XX/ directories

# 4. Build Docusaurus site
npm run build

# 5. Upload to Qdrant
python backend/scripts/populate_vector_db.py
```

## Scripts

### 1. `find_pdf_urls.py`
- Scrapes acquisition.gov to find PDF download links
- Outputs `far_pdf_urls.txt` with all URLs
- Useful if automatic downloads fail

**Usage:**
```bash
python backend/scripts/find_pdf_urls.py
```

**Output:** `backend/scripts/far_pdf_urls.txt`

---

### 2. `download_and_process_all_pdfs.py` (Main Script)
- Downloads all 53 FAR part PDFs
- Extracts text using PyPDF2
- Parses sections with regex patterns
- Creates markdown files in `docs/part-XX/`
- Tracks progress in `pdf_processing_progress.json`
- **Resumable** - rerun to continue from last successful part

**Usage:**
```bash
python backend/scripts/download_and_process_all_pdfs.py
```

**Features:**
- ✅ Progress tracking (resume on failure)
- ✅ Automatic PDF download
- ✅ Section parsing
- ✅ Markdown generation with Docusaurus frontmatter
- ✅ Error handling (saves raw text for manual processing)

**Output:**
- PDFs: `data/far/pdf/all_parts/part_X.pdf`
- Markdown: `docs/part-X/X.XXX.md`
- Progress: `backend/scripts/pdf_processing_progress.json`

---

### 3. `smart_parser_claude.py` (Advanced)
- Uses Claude API for intelligent section parsing
- Better accuracy than regex for complex parts (e.g., Part 52)
- Costs ~$0.10-0.50 per part in API calls
- Use this for parts that fail regex parsing

**Usage:**
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# Parse a specific part
python backend/scripts/smart_parser_claude.py --part 52

# Parse all failed parts
python backend/scripts/smart_parser_claude.py --retry-failed
```

---

## Directory Structure

```
far-reference-book/
├── backend/scripts/
│   ├── download_and_process_all_pdfs.py  # Main script
│   ├── find_pdf_urls.py                   # URL finder
│   ├── smart_parser_claude.py             # Advanced parser
│   ├── pdf_processing_progress.json       # Progress tracking
│   └── far_pdf_urls.txt                   # PDF URLs (generated)
├── data/far/pdf/
│   └── all_parts/
│       ├── part_1.pdf
│       ├── part_2.pdf
│       └── ... (53 total)
└── docs/
    ├── part-1/
    │   ├── 1.000.md
    │   ├── 1.101.md
    │   └── ...
    ├── part-2/
    └── ... (53 total)
```

## Progress Tracking

The script creates `pdf_processing_progress.json`:

```json
{
  "completed_parts": [1, 2, 3, ...],
  "failed_parts": [20, 21],
  "results": {
    "1": {
      "success": true,
      "sections_created": 65,
      "files": [...]
    },
    "20": {
      "success": false,
      "error": "No sections parsed",
      "sections_created": 0
    }
  }
}
```

To resume: Just rerun the script - it skips completed parts.

To reset: Delete `pdf_processing_progress.json`

## Troubleshooting

### Download Fails
**Problem:** Can't download PDFs automatically

**Solution:**
1. Run `find_pdf_urls.py` to get correct URLs
2. Or manually download from https://www.acquisition.gov/browse/index/far
3. Save to `data/far/pdf/all_parts/part_XX.pdf`

### No Sections Parsed
**Problem:** Regex can't parse sections from PDF text

**Solution:**
1. Check `data/far/processed/part_XX/part_XX_raw.txt`
2. Use Claude parser: `python backend/scripts/smart_parser_claude.py --part XX`
3. Or manually create sections in `docs/part-XX/`

### Part 52 Issues
**Problem:** Part 52 has 761 sections - hard to parse

**Solution:**
- Use Claude parser (recommended for accuracy)
- Or download Part 52 as HTML from acquisition.gov (easier to parse)
- Manual creation is impractical for 761 sections

### Missing Dependencies
```bash
pip install requests PyPDF2 beautifulsoup4
```

## Manual Processing (If Needed)

If automatic processing fails for a part:

1. **Extract raw text:**
   ```bash
   python backend/scripts/extract_part35_pdf.py  # Modify for your part
   ```

2. **Review raw text:**
   - Open `data/far/processed/part_XX/part_XX_raw.txt`
   - Identify section boundaries

3. **Create markdown manually:**
   ```markdown
   ---
   id: 35.001
   title: "35.001 Definitions"
   sidebar_label: "35.001"
   ---

   # 35.001 Definitions

   [Content here]
   ```

4. **Save to:**
   `docs/part-35/35.001.md`

## Next Steps After Processing

1. **Verify markdown files:**
   ```bash
   # Count sections
   find docs/part-* -name "*.md" | wc -l
   ```

2. **Build Docusaurus:**
   ```bash
   npm run build
   ```

3. **Upload to Qdrant:**
   ```bash
   python backend/scripts/populate_vector_db.py
   ```

4. **Test chatbot:**
   - Query: "What is FAR Section 5.101?"
   - Verify correct sections returned

## Cost Estimates

### Free (Regex Parsing):
- Download: Free
- PyPDF2 extraction: Free
- Regex parsing: Free
- **Total: $0**

### Claude API Parsing:
- ~2,000 tokens per part (average)
- ~$0.003 per part with Claude Haiku
- **Total for 53 parts: ~$0.16**

### OpenAI Embeddings (Required):
- ~7,718 sections × ~500 tokens each
- text-embedding-3-small: $0.020 per 1M tokens
- **Total: ~$0.08**

**Grand Total: $0.08 - $0.24** depending on parsing method

## Tips

- Run overnight - full processing takes 2-3 hours
- Use Claude parser for Part 52 (most complex)
- Verify Part 1 output before processing all 53
- Keep `pdf_processing_progress.json` - allows resuming
- PDFs are ~100MB total - ensure sufficient disk space
