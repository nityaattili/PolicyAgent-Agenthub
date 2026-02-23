from typing import Dict, Any, List
from app.rag.retriever import search
from app.utils.security import detect_prompt_injection
from app.utils.pii import contains_pii, redact_pii


def validate_input(state: Dict[str, Any]) -> Dict[str, Any]:
    flags: List[str] = []

    injection_reasons = detect_prompt_injection(state["question"])
    if injection_reasons:
        flags.append("PROMPT_INJECTION_SUSPECTED")

    if contains_pii(state["question"]):
        flags.append("PII_IN_QUESTION")

    state["guardrail_flags"].extend(flags)
    return state


def retrieve_docs(state: Dict[str, Any]) -> Dict[str, Any]:
    results = search(
        question=state["question"],
        user_role=state["user_role"],
        k=5
    )
    state["retrieved_chunks"] = results
    return state


def draft_answer(state: Dict[str, Any]) -> Dict[str, Any]:
    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        state["answer"] = "I don’t have enough policy text to answer confidently. Please contact HR/Legal."
        state["citations"] = []
        state["status"] = "NO_SOURCES"
        return state

    citations: List[Dict[str, Any]] = []
    key_points: List[str] = []

    for c in chunks[:3]:
        citations.append({
            "doc_id": c["doc_id"],
            "chunk_index": c["chunk_index"]
        })

        text = c["chunk_text"].replace("\n", " ")
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        for s in sentences:
            if "classification:" in s.lower():
                continue
            if "allowedroles:" in s.lower():
                continue
            if len(s) < 15:
                continue
            key_points.append(s)

    seen = set()
    cleaned_points: List[str] = []
    for p in key_points:
        if p not in seen:
            seen.add(p)
            cleaned_points.append(p)

    answer_lines: List[str] = []
    answer_lines.append("Here’s what the policy says:")
    answer_lines.append("")
    for p in cleaned_points[:5]:
        answer_lines.append(f"- {p}.")

    state["answer"] = "\n".join(answer_lines)
    state["citations"] = citations
    state["status"] = "ANSWERED"
    return state


def post_check(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("status") == "ANSWERED" and not state.get("citations"):
        state["answer"] = "I cannot answer without citing policy sources."
        state["guardrail_flags"].append("MISSING_CITATIONS")
        state["status"] = "REFUSED"

    redacted_answer, did_redact = redact_pii(state.get("answer", ""))
    if did_redact:
        state["guardrail_flags"].append("PII_REDACTED")

    state["answer"] = redacted_answer
    return state
