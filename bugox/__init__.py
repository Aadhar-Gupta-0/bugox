"""bugox: local, explainable Python and JavaScript traceback diagnostics."""
from .diagnostics import Diagnostic, diagnose, redact_secrets
__all__ = ["Diagnostic", "diagnose", "redact_secrets"]
