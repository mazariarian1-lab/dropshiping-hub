from src.research import build_prompt, run_research
from src.workflow import ResearchRequest

def test_prompt_contains_owner_constraints():
    prompt=build_prompt(ResearchRequest())
    assert "USA" in prompt and "<= $50" in prompt and "4-12" in prompt and "never invent evidence" in prompt

def test_research_without_credentials_is_safe(monkeypatch):
    for key in ["PERPLEXITY_API_KEY","GEMINI_API_KEY","ANTHROPIC_API_KEY","CJ_API_KEY","GOOGLE_TRENDS_ENABLED"]: monkeypatch.delenv(key,raising=False)
    result=run_research(ResearchRequest())
    assert result["status"]=="NO_VERIFIED_CANDIDATES" and result["final_candidates"]==[]
