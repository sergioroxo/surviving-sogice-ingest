"""
Stage 2 — Document preprocessing.

Routing:
  PDF / EPUB / DOCX  → Docling (primary)  → Unstructured (fallback)
  URL / HTML         → Trafilatura
  Video / Audio      → yt-dlp subtitles → faster-whisper fallback
  SRT                → strip timestamps, clean text

Writes extracted.md and extracted.txt to the local corpus directory.
"""
from __future__ import annotations
from pathlib import Path

from ..config import Config
from ..models.document import IntakeResult, PreprocessResult

TRUNCATION_LIMIT = 24_000
TRUNCATION_HEAD  = 16_000
TRUNCATION_TAIL  =  6_000


def run(intake: IntakeResult, config: Config) -> PreprocessResult:
    raise NotImplementedError


def _preprocess_pdf(path: Path) -> PreprocessResult:
    """Docling primary, Unstructured fallback."""
    raise NotImplementedError


def _preprocess_url(url: str) -> PreprocessResult:
    """Trafilatura extraction."""
    raise NotImplementedError


def _preprocess_video(source: str) -> PreprocessResult:
    """yt-dlp subtitle extraction; faster-whisper transcription fallback."""
    raise NotImplementedError


def _preprocess_srt(path: Path) -> PreprocessResult:
    """Strip SRT/VTT timestamps, return clean transcript text."""
    raise NotImplementedError


def _rate_quality(text: str, tool: str) -> str:
    """Return 'high' | 'medium' | 'low' | 'blocked' based on char count and heuristics."""
    raise NotImplementedError


def _maybe_truncate(text: str) -> tuple[str, bool]:
    if len(text) <= TRUNCATION_LIMIT:
        return text, False
    head = text[:TRUNCATION_HEAD]
    tail = text[-TRUNCATION_TAIL:]
    truncated = f"{head}\n\n[TRUNCATED — {len(text)} total chars]\n\n{tail}"
    return truncated, True


def _save_artifacts(result: PreprocessResult, doc_dir: Path) -> None:
    """Write extracted.md and extracted.txt to the document directory."""
    if result.markdown:
        (doc_dir / "extracted.md").write_text(result.markdown, encoding="utf-8")
    (doc_dir / "extracted.txt").write_text(result.text, encoding="utf-8")
