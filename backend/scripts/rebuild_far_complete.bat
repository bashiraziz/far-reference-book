@echo off
REM Complete FAR rebuild workflow for Windows
REM Run this to go from PDFs to deployed site

echo ======================================
echo FAR Complete Rebuild Workflow
echo ======================================
echo.

REM Change to project root
cd /d "%~dp0..\.."

echo Step 1/5: Download and process all PDFs...
python backend\scripts\download_and_process_all_pdfs.py

echo.
echo Step 2/5: Check for failed parts...
if exist "backend\scripts\pdf_processing_progress.json" (
    python -c "import json; failed = json.load(open('backend/scripts/pdf_processing_progress.json'))['failed_parts']; print(f'Failed parts: {len(failed)}'); exit(len(failed))"

    if errorlevel 1 (
        echo WARNING: Some parts failed to process
        echo You can retry with Claude API later:
        echo   python backend\scripts\smart_parser_claude.py --retry-failed
        echo.
        echo Continue anyway? (Y/N)
        choice /C YN /M "Press Y to continue or N to stop"
        if errorlevel 2 exit /b
    ) else (
        echo All parts processed successfully!
    )
)

echo.
echo Step 3/5: Building Docusaurus site...
call npm run build

echo.
echo Step 4/5: Upload to Qdrant?
echo WARNING: This will DELETE the existing far_content_production collection!
choice /C YN /M "Continue with Qdrant upload"
if errorlevel 2 (
    echo Skipped Qdrant upload
    goto test
)

echo Uploading to Qdrant...
python backend\scripts\populate_vector_db.py

:test
echo.
echo Step 5/5: Testing chatbot...
python backend\scripts\test_chatbot_production.py

echo.
echo ======================================
echo REBUILD COMPLETE!
echo ======================================
echo.
echo Summary:
python -c "import json; from pathlib import Path; p = Path('backend/scripts/pdf_processing_progress.json'); data = json.load(open(p)) if p.exists() else {}; print(f'Parts: {len(data.get(\"completed_parts\", []))}/53'); print(f'Failed: {len(data.get(\"failed_parts\", []))}')"

echo.
echo Next steps:
echo   - Review docs in: docs\part-XX\
echo   - Test chatbot: python backend\scripts\test_chatbot_production.py
echo   - Deploy: git push (Railway auto-deploys)
echo.
pause
