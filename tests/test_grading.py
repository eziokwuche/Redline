from unittest.mock import patch

from app.models import DeltaComparison, JobDescription, Resume, UserSession


def mock_result_model():
    return {
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


def test_grade_endpoint_returns_mocked_result(client, db_session):
    session = UserSession(id='session-1')
    db_session.add(session)
    db_session.commit()

    resume = Resume(
        session_id='session-1',
        version=1,
        original_filename='resume.docx',
        file_type='docx',
        raw_text='Senior Python developer with FastAPI, SQLAlchemy, and cloud experience.',
        extraction_method='python-docx',
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    job = JobDescription(
        session_id='session-1',
        title='Senior Python Engineer',
        company='Example',
        raw_text='Need Python, FastAPI, SQLAlchemy, and cloud experience.',
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    class FakeProvider:
        name = 'mock'
        model = 'fake-model'

        def generate_json(self, system_prompt, user_prompt, response_model):
            return response_model.model_validate(mock_result_model())

    with patch('app.routers.grade.get_llm_provider', return_value=FakeProvider()):
        response = client.post('/api/grade', json={'resume_id': resume.id, 'job_description_id': job.id})

    assert response.status_code == 200
    payload = response.json()
    assert payload['overall_score'] == 92
    assert payload['llm_provider'] == 'mock'
    assert payload['missing_keywords'] == ['kubernetes']


def test_grade_endpoint_uses_target_company_to_shift_score_and_feedback(client, db_session):
    session = UserSession(id='session-company-test')
    db_session.add(session)
    db_session.commit()

    resume = Resume(
        session_id='session-company-test',
        version=1,
        original_filename='resume.docx',
        file_type='docx',
        raw_text='Senior Python developer with FastAPI, SQLAlchemy, and cloud experience.',
        extraction_method='python-docx',
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    job = JobDescription(
        session_id='session-company-test',
        title='Senior Python Engineer',
        company='Example',
        raw_text='Need Python, FastAPI, SQLAlchemy, and cloud experience.',
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    seen_prompts = []

    class FakeProvider:
        name = 'mock'
        model = 'fake-model'

        def generate_json(self, system_prompt, user_prompt, response_model):
            seen_prompts.append(system_prompt)
            if 'Google' in system_prompt:
                payload = {
                    'overall_match_score': 94,
                    'score_breakdown': {
                        'technical_skills_match': 95,
                        'experience_relevance': 92,
                        'keyword_optimization': 96,
                        'action_verb_strength': 90,
                        'quantifiable_impact': 93,
                    },
                    'strengths': [
                        {'category': 'Experience', 'observation': 'Strong product thinking for Google-scale systems', 'evidence': 'Built APIs for large-scale traffic'},
                    ],
                    'areas_for_improvement': [
                        {'category': 'Leadership', 'issue': 'Need more examples of cross-team influence', 'suggestion': 'Add examples of leading across organizations', 'example_rewrite': 'Led cross-functional roadmap planning for platform features'},
                    ],
                    'missing_keywords': ['distributed-systems'],
                    'ats_compatibility_flags': [],
                }
            else:
                payload = {
                    'overall_match_score': 75,
                    'score_breakdown': {
                        'technical_skills_match': 78,
                        'experience_relevance': 72,
                        'keyword_optimization': 80,
                        'action_verb_strength': 76,
                        'quantifiable_impact': 70,
                    },
                    'strengths': [
                        {'category': 'Experience', 'observation': 'Solid Python and API delivery experience', 'evidence': 'Built API services and backend integrations'},
                    ],
                    'areas_for_improvement': [
                        {'category': 'Scale', 'issue': 'Little evidence of large-scale distributed systems work', 'suggestion': 'Highlight operations at scale', 'example_rewrite': 'Owned reliability and performance for a high-throughput platform'},
                    ],
                    'missing_keywords': ['kubernetes', 'distributed-systems'],
                    'ats_compatibility_flags': [],
                }
            return response_model.model_validate(payload)

    with patch('app.routers.grade.get_llm_provider', return_value=FakeProvider()):
        google_response = client.post('/api/grade', json={'resume_id': resume.id, 'job_description_id': job.id, 'target_company': 'Google'})
        stripe_response = client.post('/api/grade', json={'resume_id': resume.id, 'job_description_id': job.id, 'target_company': 'Stripe'})

    assert google_response.status_code == 200
    assert stripe_response.status_code == 200
    assert google_response.json()['overall_score'] != stripe_response.json()['overall_score']
    assert 'Google' in seen_prompts[0]
    assert 'Stripe' in seen_prompts[1]
    assert google_response.json()['strengths'][0]['observation'] != stripe_response.json()['strengths'][0]['observation']


def test_grade_endpoint_returns_404_for_missing_resume(client, db_session):
    session = UserSession(id='session-2')
    db_session.add(session)
    db_session.commit()

    job = JobDescription(
        session_id='session-2',
        title='Senior Python Engineer',
        company='Example',
        raw_text='Need Python, FastAPI, SQLAlchemy, and cloud experience.',
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    response = client.post('/api/grade', json={'resume_id': 9999, 'job_description_id': job.id})
    assert response.status_code == 404


def test_compare_endpoint_persists_delta_for_two_grading_results(client, db_session):
    session = UserSession(id='session-compare')
    db_session.add(session)
    db_session.commit()

    resume = Resume(
        session_id=session.id,
        version=1,
        original_filename='resume.docx',
        file_type='docx',
        raw_text='Python engineer with FastAPI experience.',
        extraction_method='python-docx',
    )
    job = JobDescription(
        session_id=session.id,
        title='Python Engineer',
        raw_text='Need Python and FastAPI experience.',
    )
    db_session.add_all([resume, job])
    db_session.commit()
    db_session.refresh(resume)
    db_session.refresh(job)

    class ComparisonProvider:
        name = 'mock'
        model = 'comparison-model'

        def generate_json(self, system_prompt, user_prompt, response_model):
            if response_model.__name__ == 'DeltaQualitativeResponse':
                return response_model.model_validate({
                    'resolved_issues': ['Added FastAPI evidence.'],
                    'new_issues': [],
                    'verdict': 'The updated resume is stronger.',
                })
            return response_model.model_validate(mock_result_model())

    with patch('app.routers.grade.get_llm_provider', return_value=ComparisonProvider()), patch(
        'app.routers.compare.get_llm_provider', return_value=ComparisonProvider()
    ):
        first = client.post('/api/grade', json={'resume_id': resume.id, 'job_description_id': job.id})
        second = client.post('/api/grade', json={'resume_id': resume.id, 'job_description_id': job.id})
        response = client.post(
            '/api/compare',
            json={
                'previous_grading_id': first.json()['id'],
                'current_grading_id': second.json()['id'],
            },
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload['previous_grading_id'] == first.json()['id']
    assert payload['current_grading_id'] == second.json()['id']
    assert payload['verdict'] == 'The updated resume is stronger.'
    assert db_session.query(DeltaComparison).count() == 1
