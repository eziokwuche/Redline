#!/usr/bin/env python3
"""
Standalone test script for profile extraction.
Reads the redline-upload-test.docx, extracts text, and parses it into a ResumeProfile.
"""

import json
from pathlib import Path
from docx import Document

from app.services.llm_client import get_llm_provider
from app.services.grading import extract_profile


def main():
    # Read the test DOCX file
    docx_path = Path("redline-upload-test.docx")
    if not docx_path.exists():
        print(f"Error: {docx_path} not found.")
        return

    print(f"Reading resume from {docx_path}...")
    doc = Document(docx_path)
    raw_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    print(f"\n--- Raw resume text ({len(raw_text)} chars) ---")
    print(raw_text[:500] + ("..." if len(raw_text) > 500 else ""))

    # Get LLM provider and extract profile
    print("\n--- Extracting profile ---")
    try:
        provider = get_llm_provider()
        print(f"Using provider: {provider.name}")
        profile = extract_profile(provider, raw_text)
        print("✓ Profile extraction succeeded!")

        # Print the result as JSON
        print("\n--- Extracted ResumeProfile JSON ---")
        print(json.dumps(profile.model_dump(mode="json"), indent=2))
    except Exception as e:
        print(f"✗ Profile extraction failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
