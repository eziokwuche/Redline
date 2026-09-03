#!/usr/bin/env python3
"""
Mock test for profile extraction.
Demonstrates the functionality by mocking the LLM provider.
"""

import json
from pathlib import Path
from unittest.mock import Mock
from docx import Document
from pydantic import ValidationError

from app.schemas import ResumeProfile
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

    print(f"\n--- Raw resume text ---")
    print(raw_text)

    # Create a mock LLM response for demonstration
    # This is what the LLM would return for this resume
    mock_json_response = {
        "name": "Senior Python Engineer",
        "phone": "555-0123",
        "email": "senior.engineer@example.com",
        "linkedin": "https://linkedin.com/in/seniorengineer",
        "github": "https://github.com/seniorengineer",
        "education": [
            {
                "institution": "State University",
                "location": "Anytown, USA",
                "degree": "B.S. Computer Science",
                "dates": "2014 - 2018"
            }
        ],
        "experience": [
            {
                "title": "Senior Python Engineer",
                "dates": "2021 - Present",
                "organization": "Tech Startup Inc.",
                "location": "San Francisco, CA",
                "bullets": [
                    "Built and maintained FastAPI services handling 100k+ requests/day",
                    "Designed SQLAlchemy ORM models and PostgreSQL schema for core platform",
                    "Led Docker containerization effort reducing deployment time by 60%",
                    "Mentored junior engineers on Python best practices and code review"
                ]
            },
            {
                "title": "Python Developer",
                "dates": "2019 - 2021",
                "organization": "Web Services Corp",
                "location": "Seattle, WA",
                "bullets": [
                    "Developed REST APIs using FastAPI and Flask",
                    "Managed database migrations and schema evolution",
                    "Improved application performance through caching and optimization"
                ]
            }
        ],
        "projects": [
            {
                "name": "Resume-ATS Grader",
                "tech_stack": "FastAPI, SQLAlchemy, PostgreSQL, React, Vite",
                "dates": "2024 - Present",
                "bullets": [
                    "Built full-stack resume evaluation system with LLM integration",
                    "Implemented structured profile extraction from raw text",
                    "Created comparison engine for resume revision tracking"
                ]
            }
        ],
        "skills": [
            {
                "category": "Languages",
                "items": ["Python", "JavaScript", "SQL"]
            },
            {
                "category": "Frameworks & Libraries",
                "items": ["FastAPI", "SQLAlchemy", "React", "Vite"]
            },
            {
                "category": "Databases",
                "items": ["PostgreSQL", "SQLite"]
            },
            {
                "category": "DevOps",
                "items": ["Docker", "Docker Compose", "Git"]
            }
        ]
    }

    print("\n--- Validating mock response against ResumeProfile schema ---")
    try:
        # Validate the mock response
        profile = ResumeProfile.model_validate(mock_json_response)
        print("✓ Validation succeeded!")
        
        print("\n--- Extracted ResumeProfile JSON ---")
        output = json.dumps(profile.model_dump(mode="json"), indent=2)
        print(output)
        
        print(f"\n--- Profile Summary ---")
        print(f"Name: {profile.name}")
        print(f"Email: {profile.email}")
        print(f"Experience entries: {len(profile.experience)}")
        print(f"Education entries: {len(profile.education)}")
        print(f"Project entries: {len(profile.projects)}")
        print(f"Skill categories: {len(profile.skills)}")
        
    except ValidationError as e:
        print(f"✗ Validation failed:")
        print(e)
        return

    # Demonstrate retry logic by showing what would happen with invalid data
    print("\n\n--- Testing retry logic with invalid data (missing required fields) ---")
    invalid_response = {
        "name": "Test",
        # Missing required fields: phone, email, education, experience, projects, skills
    }
    
    print("Attempting to validate invalid response...")
    try:
        ResumeProfile.model_validate(invalid_response)
        print("✗ Validation should have failed!")
    except ValidationError as e:
        print(f"✓ Validation correctly rejected invalid data:")
        print(f"  Errors: {e.error_count()} validation errors")
        for error in e.errors()[:3]:  # Show first 3 errors
            print(f"    - {error['loc']}: {error['msg']}")


if __name__ == "__main__":
    main()
