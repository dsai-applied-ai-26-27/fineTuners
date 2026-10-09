"""Check LaTeX before it reaches a page.

Two layers. A pure-Python lint catches structural slips (unbalanced braces, an unclosed
environment) and always runs. If Node.js is installed, every fragment is also parsed by the
exact KaTeX build the browser uses (static/vendor/katex/katex.min.js), so a typo like
`\\fraq` is reported at sync time with the file and line, instead of showing up as red text
on the site. Node is optional: without it the lint still runs and sync says what was skipped.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

from django.conf import settings

CHECKER = Path(settings.BASE_DIR) / "tools" / "katex_check.cjs"

_ENVIRONMENT = re.compile(r"\\(begin|end)\s*\{([^}]*)\}")
_UNSUPPORTED = {
    r"\label": "KaTeX has no \\label; number an equation with \\tag{1} if you need to",
    r"\ref": "KaTeX has no \\ref; refer to the equation in words",
    r"\eqref": "KaTeX has no \\eqref; refer to the equation in words",
    r"\newcommand": "define nothing inside content; write the expression out",
    r"\usepackage": "packages cannot be loaded; KaTeX supports a fixed set of commands",
}


def lint(tex):
    """Return a problem description, or None when the fragment looks structurally sound."""
    depth = 0
    index = 0
    while index < len(tex):
        char = tex[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return "a `}` closes nothing: braces are unbalanced"
        elif char == "$":
            return "a `$` inside maths: the delimiters are probably misplaced"
        index += 1
    if depth:
        return f"{depth} `{{` never closed: braces are unbalanced"

    stack = []
    for kind, name in _ENVIRONMENT.findall(tex):
        if kind == "begin":
            stack.append(name)
        elif not stack or stack.pop() != name:
            return f"\\end{{{name}}} does not match an open \\begin"
    if stack:
        return f"\\begin{{{stack[-1]}}} is never closed with \\end{{{stack[-1]}}}"

    if len(re.findall(r"\\left\b", tex)) != len(re.findall(r"\\right\b", tex)):
        return "\\left and \\right must come in pairs"
    for command, advice in _UNSUPPORTED.items():
        if re.search(re.escape(command) + r"\b", tex):
            return advice
    return None


def node_available():
    return shutil.which("node") is not None and CHECKER.is_file()


def katex_errors(fragments):
    """Parse each fragment with KaTeX under Node. Returns a list of error strings / None,
    or None when the checker could not be run."""
    payload = json.dumps([{"tex": f.tex, "display": f.display} for f in fragments])
    try:
        result = subprocess.run(
            [shutil.which("node"), str(CHECKER)],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def check(fragments, report):
    """Report every bad fragment. Returns a note describing how thorough the check was."""
    pending = []
    for fragment in fragments:
        problem = lint(fragment.tex)
        if problem:
            report.error(
                fragment.file,
                f"maths: {problem}",
                line=fragment.line,
                where=fragment.where,
                hint=_preview(fragment.tex),
            )
        else:
            pending.append(fragment)

    if not pending:
        return ""
    if not node_available():
        return (
            f"maths: {len(pending)} fragments passed the structural lint; "
            "KaTeX check skipped (Node.js not found)"
        )
    errors = katex_errors(pending)
    if errors is None or len(errors) != len(pending):
        return "maths: KaTeX check could not run; only the structural lint was applied"
    for fragment, error in zip(pending, errors, strict=True):
        if error:
            # KaTeX underlines the bad spot with combining characters; drop them so the
            # message survives a terminal that is not UTF-8.
            error = error.replace("̲", "")
            report.error(
                fragment.file,
                "maths: " + error.removeprefix("KaTeX parse error: "),
                line=fragment.line,
                where=fragment.where,
                hint=_preview(fragment.tex),
            )
    return f"maths: {len(pending)} fragments verified with KaTeX"


def _preview(tex):
    flat = " ".join(tex.split())
    return "in: " + (flat if len(flat) <= 90 else flat[:87] + "...")
