from textwrap import dedent

from fastapi import APIRouter, Depends, HTTPException, status

from ..llm_utils import get_groq_llm
from ..schemas.followup import FollowupDraftRequest, FollowupDraftResponse

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


def _build_prompt(payload: FollowupDraftRequest) -> str:
    missing = ", ".join(payload.missing_sections) if payload.missing_sections else "N/A"
    return dedent(
        f"""
        You are a professional procurement coordinator. The vendor "{payload.vendor_name}" has become unresponsive due to {payload.issue_type.value.replace("_", " ")}.
        Previous follow-ups: {payload.previous_attempts}.
        Missing sections/items: {missing}.
        Context notes: {payload.context_notes or "None"}.
        Provide a polite subject line and email body with tone "{payload.tone}" that:
        - Mentions the issue type and required documents/items.
        - Suggests a gentle deadline.
        - Offers assistance and references procurement escalation if no response.
        Respond in JSON with keys subject, body, suggested_signature.
        """
    ).strip()


@router.post(
    "/draft",
    response_model=FollowupDraftResponse,
    status_code=status.HTTP_200_OK,
)
def draft_followup(payload: FollowupDraftRequest):
    llm = get_groq_llm()
    prompt = _build_prompt(payload)
    response = llm.predict(prompt)
    if not response:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM failed to respond")
    try:
        data = FollowupDraftResponse.parse_raw(response)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned an unparsable response",
        )
    return data

