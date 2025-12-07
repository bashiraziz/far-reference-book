"""Parse Part 35 raw text into individual section markdown files."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger


def parse_sections(text: str):
    """Parse raw Part 35 text into individual sections."""
    sections = {}

    # Pattern to match section headers like "35.000  Scope of part."
    # Matches: 35.XXX or 35.XXX-X followed by title
    pattern = r'^(35\.\d+(?:-\d+)?)\s+(.+?)$'

    lines = text.split('\n')
    current_section = None
    current_title = None
    current_content = []

    for i, line in enumerate(lines):
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
            # Skip empty lines at the start
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
    """Parse Part 35 and create markdown files."""
    logger.info("=== Parsing Part 35 into Sections ===\n")

    project_root = Path(__file__).parent.parent.parent
    raw_text_file = project_root / "data" / "far" / "processed" / "part_35" / "part_35_raw.txt"

    if not raw_text_file.exists():
        logger.error(f"Raw text file not found: {raw_text_file}")
        return

    # Read raw text
    with open(raw_text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    logger.info(f"Read {len(text)} characters from {raw_text_file.name}")

    # Parse sections
    sections = parse_sections(text)
    logger.info(f"Found {len(sections)} sections\n")

    # Create output directories
    docs_dir = project_root / "docs" / "part-35"
    processed_dir = project_root / "data" / "far" / "processed" / "part_35"

    docs_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Create markdown files
    created_files = []
    for section_num in sorted(sections.keys()):
        section_data = sections[section_num]

        # Create in both directories
        filename1 = create_markdown_file(section_num, section_data, docs_dir)
        filename2 = create_markdown_file(section_num, section_data, processed_dir)

        created_files.append(section_num)
        logger.info(f"  Created {filename1} - {section_data['title']}")

    logger.info(f"\n=== Summary ===")
    logger.info(f"Created {len(created_files)} markdown files")
    logger.info(f"Output locations:")
    logger.info(f"  - {docs_dir}")
    logger.info(f"  - {processed_dir}")
    logger.info(f"\nSections: {', '.join(created_files)}")


if __name__ == "__main__":
    main()
