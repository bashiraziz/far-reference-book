"""Fix IDs by making them fully unique with part- prefix"""
from pathlib import Path
import re

docs_dir = Path(__file__).parent.parent / 'docs'

fixed_count = 0
for md_file in docs_dir.rglob('*.md'):
    # Get part number from directory
    part_match = re.search(r'part-(\d+)', str(md_file.parent))
    if not part_match:
        continue

    part_num = part_match.group(1)

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        continue

    parts = content.split('---', 2)
    if len(parts) < 3:
        continue

    frontmatter = parts[1]
    body = parts[2]

    # Extract current ID
    id_match = re.search(r'id:\s*([^\n]+)', frontmatter)
    if not id_match:
        continue

    current_id = id_match.group(1).strip()

    # Create new unique ID: part-XX-SECTION
    # e.g., 22.101 -> part-22-22-101
    new_id = f"part-{part_num}-{current_id.replace('.', '-')}"

    # Update ID and slug
    new_frontmatter = re.sub(
        r'id:\s*[^\n]+',
        f'id: {new_id}',
        frontmatter
    )

    # Also update slug to use the original section number (cleaner URLs)
    new_frontmatter = re.sub(
        r'slug:\s*"[^"]+"',
        f'slug: "{current_id}"',
        new_frontmatter
    )

    new_content = f'---{new_frontmatter}---{body}'

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    fixed_count += 1
    if fixed_count % 100 == 0:
        print(f"Fixed {fixed_count} files...")

print(f"\nTotal: {fixed_count} files updated with prefixed IDs!")
