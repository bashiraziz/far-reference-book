"""Add explicit slug fields to ALL markdown files to prevent Docusaurus conflicts"""
from pathlib import Path
import re

docs_dir = Path(__file__).parent.parent / 'docs'

fixed_count = 0
for md_file in docs_dir.rglob('*.md'):
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

    # Check if slug already exists
    if 'slug:' in frontmatter:
        continue

    # Extract ID
    id_match = re.search(r'id:\s*([^\n]+)', frontmatter)
    if not id_match:
        continue

    doc_id = id_match.group(1).strip()

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

    fixed_count += 1
    if fixed_count % 100 == 0:
        print(f"Fixed {fixed_count} files...")

print(f"\nTotal: {fixed_count} files updated with explicit slugs!")
