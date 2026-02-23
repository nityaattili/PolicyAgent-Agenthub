import re
from typing import List

INJECTION_PATTERNS = [
    r"ignore (all|previous|prior) instructions",
    r"disregard (all|previous|prior) instructions",
    r"reveal (the )?(system|developer) prompt",
    r"show me (your|the) hidden instructions",
    r"bypass (policy|guardrails|rules)",
    r"you are now (dan|developer mode)",
    r"act as (a )?system",
    r"do not follow",
    r"override",
]

def detect_prompt_injection(text: str) -> List[str]:
    """
    Simple heuristic detector. Returns matched reasons.
    """
    reasons = []
    t = text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, t):
            reasons.append(f"matched:{pat}")
    return reasons
