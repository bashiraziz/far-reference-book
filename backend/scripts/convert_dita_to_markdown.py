"""
Convert DITA XML files to Markdown format for Docusaurus.

Processes FAR DITA files and creates markdown files with frontmatter.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger


def clean_text(text):
    """Clean and normalize text content."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_text_from_element(element):
    """Recursively extract text from XML element and its children."""
    text_parts = []

    # Get direct text
    if element.text:
        text_parts.append(element.text)

    # Process child elements
    for child in element:
        # Handle different DITA elements
        if 'xref' in child.tag:
            # Extract cross-reference text
            if child.text:
                text_parts.append(child.text)
        elif 'ph' in child.tag:
            # Extract phrase text
            if child.text:
                text_parts.append(child.text)
        elif 'p' in child.tag:
            # Paragraph - add newlines
            child_text = extract_text_from_element(child)
            if child_text:
                text_parts.append('\n\n' + child_text)
        elif 'li' in child.tag:
            # List item
            child_text = extract_text_from_element(child)
            if child_text:
                text_parts.append('\n- ' + child_text)
        elif 'ol' in child.tag or 'ul' in child.tag:
            # Ordered/unordered list
            child_text = extract_text_from_element(child)
            if child_text:
                text_parts.append('\n' + child_text)
        else:
            # Generic element - just extract text
            child_text = extract_text_from_element(child)
            if child_text:
                text_parts.append(child_text)

        # Get tail text (text after the element)
        if child.tail:
            text_parts.append(child.tail)

    return ''.join(text_parts)


def convert_dita_to_markdown(dita_file: Path, part_number: int):
    """Convert a DITA file to Markdown with frontmatter."""
    try:
        # Parse DITA XML
        tree = ET.parse(dita_file)
        root = tree.getroot()

        # Find the topic or concept element
        topic = root.find('.//{*}topic')
        if topic is None:
            topic = root.find('.//{*}concept')
        if topic is None:
            logger.warning(f"No topic or concept found in {dita_file}")
            return None

        # Extract topic ID (section number)
        topic_id = topic.get('id', '')
        section_match = re.search(r'FAR_(\d+_\d+(?:-\d+)?)', topic_id)
        if not section_match:
            logger.warning(f"Could not extract section number from {dita_file}")
            return None

        section_number = section_match.group(1).replace('_', '.')

        # Extract title
        title_elem = topic.find('.//{*}title')
        if title_elem is None:
            logger.warning(f"No title found in {dita_file}")
            return None

        title_text = extract_text_from_element(title_elem)
        title_text = clean_text(title_text)

        # Extract body content (try both body and conbody)
        body_elem = topic.find('.//{*}body')
        if body_elem is None:
            body_elem = topic.find('.//{*}conbody')
        if body_elem is None:
            logger.warning(f"No body or conbody found in {dita_file}")
            content = ""
        else:
            content = extract_text_from_element(body_elem)
            content = clean_text(content)

        # Create markdown with frontmatter
        markdown = f"""---
id: {section_number}
title: "{title_text}"
sidebar_label: "{section_number}"
---

# {title_text}

{content}
"""

        return {
            'section_number': section_number,
            'title': title_text,
            'content': markdown
        }

    except Exception as e:
        logger.error(f"Error converting {dita_file}: {e}")
        return None


def process_part(part_number: int, project_root: Path):
    """Process all DITA files for a given part."""
    logger.info(f"\n=== Processing Part {part_number} ===")

    # Input directory
    dita_dir = project_root / "data" / "far" / "pdf" / f"part_{part_number}"
    if not dita_dir.exists():
        logger.error(f"Directory not found: {dita_dir}")
        return 0

    # Output directories
    processed_dir = project_root / "data" / "far" / "processed" / f"part_{part_number}"
    docs_dir = project_root / "docs" / f"part-{part_number}"

    # Create output directories
    processed_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Find all DITA files
    dita_files = sorted(dita_dir.glob("*.dita"))
    logger.info(f"Found {len(dita_files)} DITA files")

    if len(dita_files) == 0:
        logger.warning(f"No DITA files found in {dita_dir}")
        return 0

    converted_count = 0

    for dita_file in dita_files:
        result = convert_dita_to_markdown(dita_file, part_number)

        if result:
            section_number = result['section_number']
            markdown_content = result['content']

            # Save to both directories
            output_filename = f"{section_number}.md"

            # Save to processed directory
            processed_file = processed_dir / output_filename
            with open(processed_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Save to docs directory
            docs_file = docs_dir / output_filename
            with open(docs_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            converted_count += 1
            logger.info(f"  Converted {section_number}")

    logger.info(f"Successfully converted {converted_count}/{len(dita_files)} files")
    return converted_count


def main():
    """Main execution function."""
    logger.info("=== DITA to Markdown Converter ===\n")

    project_root = Path(__file__).parent.parent.parent

    total_converted = 0

    # Process Parts 31-35
    for part_num in range(31, 36):
        count = process_part(part_num, project_root)
        total_converted += count

    logger.info(f"\n=== Summary ===")
    logger.info(f"Total files converted: {total_converted}")


if __name__ == "__main__":
    main()
