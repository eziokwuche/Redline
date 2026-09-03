import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ['DATABASE_URL'] = 'sqlite:///./test_ats.db'

from app.database import Base, get_db
from app.main import app

engine = create_engine('sqlite:///./test_ats.db', connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def mock_llm_provider(monkeypatch):
    class FakeProvider:
        name = 'mock'
        model = 'fake-model'

        def generate_json(self, system_prompt, user_prompt, response_model):
            if response_model.__name__ == 'ResumeProfile':
                payload = {
                    'name': 'Sample Candidate',
                    'phone': '555-1234',
                    'email': 'sample@example.com',
                    'linkedin': 'linkedin.com/in/sample',
                    'github': 'github.com/sample',
                    'education': [],
                    'experience': [],
                    'projects': [],
                    'skills': [],
                }
                return response_model.model_validate(payload)

            payload = {
                'overall_match_score': 92,
                'score_breakdown': {
                    'technical_skills_match': 90,
                    'experience_relevance': 88,
                    'keyword_optimization': 94,
                    'action_verb_strength': 89,
                    'quantifiable_impact': 91,
                },
                'strengths': [
                    {'category': 'Experience', 'observation': 'Strong Python experience', 'evidence': 'Built APIs in Python'},
                ],
                'areas_for_improvement': [
                    {'category': 'Leadership', 'issue': 'Limited team leadership examples', 'suggestion': 'Add leadership scope', 'example_rewrite': 'Led a team of three engineers'},
                ],
                'missing_keywords': ['kubernetes'],
                'ats_compatibility_flags': [],
            }
            return response_model.model_validate(payload)

    fake_provider = FakeProvider()
    monkeypatch.setattr('app.services.llm_client.get_llm_provider', lambda: fake_provider)
    monkeypatch.setattr('app.routers.grade.get_llm_provider', lambda: fake_provider)
    monkeypatch.setattr('app.routers.upload.get_llm_provider', lambda: fake_provider)
    monkeypatch.setattr('app.routers.compare.get_llm_provider', lambda: fake_provider)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    db = SessionLocal()
    Base.metadata.create_all(bind=connection)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
