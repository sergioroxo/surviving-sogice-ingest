"""
Stage 3b — LLM analysis.

Builds the ingestion-v3.1 prompt, calls Claude or Ollama, validates the JSON
response with Pydantic, and writes analysis.json to the local corpus directory.

LLM routing (controlled by --llm flag):
  claude        → Anthropic API only
  local         → Ollama (gemma4:e4b by default)
  openrouter    → OpenRouter API (set OPENROUTER_MODEL in .env)
  both          → run both Claude + local, review.py shows diff at Checkpoint 3
  prefer-local  → Ollama first, Claude fallback on low confidence or error
  prefer-claude → Claude first, Ollama fallback on API failure
"""
from __future__ import annotations
import json
import re
from pathlib import Path

from ..config import Config
from ..models.document import AnalysisResult, PreprocessResult

PROMPT_VERSION = "ingestion-v3.1"

_PROMPT_FILE = (
    Path(__file__).parents[2]
    / "02_working_tools"
    / "Claude_Ingestion_Prompt.md"
)

# Cached at module level after first load
_SYSTEM_PROMPT: str | None = None


def _load_system_prompt() -> str:
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        raw = _PROMPT_FILE.read_text(encoding="utf-8")
        # Extract text between first ``` block after "## SYSTEM PROMPT"
        match = re.search(r"## SYSTEM PROMPT\s*\n```\n(.*?)```", raw, re.DOTALL)
        if not match:
            raise RuntimeError(f"Cannot parse system prompt from {_PROMPT_FILE}")
        _SYSTEM_PROMPT = match.group(1).strip()
    return _SYSTEM_PROMPT


def run(
    preprocess: PreprocessResult,
    llm: str,
    config: Config,
) -> AnalysisResult:
    if llm == "claude":
        return _analyze_with_claude(preprocess, config)
    if llm == "local":
        return _analyze_with_ollama(preprocess, config)
    if llm == "openrouter":
        return _analyze_with_openrouter(preprocess, config)
    if llm == "both":
        claude_result = _analyze_with_claude(preprocess, config)
        local_result  = _analyze_with_ollama(preprocess, config)
        return _merge_for_review(claude_result, local_result)
    if llm == "prefer-local":
        try:
            result = _analyze_with_ollama(preprocess, config)
            if result.confidence.status == "low":
                return _analyze_with_claude(preprocess, config)
            return result
        except Exception:
            return _analyze_with_claude(preprocess, config)
    if llm == "prefer-claude":
        try:
            return _analyze_with_claude(preprocess, config)
        except Exception:
            return _analyze_with_ollama(preprocess, config)
    raise ValueError(f"Unknown LLM option: {llm!r}")


def _analyze_with_claude(preprocess: PreprocessResult, config: Config) -> AnalysisResult:
    import anthropic
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    system_prompt = _build_system_prompt_with_lexicon(config)
    user_message  = _build_user_message(preprocess)

    response = client.messages.create(
        model=config.claude_model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    raw_json = response.content[0].text
    return _validate_response(raw_json)


def _analyze_with_ollama(preprocess: PreprocessResult, config: Config) -> AnalysisResult:
    import httpx
    system_prompt = _build_system_prompt_with_lexicon(config)
    user_message  = _build_user_message(preprocess)

    response = httpx.post(
        f"{config.ollama_base_url}/api/chat",
        json={
            "model": config.local_analysis_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        },
        timeout=300,
    )
    response.raise_for_status()
    raw_json = response.json()["message"]["content"]
    return _validate_response(raw_json)


def _analyze_with_openrouter(preprocess: PreprocessResult, config: Config) -> AnalysisResult:
    import httpx
    if not config.openrouter_api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY is not set in runner/.env\n"
            "Get a free key at https://openrouter.ai — no credit card required."
        )
    system_prompt = _build_system_prompt_with_lexicon(config)
    user_message  = _build_user_message(preprocess)

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.openrouter_api_key}",
            "HTTP-Referer":  "https://github.com/sergioroxo/surviving-sogice-ingest",
            "X-Title":       "SurvivingSOGICE",
            "Content-Type":  "application/json",
        },
        json={
            "model": config.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            "temperature": 0.1,
        },
        timeout=300,
    )
    response.raise_for_status()
    raw_json = response.json()["choices"][0]["message"]["content"]
    return _validate_response(raw_json)


def _build_system_prompt_with_lexicon(config: Config) -> str:
    base = _load_system_prompt()
    try:
        terms = _fetch_active_lexicon_terms(config)
    except Exception:
        terms = []

    if not terms:
        return base

    term_lines = "\n".join(
        f"- {t['term']} ({t.get('proposedCluster', '')})"
        for t in terms
    )
    lexicon_injection = (
        f"\n\nCURRENT LEXICON TERMS (do not propose these as candidates):\n{term_lines}"
    )
    return base + lexicon_injection


def _build_user_message(preprocess: PreprocessResult) -> str:
    lines = [
        f"DOCUMENT ID: {preprocess.doc_id}",
        f"PREPROCESSING QUALITY: {preprocess.quality}",
        f"LANGUAGE (if known): {preprocess.language_detected or 'unknown'}",
    ]
    if preprocess.title:
        lines.append(f"TITLE: {preprocess.title}")
    if preprocess.sitename:
        lines.append(f"PUBLISHER / SITE NAME: {preprocess.sitename}")
    if preprocess.hostname:
        lines.append(f"DOMAIN: {preprocess.hostname}")
    if preprocess.author:
        lines.append(f"AUTHOR: {preprocess.author}")
    if preprocess.date_published:
        lines.append(f"DATE PUBLISHED: {preprocess.date_published}")
    if preprocess.description:
        lines.append(f"PAGE DESCRIPTION: {preprocess.description}")
    if preprocess.outbound_links:
        # Give the LLM the first 20 outbound domains for network context
        domains = list(dict.fromkeys(
            lnk["domain"] for lnk in preprocess.outbound_links if lnk["domain"]
        ))[:20]
        lines.append(f"OUTBOUND DOMAINS ({len(preprocess.outbound_links)} links total): {', '.join(domains)}")

    return "\n".join(lines) + "\n\n---\n\nDOCUMENT TEXT:\n" + preprocess.text


def _fetch_active_lexicon_terms(config: Config) -> list[dict]:
    """GROQ query for draft + validated lexicon terms via Sanity Content API."""
    import httpx
    query = '*[_type == "lexiconEntry" && status in ["draft","validated"]]{ term, proposedCluster, function }'
    url = (
        f"https://{config.sanity_project_id}.api.sanity.io"
        f"/v2024-01-01/data/query/{config.sanity_dataset}"
    )
    headers = {"Authorization": f"Bearer {config.sanity_write_token}"}
    r = httpx.get(url, params={"query": query}, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json().get("result", [])


def _validate_response(raw_json: str) -> AnalysisResult:
    """Strip any markdown fences, parse JSON, validate with Pydantic."""
    text = raw_json.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    return AnalysisResult.model_validate(data)


def _merge_for_review(claude: AnalysisResult, local: AnalysisResult) -> AnalysisResult:
    """When --llm both is used, return Claude's result but store local result
    in a private attribute so review.py can show a diff at Checkpoint 3."""
    claude._local_comparison = local  # type: ignore[attr-defined]
    return claude


def save(doc_id: str, result: AnalysisResult, config: Config) -> None:
    doc_dir = config.corpus_dir / doc_id
    (doc_dir / "analysis.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8"
    )
