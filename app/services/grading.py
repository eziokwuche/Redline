from app.schemas import CategoryDelta, DeltaLLMResponse, DeltaQualitativeResponse, GradingLLMResponse, ResumeProfile
from app.services.prompts import build_delta_prompt, build_grading_prompt, build_profile_extraction_prompt


def grade_resume(provider, resume_text: str, job_text: str, target_company: str | None = None) -> GradingLLMResponse:
    system_prompt, user_prompt = build_grading_prompt(resume_text, job_text, target_company)
    return provider.generate_json(system_prompt, user_prompt, GradingLLMResponse)


def compute_category_deltas(previous: GradingLLMResponse, current: GradingLLMResponse) -> list[CategoryDelta]:
    categories = [
        "technical_skills_match",
        "experience_relevance",
        "keyword_optimization",
        "action_verb_strength",
        "quantifiable_impact",
    ]
    deltas: list[CategoryDelta] = []

    for category in categories:
        previous_value = getattr(previous.score_breakdown, category)
        current_value = getattr(current.score_breakdown, category)
        deltas.append(
            CategoryDelta(
                category=category,
                previous=previous_value,
                current=current_value,
                delta=current_value - previous_value,
            )
        )

    return deltas


def compare_versions(
    provider,
    previous_resume_text: str,
    previous_grading: GradingLLMResponse,
    current_resume_text: str,
    current_grading: GradingLLMResponse,
) -> DeltaLLMResponse:
    system_prompt, user_prompt = build_delta_prompt(
        previous_resume_text,
        current_resume_text,
        previous_grading,
        current_grading,
    )
    qualitative = provider.generate_json(system_prompt, user_prompt, DeltaQualitativeResponse)

    return DeltaLLMResponse(
        score_delta=current_grading.overall_match_score - previous_grading.overall_match_score,
        category_deltas=compute_category_deltas(previous_grading, current_grading),
        resolved_issues=qualitative.resolved_issues,
        new_issues=qualitative.new_issues,
        verdict=qualitative.verdict,
    )


def extract_profile(provider, raw_text: str) -> ResumeProfile:
    system_prompt, user_prompt = build_profile_extraction_prompt(raw_text)
    return provider.generate_json(system_prompt, user_prompt, ResumeProfile)


def profile_to_text(profile: ResumeProfile) -> str:
    """Convert a ResumeProfile back to readable text for grading."""
    lines = []
    
    # Header with contact info
    lines.append(profile.name)
    lines.append(f"Phone: {profile.phone} | Email: {profile.email}")
    if profile.linkedin:
        lines.append(f"LinkedIn: {profile.linkedin}")
    if profile.github:
        lines.append(f"GitHub: {profile.github}")
    lines.append("")
    
    # Education
    if profile.education:
        lines.append("EDUCATION")
        for edu in profile.education:
            lines.append(f"{edu.degree} from {edu.institution}, {edu.location}")
            lines.append(f"{edu.dates}")
        lines.append("")
    
    # Experience
    if profile.experience:
        lines.append("EXPERIENCE")
        for exp in profile.experience:
            lines.append(f"{exp.title} at {exp.organization}, {exp.location}")
            lines.append(f"{exp.dates}")
            for bullet in exp.bullets:
                lines.append(f"  • {bullet}")
        lines.append("")
    
    # Projects
    if profile.projects:
        lines.append("PROJECTS")
        for proj in profile.projects:
            lines.append(f"{proj.name} ({proj.tech_stack})")
            lines.append(f"{proj.dates}")
            for bullet in proj.bullets:
                lines.append(f"  • {bullet}")
        lines.append("")
    
    # Skills
    if profile.skills:
        lines.append("SKILLS")
        for skill_cat in profile.skills:
            lines.append(f"{skill_cat.category}: {', '.join(skill_cat.items)}")
    
    return "\n".join(lines)
