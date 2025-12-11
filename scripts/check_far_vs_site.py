#!/usr/bin/env python
"""
Compare local FAR sections against the official FAR on acquisition.gov.

Writes a detailed report to: build/far_site_vs_local_report.txt
"""

import re
import time
from pathlib import Path
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

# ---- CONFIG ----

PARTS = range(1, 54)  # FAR Parts 1–53
FAR_PART_URL = "https://www.acquisition.gov/far/part-{part}"

DOCS_ROOT = Path("docs")  # change if you want to compare pdf/processed instead

# section ids like 4.101 or 4.402-2
SECTION_ID_RE = re.compile(r"\b(\d+\.\d+(?:-\d+)?)\b")

REPORT_PATH = Path("build/far_site_vs_local_report.txt")


# ---- 1. Canonical section list from acquisition.gov ----

def fetch_canonical_sections() -> dict[str, set[str]]:
    canonical: dict[str, set[str]] = defaultdict(set)

    for part in PARTS:
        part_str = str(part)
        url = FAR_PART_URL.format(part=part)
        print(f"Fetching FAR Part {part_str} from {url} ...")

        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ! Error fetching Part {part_str}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look at main text-ish elements
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            text = tag.get_text(" ", strip=True)
            for m in SECTION_ID_RE.finditer(text):
                sec = m.group(1)
                # ensure it belongs to this part, e.g. "4.101" for part 4
                if sec.startswith(part_str + "."):
                    canonical[part_str].add(sec)

        # be polite
        time.sleep(0.3)

    return canonical


# ---- 2. Local sections from docs/part-N/*.md ----

def fetch_local_sections_from_docs() -> dict[str, set[str]]:
    """
    Assumes folders like docs/part-1, docs/part-2, etc. and
    section files like 1.101.md, 4.402-2.md, etc.
    """
    local: dict[str, set[str]] = defaultdict(set)

    for part_dir in sorted(DOCS_ROOT.glob("part-*")):
        if not part_dir.is_dir():
            continue

        # docs/part-4 -> "4"
        name = part_dir.name
        part_num = name.split("-")[-1]
        part_num = str(int(part_num))  # normalize e.g. "04" -> "4"

        for f in part_dir.glob("*.md"):
            if f.is_file():
                section_id = f.stem  # "4.101"
                local[part_num].add(section_id)

    return local


# ---- 3. Compare and write report ----

def main():
    print("Building canonical section list from acquisition.gov...")
    canonical = fetch_canonical_sections()

    print("Scanning local docs for section IDs...")
    local = fetch_local_sections_from_docs()

    # make sure build/ exists
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as out:

        def wr(line: str = ""):
            out.write(line + "\n")

        wr("=== FAR Site vs Local Docs Report ===")
        wr("Source site: https://www.acquisition.gov/far")
        wr(f"Compared against local docs in: {DOCS_ROOT}")
        wr("==============================================")
        wr("")

        all_parts = sorted(
            set(canonical.keys()) | set(local.keys()),
            key=lambda x: int(x),
        )

        for part in all_parts:
            c = canonical.get(part, set())
            l = local.get(part, set())

            missing = sorted(c - l, key=lambda s: [int(x) for x in re.split(r"[.-]", s)])
            extra = sorted(l - c, key=lambda s: [int(x) for x in re.split(r"[.-]", s)])

            wr(f"Part {part}")
            wr(f"  Canonical sections (site): {len(c)}")
            wr(f"  Local docs sections:       {len(l)}")

            if missing:
                wr(f"  MISSING locally ({len(missing)}):")
                for sec in missing:
                    wr(f"    - {sec}")
            else:
                wr("  MISSING locally: none")

            if extra:
                wr(f"  EXTRA locally ({len(extra)}) (check for typos/old sections):")
                for sec in extra:
                    wr(f"    - {sec}")
            else:
                wr("  EXTRA locally: none")

            wr("")  # blank line between parts

    print(f"\nDone. Full report written to: {REPORT_PATH}")
    print("Open that file in VS Code to see all missing sections.")


if __name__ == "__main__":
    main()
