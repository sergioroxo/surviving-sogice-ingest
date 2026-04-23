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
import re
from pathlib import Path

from ..config import Config
from ..models.document import IntakeResult, PreprocessResult

# Fallback constants — overridden by config or --max-chars CLI flag
_DEFAULT_LIMIT = 24_000
_HEAD_RATIO    = 0.67   # 2/3 of limit from the front
_TAIL_RATIO    = 0.25   # 1/4 of limit from the end


def run(intake: IntakeResult, config: Config, max_chars: int | None = None) -> PreprocessResult:
    st = intake.source_type
    if st == "url" or st == "html":
        result = _preprocess_url(intake.source)
    elif st == "pdf":
        result = _preprocess_pdf(Path(intake.source))
    elif st == "epub":
        result = _preprocess_pdf(Path(intake.source))  # Docling handles EPUB
    elif st in ("video", "audio"):
        result = _preprocess_video(intake.source)
    elif st == "srt":
        result = _preprocess_srt(Path(intake.source))
    else:
        raise ValueError(f"Unknown source type: {st!r}")

    result.doc_id = intake.doc_id

    # Determine effective limit: CLI flag > env var > default
    limit = max_chars if max_chars is not None else config.truncation_limit
    text, truncated = _maybe_truncate(result.text, limit)
    result.text = text
    result.truncated = truncated
    result.char_count = len(result.text)

    if intake.local_dir:
        _save_artifacts(result, intake.local_dir)

    return result


def _preprocess_url(url: str) -> PreprocessResult:
    try:
        import trafilatura
    except ImportError:
        raise RuntimeError("trafilatura is not installed. Run: pip install trafilatura")

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError(f"trafilatura: could not fetch {url}")

    # JSON output gives us structured metadata alongside the text
    import json as _json
    json_str = trafilatura.extract(
        downloaded,
        output_format="json",
        include_comments=False,
        favor_precision=True,
    )
    metadata: dict = _json.loads(json_str) if json_str else {}
    text = metadata.get("text") or trafilatura.extract(downloaded) or ""
    md   = trafilatura.extract(downloaded, output_format="markdown") or text

    # Extract outbound links via lxml (already a trafilatura dependency)
    outbound_links = _extract_links(downloaded, base_url=url)

    return PreprocessResult(
        doc_id="",
        tool_used="trafilatura",
        quality=_rate_quality(text, "trafilatura"),
        text=text,
        markdown=md,
        title=metadata.get("title", ""),
        author=metadata.get("author", ""),
        date_published=metadata.get("date", ""),
        sitename=metadata.get("sitename", ""),
        description=metadata.get("description", ""),
        hostname=metadata.get("hostname", ""),
        outbound_links=outbound_links,
    )


def _preprocess_pdf(path: Path) -> PreprocessResult:
    """Docling primary, Unstructured fallback."""
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        doc = converter.convert(str(path))
        md   = doc.document.export_to_markdown()
        text = doc.document.export_to_text()
        quality = _rate_quality(text, "docling")
        return PreprocessResult(
            doc_id="",
            tool_used="docling",
            quality=quality,
            text=text,
            markdown=md,
        )
    except ImportError:
        pass
    except Exception as exc:
        import sys
        print(f"[docling error] {exc} — falling back to unstructured", file=sys.stderr)

    # Unstructured fallback
    try:
        from unstructured.partition.auto import partition
        elements = partition(filename=str(path))
        text = "\n\n".join(str(e) for e in elements)
        quality = _rate_quality(text, "unstructured")
        return PreprocessResult(
            doc_id="",
            tool_used="unstructured",
            quality=quality,
            text=text,
        )
    except ImportError:
        raise RuntimeError(
            "Neither docling nor unstructured is installed.\n"
            "Run: pip install docling  (or pip install unstructured)"
        )


