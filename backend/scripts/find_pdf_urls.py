"""
Helper script to find correct PDF download URLs for FAR parts.

This script scrapes acquisition.gov to find the actual PDF links.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def find_pdf_urls():
    """Find PDF URLs for all FAR parts by scraping acquisition.gov."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("Missing dependencies. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        import requests
        from bs4 import BeautifulSoup

    base_url = "https://www.acquisition.gov"
    far_index_url = f"{base_url}/browse/index/far"

    logger.info(f"Fetching FAR index from: {far_index_url}")

    try:
        response = requests.get(far_index_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links to FAR parts
        pdf_urls = {}

        # Look for part links (pattern: /far/part-1, /far/part-2, etc.)
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Match FAR part pages
            if '/far/part-' in href:
                part_num = href.split('/far/part-')[-1].split('/')[0].split('?')[0]
                try:
                    part_num = int(part_num)
                    if 1 <= part_num <= 53:
                        part_url = base_url + href if href.startswith('/') else href
                        logger.info(f"  Found Part {part_num}: {part_url}")

                        # Now fetch the part page to find PDF link
                        part_response = requests.get(part_url, timeout=30)
                        part_soup = BeautifulSoup(part_response.content, 'html.parser')

                        # Find PDF download link
                        for pdf_link in part_soup.find_all('a', href=True):
                            pdf_href = pdf_link['href']
                            if '.pdf' in pdf_href.lower() and 'part' in pdf_href.lower():
                                pdf_url = base_url + pdf_href if pdf_href.startswith('/') else pdf_href
                                pdf_urls[part_num] = pdf_url
                                logger.info(f"    → PDF: {pdf_url}")
                                break

                except ValueError:
                    pass

        # Save URLs to a file
        output_file = Path(__file__).parent / "far_pdf_urls.txt"
        with open(output_file, 'w') as f:
            f.write("# FAR PDF URLs\n")
            f.write(f"# Generated from: {far_index_url}\n\n")

            for part_num in range(1, 54):
                if part_num in pdf_urls:
                    f.write(f"{part_num}={pdf_urls[part_num]}\n")
                else:
                    f.write(f"{part_num}=NOT_FOUND\n")

        logger.info(f"\n✓ Found {len(pdf_urls)}/53 PDF URLs")
        logger.info(f"✓ Saved to: {output_file}")

        if len(pdf_urls) < 53:
            logger.warning(f"\n⚠ Only found {len(pdf_urls)}/53 PDFs")
            logger.warning("You may need to download missing parts manually from:")
            logger.warning(f"  {far_index_url}")

        return pdf_urls

    except Exception as e:
        logger.error(f"Failed to scrape URLs: {e}")
        logger.info("\nManual download instructions:")
        logger.info(f"1. Go to: {far_index_url}")
        logger.info(f"2. For each part (1-53):")
        logger.info(f"   - Click on the part link")
        logger.info(f"   - Download the PDF")
        logger.info(f"   - Save to: data/far/pdf/all_parts/part_XX.pdf")
        return {}

if __name__ == "__main__":
    find_pdf_urls()
