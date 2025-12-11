"""
Simple PDF processor - extracts and creates markdown from PDFs.
"""
import sys
import re
from pathlib import Path
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from PDF."""
    try:
        import PyPDF2
    except ImportError:
        logger.info("Installing PyPDF2...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2

    logger.info(f"Reading: {pdf_path.name}")

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        logger.info(f"  Pages: {len(reader.pages)}")

        full_text = ""
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            full_text += text + "\n\n"

        return full_text

def parse_sections(text: str, part_num: int) -> Dict[str, Tuple[str, str]]:
    """Parse sections from PDF text."""
    sections = {}

    # Split by lines
    lines = text.split('\n')
    current_section = None
    current_title = None
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match section headers: "1.000 Scope of part"
        match = re.match(rf'^({part_num}\.\d{{3}}(?:-\d+)?)\s+(.+?)\.?\s*$', line)

        if match:
            # Save previous section
            if current_section:
                content = '\n\n'.join(current_content).strip()
                if content:
                    sections[current_section] = (current_title, content)

            # Start new section
            current_section = match.group(1)
            current_title = match.group(2).rstrip('.')
            current_content = []
            logger.info(f"  Found: {current_section} {current_title}")

        elif current_section:
            # Add to current section
            current_content.append(line)

    # Save last section
    if current_section:
        content = '\n\n'.join(current_content).strip()
        if content:
            sections[current_section] = (current_title, content)

    return sections

def create_markdown(section_id: str, title: str, content: str, output_dir: Path):
    """Create markdown file."""
    filename = f"{section_id}.md"
    filepath = output_dir / filename

    frontmatter = f"""---
id: {section_id}
title: "{section_id} {title}"
sidebar_label: "{section_id}"
---

"""

    markdown = frontmatter + f"# {section_id} {title}\n\n" + content + "\n"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return filepath

def process_pdf(pdf_path: Path, docs_dir: Path):
    """Process a single PDF."""
    # Extract part number from filename
    match = re.search(r'Part-(\d+)', pdf_path.name)
    if not match:
        logger.error(f"Can't extract part number from: {pdf_path.name}")
        return

    part_num = int(match.group(1))

    logger.info(f"\n{'='*60}")
    logger.info(f"Processing Part {part_num}")
    logger.info(f"{'='*60}")

    # Extract text
    logger.info("Step 1/3: Extracting text...")
    text = extract_pdf_text(pdf_path)
    logger.info(f"  Extracted {len(text):,} characters")

    # Parse sections
    logger.info("Step 2/3: Parsing sections...")
    sections = parse_sections(text, part_num)
    logger.info(f"  Found {len(sections)} sections")

    if not sections:
        logger.warning("  No sections found!")
        # Save raw text for debugging
        debug_path = pdf_path.parent.parent / "processed" / f"part_{part_num}_raw.txt"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"  Saved raw text to: {debug_path}")
        return

    # Create markdown files
    logger.info("Step 3/3: Creating markdown files...")
    part_dir = docs_dir / f"part-{part_num}"
    part_dir.mkdir(parents=True, exist_ok=True)

    for section_id, (title, content) in sections.items():
        create_markdown(section_id, title, content, part_dir)

    logger.info(f"  Created {len(sections)} files in: {part_dir}")
    logger.info(f"SUCCESS: Part {part_num} complete!")

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent.parent
    pdf_dir = project_root / "data" / "far" / "pdf"
    docs_dir = project_root / "docs"

    # Find all PDFs
    pdfs = sorted(pdf_dir.glob("Part-*.pdf"))

    if not pdfs:
        logger.error(f"No PDFs found in: {pdf_dir}")
        return

    logger.info(f"Found {len(pdfs)} PDFs to process\n")

    for pdf in pdfs:
        process_pdf(pdf, docs_dir)

    logger.info(f"\n{'='*60}")
    logger.info(f"ALL DONE! Processed {len(pdfs)} parts")
    logger.info(f"{'='*60}")
    logger.info(f"\nMarkdown files created in: {docs_dir}")
    logger.info(f"\nNext steps:")
    logger.info(f"  1. Review markdown files")
    logger.info(f"  2. Run: npm run build")
    logger.info(f"  3. Upload to Qdrant")

if __name__ == "__main__":
    main()
