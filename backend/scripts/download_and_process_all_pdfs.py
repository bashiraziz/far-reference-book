"""
Download all FAR PDFs and process them into markdown documentation.

This script:
1. Downloads all 53 FAR part PDFs from acquisition.gov
2. Extracts text from each PDF
3. Parses sections intelligently
4. Creates markdown files in docs/part-XX/ directories
5. Tracks progress and allows resuming
"""
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

# Progress tracking file
PROGRESS_FILE = Path(__file__).parent / "pdf_processing_progress.json"

# FAR PDF URLs - acquisition.gov pattern
def get_pdf_url(part_num: int) -> str:
    """Get the PDF download URL for a specific FAR part."""
    # Note: These URLs may need adjustment based on actual acquisition.gov structure
    # The pattern is typically: https://www.acquisition.gov/sites/default/files/page_file_uploads/Part%2035.pdf
    return f"https://www.acquisition.gov/sites/default/files/page_file_uploads/Part%20{part_num}.pdf"

def download_pdf(part_num: int, output_dir: Path) -> Optional[Path]:
    """Download PDF for a specific part."""
    try:
        import requests
    except ImportError:
        logger.error("requests not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

    url = get_pdf_url(part_num)
    output_path = output_dir / f"part_{part_num}.pdf"

    if output_path.exists():
        logger.info(f"  PDF already exists: {output_path}")
        return output_path

    logger.info(f"  Downloading from: {url}")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"  ✓ Downloaded: {output_path.name} ({len(response.content)} bytes)")
        return output_path

    except Exception as e:
        logger.error(f"  ✗ Failed to download Part {part_num}: {e}")
        return None

