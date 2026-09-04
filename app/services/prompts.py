import json

from app.schemas import GradingLLMResponse, ResumeDraftLLMResponse, ResumeProfile


def build_profile_extraction_prompt(resume_text: str) -> tuple[str, str]:
    schema = json.dumps(ResumeProfile.model_json_schema(), separators=(",", ":"))
    system_prompt = (
        "You are an expert resume parser. Your task is to extract structured information from raw resume text "
        "and return it as JSON matching the provided schema exactly. "
        "Be thorough and accurate. For missing fields, use null for optional fields or provide sensible defaults for required fields. "
        "Return only valid JSON matching the schema. No markdown fences, no preamble, no explanations."
    )
    user_prompt = (
        "Resume text:\n"
        f"{resume_text}\n\n"
        "Expected JSON schema:\n"
        f"{schema}\n\n"
        "Extract and return the resume data as JSON."
    )
    return system_prompt, user_prompt


def build_grading_prompt(resume_text: str, job_text: str, target_company: str | None = None) -> tuple[str, str]:
    schema = json.dumps(GradingLLMResponse.model_json_schema(), separators=(",", ":"))
    company_frame = ""
    if target_company:
        company_frame = (
            f" Evaluate this resume as a recruiter at {target_company} would, weighing their known engineering culture and typical technical bar."
        )

    system_prompt = (
        "You are evaluating a resume against a job description for an ATS-like grading system."
        f"{company_frame}"
        " Ground every claim in an exact resume quote from the candidate text. "
        "Score conservatively: 90+ is only for near-perfect matches, and vague or unquantified bullets should score low for quantifiable_impact and action_verb_strength. "
        "Only include missing_keywords when a keyword is truly absent. "
        "Only raise ats_compatibility_flags for issues that genuinely break ATS parsing, such as text inside images, multi-column layouts, table-based skill lists, or contact information in headers. "
        "Return only valid JSON matching the requested schema. No markdown fences, no preamble."
    )
    user_prompt = (
        "Resume text:\n"
        f"{resume_text}\n\n"
        "Job description:\n"
        f"{job_text}\n\n"
        "Expected JSON schema:\n"
        f"{schema}"
    )
    return system_prompt, user_prompt


def build_resume_draft_prompt(
    profile: ResumeProfile,
    job_text: str,
    latest_grading: object | None = None,
    target_company: str | None = None,
) -> tuple[str, str]:
    schema = json.dumps(ResumeDraftLLMResponse.model_json_schema(), separators=(',', ':'))
    company_frame = f' for {target_company}' if target_company else ''
    grading_context = (
        json.dumps(latest_grading, separators=(',', ':'))
        if latest_grading is not None
        else 'No prior grading is available.'
    )
    system_prompt = (
        'You are an ATS resume editor. Create a proposed, user-reviewable resume draft that improves clarity, '
        f'keyword alignment, and action-oriented writing{company_frame}. '
        'Do not invent, infer, exaggerate, or add factual claims. Do not add employers, roles, dates, degrees, '
        'credentials, metrics, technologies, achievements, or contact details not already present in the supplied profile. '
        'Preserve all factual identity, education, role, organization, location, and date fields exactly. '
        'You may rewrite existing bullets for clarity and reorder existing skills, but every claim must remain supported '
        'by the supplied profile. Put any wording the user should verify in factual_claims_to_verify. '
        'Return only valid JSON matching the requested schema.'
    )
    user_prompt = (
        'Current structured resume profile:\n'
        f'{profile.model_dump_json()}\n\n'
        'Target job description:\n'
        f'{job_text}\n\n'
        'Most recent grading context:\n'
        f'{grading_context}\n\n'
        'Expected JSON schema:\n'
        f'{schema}'
    )
    return system_prompt, user_prompt


def build_delta_prompt(previous_resume_text: str, current_resume_text: str, previous_grading: object, current_grading: object) -> tuple[str, str]:
    system_prompt = (
        "You are comparing two resume versions and explaining the change in fit against a job description. "
        "Return only the qualitative comparison fields. Do not compute or invent score_delta or category_deltas; those are produced in Python. "
        "Focus on resolved_issues, new_issues, and verdict."
    )
    user_prompt = (
        "Previous resume:\n"
        f"{previous_resume_text}\n\n"
        "Current resume:\n"
        f"{current_resume_text}\n\n"
        "Previous grading JSON:\n"
        f"{previous_grading.model_dump(mode='json')}\n\n"
        "Current grading JSON:\n"
        f"{current_grading.model_dump(mode='json')}\n\n"
        "Return only a JSON object with resolved_issues, new_issues, and verdict."
    )
    return system_prompt, user_prompt
