from __future__ import annotations

import re

_LATEX_ESCAPE_RE = re.compile(r'([\\&%$#_{}~^])')
_LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    """Escape user-supplied text for safe insertion into LaTeX."""
    if text is None:
        return ""

    return _LATEX_ESCAPE_RE.sub(lambda match: _LATEX_REPLACEMENTS[match.group(1)], str(text))