def _preprocess_video(source: str) -> PreprocessResult:
    """yt-dlp subtitle extraction; faster-whisper transcription fallback."""
    import tempfile, os

    # Try yt-dlp subtitles first (fast, no compute)
    try:
        import yt_dlp
        with tempfile.TemporaryDirectory() as tmp:
            opts = {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en", "de", "fr", "nl", "no", "sv", "pt", "es"],
                "skip_download": True,
                "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([source])
            srt_files = list(Path(tmp).glob("*.vtt")) + list(Path(tmp).glob("*.srt"))
            if srt_files:
                text = _strip_srt(srt_files[0].read_text(encoding="utf-8"))
                if text.strip():
                    quality = _rate_quality(text, "yt-dlp")
                    return PreprocessResult(
                        doc_id="",
                        tool_used="yt-dlp",
                        quality=quality,
                        text=text,
                    )
    except ImportError:
        pass
    except Exception:
        pass

    # faster-whisper fallback (local file or downloaded audio)
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, info = model.transcribe(source, beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments)
        quality = _rate_quality(text, "whisper")
        return PreprocessResult(
            doc_id="",
            tool_used="whisper",
            quality=quality,
            text=text,
            language_detected=info.language,
        )
    except ImportError:
        raise RuntimeError(
            "Neither yt-dlp nor faster-whisper is installed.\n"
            "Run: pip install yt-dlp faster-whisper"
        )


def _preprocess_srt(path: Path) -> PreprocessResult:
    raw  = path.read_text(encoding="utf-8", errors="replace")
    text = _strip_srt(raw)
    quality = _rate_quality(text, "srt")
    return PreprocessResult(
        doc_id="",
        tool_used="srt",
        quality=quality,
        text=text,
    )


def _strip_srt(raw: str) -> str:
    """Remove SRT/VTT sequence numbers, timestamps, and HTML tags."""
    # VTT header
    raw = re.sub(r"^WEBVTT.*?\n\n", "", raw, flags=re.DOTALL)
    # Timestamps: 00:00:00,000 --> 00:00:00,000  or  00:00.000 --> ...
    raw = re.sub(r"\d+:\d+[\d:,\.]+\s*-->\s*\d+[\d:,\. ]+\n?", "", raw)
    # Sequence numbers on their own line
    raw = re.sub(r"^\d+\s*$", "", raw, flags=re.MULTILINE)
    # VTT cue tags
    raw = re.sub(r"<[^>]+>", "", raw)
    # Collapse blank lines
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def _rate_quality(text: str, tool: str) -> str:
    n = len(text)
    if n == 0:
        return "blocked"
    if n < 500:
        return "low"
    if n < 3000:
        return "medium"
    return "high"


def _maybe_truncate(text: str, limit: int = _DEFAULT_LIMIT) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    head_size = int(limit * _HEAD_RATIO)
    tail_size = int(limit * _TAIL_RATIO)
    head = text[:head_size]
    tail = text[-tail_size:]
    truncated = f"{head}\n\n[TRUNCATED — {len(text)} total chars, showing first {head_size} + last {tail_size}]\n\n{tail}"
    return truncated, True


def _extract_links(html: str, base_url: str, max_links: int = 80) -> list[dict]:
    """Extract outbound links from raw HTML using lxml. Returns up to max_links entries."""
    from urllib.parse import urljoin, urlparse
    try:
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html.encode() if isinstance(html, str) else html)
    except Exception:
        return []

    seen: set[str] = set()
    links: list[dict] = []
    for a in tree.xpath("//a[@href]"):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https") or full in seen:
            continue
        seen.add(full)
        links.append({
            "url":         full,
            "anchor_text": (a.text_content() or "").strip()[:120],
            "domain":      parsed.netloc,
        })
        if len(links) >= max_links:
            break
    return links


def _save_artifacts(result: PreprocessResult, doc_dir: Path) -> None:
    if result.markdown:
        (doc_dir / "extracted.md").write_text(result.markdown, encoding="utf-8")
    (doc_dir / "extracted.txt").write_text(result.text, encoding="utf-8")
