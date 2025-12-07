"""Create reserved placeholder files for Parts 20 and 21."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger


def create_reserved_part(part_num: int, project_root: Path):
    """Create a reserved placeholder markdown file for a part."""

    # Create markdown content
    markdown = f"""---
id: {part_num}.000
title: "Part {part_num} - Reserved"
sidebar_label: "{part_num}.000"
---

# Part {part_num} - Reserved

This part of the Federal Acquisition Regulation (FAR) is reserved for future use.

**Status:** Reserved
**Content:** No content is currently assigned to this part.

Parts 20 and 21 of the FAR are reserved sections that do not contain regulations or guidance. If you are looking for specific procurement or acquisition information, please refer to other parts of the FAR.

For a complete list of active FAR parts and their contents, please consult the FAR Table of Contents.
"""

    # Create output directories
    docs_dir = project_root / "docs" / f"part-{part_num}"
    processed_dir = project_root / "data" / "far" / "processed" / f"part_{part_num}"

    docs_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Save to both directories
    filename = f"{part_num}.000.md"

    docs_file = docs_dir / filename
    with open(docs_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    processed_file = processed_dir / filename
    with open(processed_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    logger.info(f"Created reserved placeholder for Part {part_num}")
    logger.info(f"  - {docs_file}")
    logger.info(f"  - {processed_file}")


def main():
    """Create reserved placeholders for Parts 20 and 21."""
    logger.info("=== Creating Reserved Placeholders for Parts 20-21 ===\n")

    project_root = Path(__file__).parent.parent.parent

    # Create reserved placeholders
    for part_num in [20, 21]:
        create_reserved_part(part_num, project_root)

    logger.info("\n=== Summary ===")
    logger.info("Created reserved placeholders for Parts 20 and 21")
    logger.info("These will be uploaded to Qdrant so users know these parts are reserved")


if __name__ == "__main__":
    main()
