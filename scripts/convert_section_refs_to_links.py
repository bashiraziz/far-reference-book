"""
Convert FAR section references to hyperlinks in markdown files.

Finds patterns like "52.219-1" and converts them to markdown links like [52.219-1](/part-52/52.219-1)
"""

import re
from pathlib import Path
import sys

# Pattern to match FAR section references (e.g., 52.219-1, 15.404, 1.101)
# Must be preceded by space, "at ", "section ", or start of line
# Must not already be in a markdown link
SECTION_PATTERN = re.compile(
    r'(?<!\[)(?<!\()(?<=\s|at |section |Section |^)(\d{1,2}\.\d{1,3}(?:-\d{1,2})?)'
    r'(?!\])'  # Negative lookahead to avoid already-linked sections
)

def get_part_number(section: str) -> str:
    """Extract part number from section reference."""
    return section.split('.')[0]

def convert_section_to_link(match: re.Match) -> str:
    """Convert a section reference to a markdown link."""
    section = match.group(1)
    part = get_part_number(section)

    # Format: [52.219-1](/part-52/52.219-1)
    return f'[{section}](/part-{part}/{section})'

def is_already_linked(text: str, pos: int) -> bool:
    """Check if the position is already inside a markdown link."""
    # Look backward for [ or ]
    before = text[:pos]
    # Count brackets
    open_brackets = before.count('[') - before.count(']')
    return open_brackets > 0

def process_file(file_path: Path, dry_run: bool = True) -> tuple[int, int]:
    """
    Process a single markdown file to convert section references.

    Returns:
        (replacements_made, sections_found)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Skip frontmatter (YAML between ---)
        frontmatter_match = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(0)
            body = content[len(frontmatter):]
        else:
            frontmatter = ""
            body = content

        # Find all section references
        matches = list(SECTION_PATTERN.finditer(body))

        if not matches:
            return 0, 0

        # Replace from end to start to preserve positions
        replacements = 0
        for match in reversed(matches):
            section = match.group(1)
            start = match.start(1)
            end = match.end(1)

            # Check if already in a link by looking for [...](...)
            # Look backward and forward
            before = body[max(0, start-50):start]
            after = body[end:min(len(body), end+50)]

            # Skip if it's part of a URL or already linked
            if '](' in before[-10:] or 'http' in before[-20:]:
                continue
            if ')' in after[:10]:
                continue

            # Create the link
            part = get_part_number(section)
            link = f'[{section}](/part-{part}/{section})'

            # Replace in body
            body = body[:start] + link + body[end:]
            replacements += 1

        if replacements > 0:
            new_content = frontmatter + body

            if dry_run:
                print(f"\n{file_path.relative_to(Path.cwd())}:")
                print(f"  Found {len(matches)} section references")
                print(f"  Would replace {replacements} references")
            else:
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✓ {file_path.relative_to(Path.cwd())}: Replaced {replacements} references")

        return replacements, len(matches)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0

def main():
    """Main execution."""
    docs_dir = Path('docs')

    if not docs_dir.exists():
        print(f"Error: docs directory not found at {docs_dir.absolute()}")
        sys.exit(1)

    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 70)
    else:
        print("=" * 70)
        print("LIVE MODE - Files will be modified")
        print("=" * 70)
        response = input("\nContinue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Process all markdown files in docs/part-* directories
    total_files = 0
    total_replacements = 0
    total_sections = 0

    for part_dir in sorted(docs_dir.glob('part-*')):
        if not part_dir.is_dir():
            continue

        for md_file in sorted(part_dir.glob('*.md')):
            replacements, sections = process_file(md_file, dry_run)
            if replacements > 0 or sections > 0:
                total_files += 1
                total_replacements += replacements
                total_sections += sections

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files processed: {total_files}")
    print(f"Section references found: {total_sections}")
    print(f"{'Would replace' if dry_run else 'Replaced'}: {total_replacements} references")

    if dry_run:
        print("\nTo apply changes, run without --dry-run flag:")
        print("  python scripts/convert_section_refs_to_links.py")

if __name__ == '__main__':
    main()
