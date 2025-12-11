#!/bin/bash
# Complete FAR rebuild workflow
# Run this to go from PDFs to deployed site

set -e  # Exit on error

echo "======================================"
echo "FAR Complete Rebuild Workflow"
echo "======================================"
echo ""

# Change to project root
cd "$(dirname "$0")/../.."

echo "Step 1/5: Download and process all PDFs..."
python backend/scripts/download_and_process_all_pdfs.py

echo ""
echo "Step 2/5: Check for failed parts..."
if [ -f "backend/scripts/pdf_processing_progress.json" ]; then
    failed_count=$(python -c "import json; print(len(json.load(open('backend/scripts/pdf_processing_progress.json'))['failed_parts']))")

    if [ "$failed_count" -gt 0 ]; then
        echo "⚠ Found $failed_count failed parts"
        echo "Would you like to retry with Claude API? (y/n)"
        read -r response

        if [ "$response" = "y" ]; then
            echo "Retrying failed parts with Claude API..."
            python backend/scripts/smart_parser_claude.py --retry-failed
        else
            echo "Skipping failed parts (you can retry later)"
        fi
    else
        echo "✓ All parts processed successfully!"
    fi
fi

echo ""
echo "Step 3/5: Building Docusaurus site..."
npm run build

echo ""
echo "Step 4/5: Clearing old Qdrant data..."
echo "⚠ This will DELETE the existing far_content_production collection!"
echo "Continue? (y/n)"
read -r response

if [ "$response" = "y" ]; then
    echo "Uploading to Qdrant..."
    python backend/scripts/populate_vector_db.py
else
    echo "Skipped Qdrant upload"
fi

echo ""
echo "Step 5/5: Testing chatbot..."
python backend/scripts/test_chatbot_production.py

echo ""
echo "======================================"
echo "REBUILD COMPLETE!"
echo "======================================"
echo ""
echo "Summary:"
python -c "
import json
from pathlib import Path

progress_file = Path('backend/scripts/pdf_processing_progress.json')
if progress_file.exists():
    progress = json.load(open(progress_file))
    print(f'  Parts processed: {len(progress[\"completed_parts\"])}/53')
    print(f'  Parts failed: {len(progress[\"failed_parts\"])}')
    total_sections = sum(r.get('sections_created', 0) for r in progress['results'].values())
    print(f'  Total sections: {total_sections}')

# Count markdown files
import subprocess
md_count = subprocess.check_output(['find', 'docs/part-*', '-name', '*.md'], text=True).count('\n')
print(f'  Markdown files: {md_count}')
"

echo ""
echo "Next steps:"
echo "  - Review docs in: docs/part-XX/"
echo "  - Test chatbot: python backend/scripts/test_chatbot_production.py"
echo "  - Deploy: git push (Railway auto-deploys)"
