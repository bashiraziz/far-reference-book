"""Fix the infinite loop bug in all populate scripts."""
import re
from pathlib import Path

# Pattern to find the buggy line
OLD_PATTERN = r"(\s+)start = end - chunk_overlap if end < text_length else end"

# Replacement with fixed logic
NEW_CODE = r"""\1# Calculate next start, ensuring we always advance to avoid infinite loops
\1if end < text_length:
\1    new_start = end - chunk_overlap
\1    start = max(new_start, start + 1)  # Always advance by at least 1
\1else:
\1    start = end"""

def fix_file(file_path: Path):
    """Fix the chunking bug in a single file."""
    print(f"Fixing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has the bug
    if "start = end - chunk_overlap if end < text_length else end" in content:
        # Apply the fix
        fixed_content = re.sub(OLD_PATTERN, NEW_CODE, content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"  [FIXED] {file_path.name}")
        return True
    else:
        print(f"  - {file_path.name} already fixed or doesn't have the bug")
        return False

def main():
    """Fix all populate scripts."""
    scripts_dir = Path("backend/scripts")

    # Find all populate scripts
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
