#!/usr/bin/env python3
"""Setup test data for the rescan endpoint test."""

__test__ = False

from sqlalchemy.orm import Session
from app.models import Resume, JobDescription, UserSession
from app.database import engine, Base

# Create tables if needed
Base.metadata.create_all(bind=engine)

# Create a session
with Session(engine) as db:
    # Create a user session if needed
    user_session = db.query(UserSession).first()
    if not user_session:
        user_session = UserSession(session_id="test-session-001")
        db.add(user_session)
        db.commit()
    
    session_id = user_session.id
    
    # Create a test resume
    resume = Resume(
        session_id=session_id,
        version=1,
        original_filename="test_resume.txt",
        file_type="txt",
        raw_text="""John Smith
Phone: 555-1234 | Email: john@example.com
LinkedIn: linkedin.com/in/johnsmith

EDUCATION
Bachelor of Science from University of State, Boston, MA
2020

EXPERIENCE
Software Engineer at TechCorp, San Francisco, CA
2021-2023
  • Developed Python backend services
  • Improved API performance by 40%
  • Led team of 3 engineers

SKILLS
Python, JavaScript, React, SQL""",
        extraction_method="text",
    )
    db.add(resume)
    db.commit()
    
    # Create a test job description
    job = JobDescription(
        session_id=session_id,
        title="Senior Software Engineer",
        company="MegaCorp",
        raw_text="""Senior Software Engineer

We are looking for an experienced software engineer with:
- 5+ years of Python experience
- Experience with React and frontend development
- SQL and database design skills
- Leadership experience
- Bachelor's degree in Computer Science

Responsibilities:
- Design and implement scalable backend systems
- Lead engineering team
- Mentor junior engineers
- Participate in architecture decisions""",
    )
    db.add(job)
    db.commit()
    
    print(f"✓ Test data created successfully!")
    print(f"Resume ID: {resume.id}")
    print(f"Job Description ID: {job.id}")
    print(f"Session ID: {session_id}")