def extract_pdf_text(pdf_path: Path) -> Optional[str]:
    """Extract all text from a PDF file."""
    try:
        import PyPDF2
    except ImportError:
        logger.error("PyPDF2 not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2

    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            full_text = ""

            for page in reader.pages:
                text = page.extract_text()
                full_text += text + "\n\n"

            return full_text

    except Exception as e:
        logger.error(f"  ✗ Failed to extract text from {pdf_path}: {e}")
        return None

def parse_sections_from_text(text: str, part_num: int) -> Dict[str, Tuple[str, str]]:
    """
    Parse sections from PDF text.

    Returns dict mapping section_id -> (title, content)

    Pattern examples:
    - "35.000 Scope of part."
    - "35.001 Definitions."
    - "35.017-1 Recordkeeping."
    """
    sections = {}

    # Regex pattern to find section headers
    # Matches: "35.000 Scope of part." or "35.017-1 Recordkeeping."
    section_pattern = rf"^{part_num}\.[\d-]+\s+.+?\.?$"

    lines = text.split('\n')
    current_section_id = None
    current_title = None
    current_content = []

    for line in lines:
        line_stripped = line.strip()

        # Check if this line is a section header
        if re.match(section_pattern, line_stripped):
            # Save previous section if exists
            if current_section_id:
                content = '\n'.join(current_content).strip()
                sections[current_section_id] = (current_title, content)

            # Parse new section
            # Extract section number and title
            match = re.match(rf"({part_num}\.[\d-]+)\s+(.+)", line_stripped)
            if match:
                current_section_id = match.group(1)
                current_title = match.group(2).rstrip('.')
                current_content = []

        elif current_section_id:
            # Add to current section content
            if line_stripped:  # Skip empty lines at boundaries
                current_content.append(line)

    # Save last section
    if current_section_id:
        content = '\n'.join(current_content).strip()
        sections[current_section_id] = (current_title, content)

    return sections

def create_markdown_file(section_id: str, title: str, content: str, output_dir: Path):
    """Create a markdown file for a FAR section."""
    # Create filename: 35.001 -> 35.001.md
    filename = f"{section_id}.md"
    filepath = output_dir / filename

    # Create frontmatter
    frontmatter = f"""---
id: {section_id}
title: "{section_id} {title}"
sidebar_label: "{section_id}"
---

"""

    # Create markdown content
    markdown = frontmatter
    markdown += f"# {section_id} {title}\n\n"
    markdown += content + "\n"

    # Write file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return filepath

def process_part(part_num: int, pdf_dir: Path, docs_dir: Path) -> Dict:
    """Process a single FAR part: download, extract, parse, create markdown files."""
    result = {
        'part': part_num,
        'success': False,
        'sections_created': 0,
        'error': None,
        'files': []
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"Processing Part {part_num}/53")
    logger.info(f"{'='*60}")

    # Step 1: Download PDF
    logger.info(f"Step 1/4: Downloading PDF...")
    pdf_path = download_pdf(part_num, pdf_dir)
    if not pdf_path:
        result['error'] = "Download failed"
        return result

    # Step 2: Extract text
    logger.info(f"Step 2/4: Extracting text from PDF...")
    text = extract_pdf_text(pdf_path)
    if not text:
        result['error'] = "Text extraction failed"
        return result

    logger.info(f"  ✓ Extracted {len(text)} characters")

    # Step 3: Parse sections
    logger.info(f"Step 3/4: Parsing sections...")
    sections = parse_sections_from_text(text, part_num)

    if not sections:
        logger.warning(f"  ⚠ No sections found - may need manual processing")
        # Save raw text for manual processing
        raw_dir = Path(__file__).parent.parent.parent / "data" / "far" / "processed" / f"part_{part_num}"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_file = raw_dir / f"part_{part_num}_raw.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"  ✓ Raw text saved to: {raw_file}")
        result['error'] = "No sections parsed (raw text saved)"
        return result

    logger.info(f"  ✓ Found {len(sections)} sections")

    # Step 4: Create markdown files
    logger.info(f"Step 4/4: Creating markdown files...")
    part_docs_dir = docs_dir / f"part-{part_num}"
    part_docs_dir.mkdir(parents=True, exist_ok=True)

    for section_id, (title, content) in sections.items():
        filepath = create_markdown_file(section_id, title, content, part_docs_dir)
        result['files'].append(str(filepath))

    result['success'] = True
    result['sections_created'] = len(sections)
    logger.info(f"  ✓ Created {len(sections)} markdown files in {part_docs_dir}")

    return result

def load_progress() -> Dict:
    """Load processing progress from file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed_parts': [], 'failed_parts': [], 'results': {}}

def save_progress(progress: Dict):
    """Save processing progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def main():
    """Main processing function."""
    logger.info("="*60)
    logger.info("FAR PDF Download & Processing Script")
    logger.info("="*60)

    project_root = Path(__file__).parent.parent.parent
    pdf_dir = project_root / "data" / "far" / "pdf" / "all_parts"
    docs_dir = project_root / "docs"

    # Load progress
    progress = load_progress()

    logger.info(f"\nConfiguration:")
    logger.info(f"  PDF directory: {pdf_dir}")
    logger.info(f"  Docs directory: {docs_dir}")
    logger.info(f"  Previously completed: {len(progress['completed_parts'])} parts")
    logger.info(f"  Previously failed: {len(progress['failed_parts'])} parts")

    # Process all 53 parts
    total_sections = 0
    start_time = time.time()

    for part_num in range(1, 54):
        # Skip if already completed
        if part_num in progress['completed_parts']:
            logger.info(f"\n[SKIP] Part {part_num} already completed")
            continue

        # Process part
        result = process_part(part_num, pdf_dir, docs_dir)

        # Update progress
        if result['success']:
            progress['completed_parts'].append(part_num)
            total_sections += result['sections_created']
            logger.info(f"[SUCCESS] Part {part_num}: {result['sections_created']} sections")
        else:
            progress['failed_parts'].append(part_num)
            logger.error(f"[FAILED] Part {part_num}: {result['error']}")

        progress['results'][str(part_num)] = result
        save_progress(progress)

        # Small delay to be nice to acquisition.gov servers
        time.sleep(1)

    # Summary
    elapsed = time.time() - start_time
    logger.info("\n" + "="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info("="*60)
    logger.info(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    logger.info(f"Completed parts: {len(progress['completed_parts'])}/53")
    logger.info(f"Failed parts: {len(progress['failed_parts'])}")
    logger.info(f"Total sections created: {total_sections}")

    if progress['failed_parts']:
        logger.warning(f"\nFailed parts (need manual processing):")
        for part_num in progress['failed_parts']:
            error = progress['results'][str(part_num)].get('error', 'Unknown error')
            logger.warning(f"  Part {part_num}: {error}")

    logger.info(f"\nProgress saved to: {PROGRESS_FILE}")
    logger.info(f"Next steps:")
    logger.info(f"  1. Review markdown files in: {docs_dir}")
    logger.info(f"  2. Fix any failed parts manually")
    logger.info(f"  3. Run: npm run build")
    logger.info(f"  4. Upload to Qdrant with populate_vector_db.py")

if __name__ == "__main__":
    main()
