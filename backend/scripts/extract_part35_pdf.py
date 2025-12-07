"""Extract text from Part 35 PDF and create markdown files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def main():
    """Extract Part 35 PDF."""
    logger.info("=== Extracting Part 35 PDF ===\n")

    # Try to import PyPDF2
    try:
        import PyPDF2
    except ImportError:
        logger.error("PyPDF2 not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2

    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "data" / "far" / "pdf" / "part_35" / "Part-35---Research-and-Development-Contracting.pdf"

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return

    logger.info(f"Reading PDF: {pdf_path}")

    # Read PDF
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        logger.info(f"Total pages: {len(reader.pages)}")

        # Extract all text
        full_text = ""
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            full_text += text + "\n\n"
            logger.info(f"  Extracted page {i}")

    logger.info(f"\nTotal text extracted: {len(full_text)} characters")
    logger.info(f"First 500 chars:\n{full_text[:500]}")

    # Save raw text for inspection
    output_path = project_root / "data" / "far" / "processed" / "part_35" / "part_35_raw.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    logger.info(f"\nRaw text saved to: {output_path}")
    logger.info("Next: Manual conversion needed to create proper section files")

if __name__ == "__main__":
    main()
