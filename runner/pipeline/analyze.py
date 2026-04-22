"""
Stage 3b — LLM analysis.

Builds the ingestion-v3.1 prompt, calls Claude or Ollama, validates the JSON
response with Pydantic, and writes analysis.json to the local corpus directory.

LLM routing (controlled by --llm flag):
  claude        → Anthropic API only
  local         → Ollama (gemma4:e4b by default)
  both          → run both, return tuple; review.py shows diff at Checkpoint 3
  prefer-local  → Ollama first, Claude fallback on low confidence or error
  prefer-claude → Claude first, Ollama fallback on API failure
"""
from __future__ import annotations
import json
from pathlib import Path

from ..config import Config
from ..models.document import AnalysisResult, PreprocessResult

PROMPT_VERSION = "ingestion-v3.1"

# Ingestion system prompt lives in 02_working_tools/Claude_Ingestion_Prompt.md.
# The SYSTEM_PROMPT constant below is loaded from that file at runtime so the
# prompt file remains the single source of truth.
_PROMPT_FILE = (
    Path(__file__).parents[3]
    / "02_working_tools"
    / "Claude_Ingestion_Prompt.md"
)


def run(
    preprocess: PreprocessResult,
    llm: str,
    config: Config,
) -> AnalysisResult:
    """Route to the appropriate LLM and return a validated AnalysisResult."""
    if llm == "claude":
        return _analyze_with_claude(preprocess, config)
    elif llm == "local":
        return _analyze_with_ollama(preprocess, config)
    elif llm == "both":
        claude_result = _analyze_with_claude(preprocess, config)
        local_result = _analyze_with_ollama(preprocess, config)
        return _merge_for_review(claude_result, local_result)
    elif llm == "prefer-local":
        try:
            result = _analyze_with_ollama(preprocess, config)
            if result.confidence.status == "low":
                return _analyze_with_claude(preprocess, config)
            return result
        except Exception:
            return _analyze_with_claude(preprocess, config)
    elif llm == "prefer-claude":
        try:
            return _analyze_with_claude(preprocess, config)
        except Exception:
            return _analyze_with_ollama(preprocess, config)
    else:
        raise ValueError(f"Unknown LLM option: {llm!r}")


def _analyze_with_claude(preprocess: PreprocessResult, config: Config) -> AnalysisResult:
    raise NotImplementedError


def _analyze_with_ollama(preprocess: PreprocessResult, config: Config) -> AnalysisResult:
    raise NotImplementedError


def _build_user_message(preprocess: PreprocessResult) -> str:
    raise NotImplementedError


def _fetch_active_lexicon_terms(config: Config) -> list[dict]:
    """Query Sanity for draft + validated lexicon entries to inject into the prompt."""
    raise NotImplementedError


def _validate_response(raw_json: str) -> AnalysisResult:
    """Parse and validate the LLM's JSON response against the AnalysisResult schema."""
    data = json.loads(raw_json)
    return AnalysisResult.model_validate(data)


def _merge_for_review(claude: AnalysisResult, local: AnalysisResult) -> AnalysisResult:
    """When --llm both is used, attach local result as metadata for Checkpoint 3 diff."""
    raise NotImplementedError


def save(doc_id: str, result: AnalysisResult, config: Config) -> None:
    doc_dir = config.corpus_dir / doc_id
    (doc_dir / "analysis.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8"
    )
