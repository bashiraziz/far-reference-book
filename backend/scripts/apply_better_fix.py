"""Apply the better fix that skips overlap on problematic chunks."""
import re
from pathlib import Path

# Old (current fix - still buggy)
OLD_FIX = r"""(\s+)# Calculate next start, ensuring we always advance to avoid infinite loops
\1if end < text_length:
\1    new_start = end - chunk_overlap
\1    start = max\(new_start, start \+ 1\)  # Always advance by at least 1
\1else:
\1    start = end"""

# Better fix - skip overlap when it would cause backward movement
BETTER_FIX = r"""\1# Calculate next start, ensuring we always advance to avoid infinite loops
\1if end < text_length:
\1    new_start = end - chunk_overlap
\1    # If new_start would move backwards, skip overlap entirely for this chunk
\1    if new_start <= start:
\1        start = end  # Jump to end, no overlap
\1    else:
\1        start = new_start
\1else:
\1    start = end"""

def fix_file(file_path: Path):
    """Apply better fix to a single file."""
    print(f"Fixing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has the current fix
    if "max(new_start, start + 1)" in content:
        # Apply the better fix
        fixed_content = re.sub(OLD_FIX, BETTER_FIX, content, flags=re.MULTILINE)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"  [FIXED] {file_path.name}")
        return True
    else:
        print(f"  - {file_path.name} doesn't have current fix")
        return False

def main():
    """Fix all populate scripts."""
    scripts_dir = Path("backend/scripts")
    populate_scripts = list(scripts_dir.glob("populate*.py"))

    print(f"Found {len(populate_scripts)} populate scripts\n")

    fixed_count = 0
    for script in populate_scripts:
        if fix_file(script):
            fixed_count += 1

    print(f"\n{'='*50}")
    print(f"Fixed {fixed_count} / {len(populate_scripts)} scripts")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
