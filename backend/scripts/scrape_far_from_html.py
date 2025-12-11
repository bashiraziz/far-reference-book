"""
Scrape FAR content directly from HTML (better than PDF).

This script:
1. Scrapes each FAR part page from acquisition.gov
2. Extracts sections from HTML
3. Creates markdown files directly

NO PDF downloads needed - HTML is cleaner and easier to parse!
"""
import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

PROGRESS_FILE = Path(__file__).parent / "html_scraping_progress.json"

def scrape_part_html(part_num: int) -> str:
    """Scrape HTML content for a FAR part."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("Missing dependencies. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        import requests
        from bs4 import BeautifulSoup

    url = f"https://www.acquisition.gov/far/part-{part_num}"
    logger.info(f"  Fetching: {url}")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text

    except Exception as e:
        logger.error(f"  Failed to fetch Part {part_num}: {e}")
        return ""

def parse_sections_from_html(html: str, part_num: int) -> Dict[str, Tuple[str, str]]:
    """
    Parse FAR sections from acquisition.gov HTML.

    Returns dict: section_id -> (title, content)
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    sections = {}

    # Find all section headings
    # acquisition.gov uses various heading tags with specific patterns
    for heading in soup.find_all(['h2', 'h3', 'h4']):
        text = heading.get_text(strip=True)

        # Match section patterns like "1.101 Purpose" or "52.203-1 Contract clause"
        match = re.match(rf'({part_num}\.\d+(?:-\d+)?)\s+(.+)', text)
        if match:
            section_id = match.group(1)
            title = match.group(2).rstrip('.')

            # Get content - everything until next heading
            content_parts = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    # Stop at next section
                    break

                # Extract text from paragraphs, lists, etc.
                if sibling.name in ['p', 'div', 'ul', 'ol', 'table']:
                    text = sibling.get_text(separator='\n', strip=True)
                    if text:
                        content_parts.append(text)

            content = '\n\n'.join(content_parts)

            if content.strip():
                sections[section_id] = (title, content)

    return sections

def create_markdown_file(section_id: str, title: str, content: str, output_dir: Path):
    """Create a markdown file for a FAR section."""
    filename = f"{section_id}.md"
    filepath = output_dir / filename

    frontmatter = f"""---
id: {section_id}
title: "{section_id} {title}"
sidebar_label: "{section_id}"
---

"""

    markdown = frontmatter
    markdown += f"# {section_id} {title}\n\n"
    markdown += content + "\n"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return filepath

def process_part(part_num: int, docs_dir: Path) -> Dict:
    """Process a single FAR part."""
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

    # Step 1: Scrape HTML
    logger.info(f"Step 1/3: Scraping HTML...")
    html = scrape_part_html(part_num)

    if not html:
        result['error'] = "Failed to fetch HTML"
        return result

    logger.info(f"  Downloaded {len(html)} characters")

    # Step 2: Parse sections
    logger.info(f"Step 2/3: Parsing sections...")
    sections = parse_sections_from_html(html, part_num)

    if not sections:
        logger.warning(f"  No sections found")
        # Save raw HTML for debugging
        debug_dir = Path(__file__).parent.parent.parent / "data" / "far" / "html_debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"part_{part_num}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"  Saved HTML to: {debug_file}")
        result['error'] = "No sections parsed (HTML saved for debugging)"
        return result

    logger.info(f"  Found {len(sections)} sections")

    # Step 3: Create markdown files
    logger.info(f"Step 3/3: Creating markdown files...")
    part_docs_dir = docs_dir / f"part-{part_num}"
    part_docs_dir.mkdir(parents=True, exist_ok=True)

    for section_id, (title, content) in sections.items():
        filepath = create_markdown_file(section_id, title, content, part_docs_dir)
        result['files'].append(str(filepath))

    result['success'] = True
    result['sections_created'] = len(sections)
    logger.info(f"  Created {len(sections)} markdown files")

    return result

def load_progress() -> Dict:
    """Load processing progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed_parts': [], 'failed_parts': [], 'results': {}}

def save_progress(progress: Dict):
    """Save processing progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def main():
    """Main processing function."""
    logger.info("="*60)
    logger.info("FAR HTML Scraping Script")
    logger.info("Scraping from: acquisition.gov")
    logger.info("="*60)

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"

    # Load progress
    progress = load_progress()

    logger.info(f"\nConfiguration:")
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
        result = process_part(part_num, docs_dir)

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

        # Delay to be nice to acquisition.gov
        time.sleep(2)

    # Summary
    elapsed = time.time() - start_time
    logger.info("\n" + "="*60)
    logger.info("SCRAPING COMPLETE")
    logger.info("="*60)
    logger.info(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    logger.info(f"Completed parts: {len(progress['completed_parts'])}/53")
    logger.info(f"Failed parts: {len(progress['failed_parts'])}")
    logger.info(f"Total sections created: {total_sections}")

    if progress['failed_parts']:
        logger.warning(f"\nFailed parts:")
        for part_num in progress['failed_parts']:
            error = progress['results'][str(part_num)].get('error', 'Unknown')
            logger.warning(f"  Part {part_num}: {error}")

    logger.info(f"\nProgress saved to: {PROGRESS_FILE}")
    logger.info(f"\nNext steps:")
    logger.info(f"  1. Review docs/part-XX/ directories")
    logger.info(f"  2. Run: npm run build")
    logger.info(f"  3. Upload to Qdrant: python backend/scripts/populate_vector_db.py")

if __name__ == "__main__":
    main()
