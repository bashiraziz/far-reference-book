"""Process Part 35 DITA file to markdown."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.scripts.convert_dita_to_markdown import process_part
from backend.config.logging import logger

def main():
    """Process Part 35."""
    logger.info("=== Processing Part 35 ===\n")

    project_root = Path(__file__).parent.parent.parent
    count = process_part(35, project_root)

    if count > 0:
        logger.info(f"\n✓ Successfully converted {count} file(s) for Part 35")
        logger.info(f"Output locations:")
        logger.info(f"  - docs/part-35/")
        logger.info(f"  - data/far/processed/part_35/")
    else:
        logger.warning("No files were converted for Part 35")

if __name__ == "__main__":
    main()
