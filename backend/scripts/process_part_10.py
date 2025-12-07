"""Process Part 10 PDF - extract, parse, and create markdown files."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from PDF."""
    try:
        import PyPDF2
    except ImportError:
        logger.error("PyPDF2 not installed")
        return ""

    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            logger.info(f"Total pages: {len(reader.pages)}")

            full_text = ""
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                full_text += text + "\n\n"
                logger.info(f"  Extracted page {i}")

        return full_text
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return ""


def parse_sections(text: str):
    """Parse raw Part 10 text into individual sections."""
    sections = {}

    # Pattern to match section headers like "10.000  Scope of part."
    pattern = r'^(10\.\d+(?:-\d+)?)\s+(.+?)$'

    lines = text.split('\n')
    current_section = None
    current_title = None
    current_content = []

    for line in lines:
        # Check if this line is a section header
        match = re.match(pattern, line.strip())

        if match:
            # Save previous section if exists
            if current_section:
                sections[current_section] = {
                    'title': current_title,
                    'content': '\n'.join(current_content).strip()
                }

            # Start new section
            current_section = match.group(1)
            current_title = match.group(2).strip()
            current_content = []
        elif current_section:
            # Add line to current section content
            if line.strip() or current_content:
                current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = {
            'title': current_title,
            'content': '\n'.join(current_content).strip()
        }

    return sections


def create_markdown_file(section_num: str, section_data: dict, output_dir: Path):
    """Create a markdown file for a section."""
    title = section_data['title']
    content = section_data['content']

    # Create markdown with frontmatter
    markdown = f"""---
id: {section_num}
title: "{section_num} {title}"
sidebar_label: "{section_num}"
---

# {section_num} {title}

{content}
"""

    # Save file
    filename = f"{section_num}.md"
    output_file = output_dir / filename

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return filename


def main():
    """Process Part 10 PDF."""
    logger.info("=== Processing Part 10 PDF ===\n")

    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "far" / "pdf" / "part_10" / "Part-10---Market-Research.pdf"

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return

    # Extract text
    logger.info(f"Reading PDF: {pdf_path.name}")
    text = extract_pdf_text(pdf_path)

    if not text:
        logger.error("Failed to extract text from PDF")
        return

    logger.info(f"\nTotal text extracted: {len(text)} characters")

    # Save raw text
    raw_output_dir = project_root / "data" / "far" / "processed" / "part_10"
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    raw_text_file = raw_output_dir / "part_10_raw.txt"

    with open(raw_text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    logger.info(f"Raw text saved to: {raw_text_file}")

    # Parse sections
    sections = parse_sections(text)
    logger.info(f"\nFound {len(sections)} sections")

    if len(sections) == 0:
        logger.warning("No sections found!")
        return

    # Create output directories
    docs_dir = project_root / "docs" / "part-10"
    processed_dir = project_root / "data" / "far" / "processed" / "part_10"

    docs_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Create markdown files
    created_files = []
    for section_num in sorted(sections.keys()):
        section_data = sections[section_num]

        # Create in both directories
        create_markdown_file(section_num, section_data, docs_dir)
        create_markdown_file(section_num, section_data, processed_dir)

        created_files.append(section_num)
        logger.info(f"  Created {section_num}.md - {section_data['title']}")

    logger.info(f"\n=== Summary ===")
    logger.info(f"Created {len(created_files)} markdown files")
    logger.info(f"Output locations:")
    logger.info(f"  - {docs_dir}")
    logger.info(f"  - {processed_dir}")


if __name__ == "__main__":
    main()
