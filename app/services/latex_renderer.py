from __future__ import annotations

from typing import Any

import jinja2

from app.services.latex_utils import escape_latex

latex_env = jinja2.Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader('app/templates'),
)
latex_env.globals['escape_latex'] = escape_latex
latex_env.filters['escape_latex'] = escape_latex


def sanitize_profile(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key in {"email", "linkedin", "github"}:
                sanitized[key] = item
            else:
                sanitized[key] = sanitize_profile(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_profile(item) for item in value]
    if isinstance(value, str):
        return escape_latex(value)
    return value


def render_resume_template(profile_data: dict) -> str:
    template = latex_env.get_template('resume.tex.jinja')
    sanitized = sanitize_profile(profile_data)
    return template.render(**sanitized)
