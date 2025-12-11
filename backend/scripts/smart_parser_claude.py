"""
Smart FAR PDF parser using Claude API for better accuracy.

Use this for parts where regex parsing fails (especially Part 52).
Costs ~$0.003 per part with Claude Haiku.
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def parse_with_claude(text: str, part_num: int) -> Dict[str, Tuple[str, str]]:
    """Use Claude API to intelligently parse FAR sections."""
    try:
        import anthropic
    except ImportError:
        logger.error("anthropic package not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
        import anthropic

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Set it with:\n"
            "export ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are parsing FAR (Federal Acquisition Regulation) Part {part_num} from PDF text.

Your task: Extract each section as a structured JSON object.

Section format examples:
- "{part_num}.000 Scope of part."
- "{part_num}.101 Definitions."
- "{part_num}.101-1 Specific definition."
- "52.203-1 Contract clause title."

Return JSON in this exact format:
{{
  "sections": [
    {{
      "id": "{part_num}.000",
      "title": "Scope of part",
      "content": "The full text content of this section..."
    }},
    {{
      "id": "{part_num}.101",
      "title": "Definitions",
      "content": "Applied research means..."
    }}
  ]
}}

Rules:
1. Extract ALL sections (even if hundreds)
2. Section ID must match pattern: {part_num}.XXX or {part_num}.XXX-Y
3. Title should NOT end with period
4. Content should include all text until next section
5. Preserve paragraph breaks and formatting
6. If uncertain about boundaries, err on including more content

Here is the PDF text to parse:

{text[:100000]}

Return ONLY the JSON, no other text."""

    logger.info(f"  Calling Claude API to parse Part {part_num}...")
    logger.info(f"  Text length: {len(text)} chars (truncated to 100k for API)")

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Cheap and fast
            max_tokens=16000,  # Enough for Part 52
            temperature=0,  # Deterministic
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text

        # Parse JSON response
        # Claude sometimes wraps in ```json ... ``` so strip that
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        data = json.loads(response_text.strip())

        # Convert to our format: section_id -> (title, content)
        sections = {}
        for section in data.get("sections", []):
            section_id = section["id"]
            title = section["title"]
            content = section["content"]
            sections[section_id] = (title, content)

        logger.info(f"  ✓ Claude parsed {len(sections)} sections")
        logger.info(f"  API usage: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

        return sections

    except Exception as e:
        logger.error(f"  ✗ Claude API error: {e}")
        return {}

def process_part_with_claude(part_num: int, docs_dir: Path) -> Dict:
    """Process a FAR part using Claude API."""
    from download_and_process_all_pdfs import (
        create_markdown_file,
        extract_pdf_text
    )

    result = {
        'part': part_num,
        'success': False,
        'sections_created': 0,
        'error': None,
        'files': []
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"Processing Part {part_num} with Claude API")
    logger.info(f"{'='*60}")

    # Find PDF
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "far" / "pdf" / "all_parts" / f"part_{part_num}.pdf"

    if not pdf_path.exists():
        # Try raw text
        raw_path = project_root / "data" / "far" / "processed" / f"part_{part_num}" / f"part_{part_num}_raw.txt"
        if raw_path.exists():
            logger.info(f"Using raw text from: {raw_path}")
            with open(raw_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            result['error'] = f"No PDF or raw text found at {pdf_path}"
            return result
    else:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        text = extract_pdf_text(pdf_path)
        if not text:
            result['error'] = "Text extraction failed"
            return result

    # Parse with Claude
    sections = parse_with_claude(text, part_num)

    if not sections:
        result['error'] = "Claude parsing returned no sections"
        return result

    # Create markdown files
    part_docs_dir = docs_dir / f"part-{part_num}"
    part_docs_dir.mkdir(parents=True, exist_ok=True)

    for section_id, (title, content) in sections.items():
        filepath = create_markdown_file(section_id, title, content, part_docs_dir)
        result['files'].append(str(filepath))

    result['success'] = True
    result['sections_created'] = len(sections)
    logger.info(f"[SUCCESS] Created {len(sections)} markdown files")

    return result

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse FAR PDFs using Claude API")
    parser.add_argument("--part", type=int, help="Part number to process (1-53)")
    parser.add_argument("--retry-failed", action="store_true", help="Retry all failed parts from progress file")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"

    if args.retry_failed:
        # Load progress and retry failed parts
        progress_file = Path(__file__).parent / "pdf_processing_progress.json"
        if not progress_file.exists():
            logger.error(f"No progress file found at {progress_file}")
            return

        with open(progress_file, 'r') as f:
            progress = json.load(f)

        failed_parts = progress.get('failed_parts', [])
        if not failed_parts:
            logger.info("No failed parts to retry")
            return

        logger.info(f"Retrying {len(failed_parts)} failed parts with Claude API")

        for part_num in failed_parts:
            result = process_part_with_claude(part_num, docs_dir)

            if result['success']:
                # Update progress
                progress['failed_parts'].remove(part_num)
                progress['completed_parts'].append(part_num)
                progress['results'][str(part_num)] = result

                with open(progress_file, 'w') as f:
                    json.dump(progress, f, indent=2)

    elif args.part:
        # Process single part
        result = process_part_with_claude(args.part, docs_dir)

        if result['success']:
            logger.info(f"\n✓ Successfully processed Part {args.part}")
        else:
            logger.error(f"\n✗ Failed to process Part {args.part}: {result['error']}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
