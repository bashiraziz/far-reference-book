"""Fix duplicate slug issues in Part 22 by ensuring unique slugs"""
from pathlib import Path
import re

docs_dir = Path(__file__).parent.parent / 'docs' / 'part-22'

# Process all markdown files
for md_file in sorted(docs_dir.glob('*.md')):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it has frontmatter
    if not content.startswith('---'):
        continue

    parts = content.split('---', 2)
    if len(parts) < 3:
        continue

    frontmatter = parts[1]
    body = parts[2]

    # Extract ID
    id_match = re.search(r'id:\s*([^\n]+)', frontmatter)
    if not id_match:
        continue

    doc_id = id_match.group(1).strip()

    # Check if slug already exists
    if 'slug:' in frontmatter:
        continue

    # Add slug after id line
    new_frontmatter = re.sub(
        r'(id:\s*[^\n]+)',
        f'\\1\nslug: "{doc_id}"',
        frontmatter
    )

    # Write back
    new_content = f'---{new_frontmatter}---{body}'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed: {md_file.name} -> slug: {doc_id}")

print("\nAll Part 22 files updated with explicit slugs!")
