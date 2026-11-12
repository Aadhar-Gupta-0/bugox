"""Offline traceback analysis with conservative, evidence-based guidance.

This analyzer does not execute uploaded code or contact network services.
Its advice is generic and never asserts that a suggested fix is guaranteed.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re

MAX_INPUT = 32_768
PATTERNS = (
    ("NameError", r"\bNameError:\s*(?:name\s+)?['\"]?([A-Za-z_]\w*)['\"]?\s+is not defined",
     "Undefined name", "Check spelling, variable scope, and whether the name was defined before use."),
    ("ModuleNotFoundError", r"\bModuleNotFoundError:\s*No module named ['\"]([^'\"]+)['\"]",
     "Missing module", "Check your environment, dependencies, and module import path."),
    ("ImportError", r"\bImportError:", "Import failure",
     "Check module exports, dependency versions, and circular imports."),
    ("SyntaxError", r"\bSyntaxError:", "Python syntax problem",
     "Inspect the indicated line and its preceding line for brackets, quotes, colons, or indentation."),
    ("IndentationError", r"\bIndentationError:", "Python indentation problem",
     "Use consistent spaces and inspect the block immediately before the reported line."),
    ("TabError", r"\bTabError:", "Inconsistent indentation",
     "Replace mixed tabs and spaces with a consistent indentation style."),
    ("TypeError", r"\bTypeError:", "Incompatible value or operation",
     "Inspect the types and arguments involved; confirm the function signature."),
    ("AttributeError", r"\bAttributeError:", "Missing attribute",
     "Verify the object's actual type and attribute spelling."),
    ("KeyError", r"\bKeyError:", "Missing dictionary key",
     "Check key existence or use an appropriate default with dict.get()."),
    ("IndexError", r"\bIndexError:", "Invalid sequence index",
     "Check sequence length and boundary conditions before indexing."),
    ("ZeroDivisionError", r"\bZeroDivisionError:", "Division by zero",
     "Check for a zero divisor before dividing."),
    ("FileNotFoundError", r"\bFileNotFoundError:", "Missing file",
     "Check the path, current working directory, and file permissions."),
    ("ReferenceError", r"\bReferenceError:", "JavaScript undefined reference",
     "Check variable names, declarations, module imports, and execution order."),
    ("TypeErrorJS", r"\bTypeError:\s*Cannot (?:read|set) properties of",
     "JavaScript null/undefined property access",
     "Check that the value is initialized before accessing its properties."),
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(authorization\s*[:=]\s*bearer\s+)[^\s,'\";]+"),
    re.compile(r"(?i)\b((?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*)['\"]?[^\s,'\";]+"),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{20,})\b"),
)


def redact_secrets(text: str) -> str:
    """Mask common credential-shaped strings before display or storage."""
    safe = text
    for pattern in SECRET_PATTERNS:
        safe = pattern.sub(lambda m: (m.group(1) if m.lastindex else "") + "[REDACTED]", safe)
    return safe


@dataclass(frozen=True)
class Diagnostic:
    category: str
    title: str
    explanation: str
    matched_line: str
    line_number: int | None
    confidence: str

    def to_dict(self) -> dict:
        return asdict(self)


def diagnose(text: str) -> Diagnostic:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste a non-empty error or traceback.")
    if len(text) > MAX_INPUT:
        raise ValueError(f"Input must be at most {MAX_INPUT:,} characters.")
    clean = redact_secrets(text)
    lines = clean.splitlines()
    line_number = None
    matches = re.findall(r'File\s+["\'][^"\']+["\'],\s+line\s+(\d+)', clean)
    if matches:
        line_number = int(matches[-1])
    else:
        js = re.findall(r"(?<!\d):(\d+):\d+\)?", clean)
        if js:
            line_number = int(js[-1])
    # Prefer specific JavaScript property errors before generic TypeError.
    ordered = [PATTERNS[-1], *PATTERNS[:-1]]
    for category, pattern, title, guidance in ordered:
        match = re.search(pattern, clean, flags=re.I)
        if match:
            excerpt = next((line.strip() for line in reversed(lines) if re.search(pattern, line, flags=re.I)), "")
            return Diagnostic(category, title, guidance, excerpt[:300], line_number, "pattern_match")
    return Diagnostic(
        "Unknown", "Further context required",
        "Read the last error line, reproduce with minimal input, and inspect the nearest stack frame. "
        "This offline analyzer cannot safely determine the cause from the supplied text.",
        lines[-1].strip()[:300], line_number, "unclassified",
    )
