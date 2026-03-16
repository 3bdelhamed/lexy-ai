"""
LARF HTML → Flutter-ready JSON post-processor
src/services/larf/html_processor.py
-----------------------------------------------
Converts annotated HTML from LarfService into a structured
paragraphs → spans JSON that Flutter's RichText / TextSpan
can consume directly — no client-side HTML parsing needed.

Supported tags from your prompts.py:
  <strong>   → "bold"         (entities: dates, numbers, names)
  <mark>     → "highlight"    (key points / conclusions)
  <u>        → "underline"    (unusual phrases / focus items)
  <em> / <i> → "italic"       (extra, defensive support)
  <b>        → "bold"
  inline style color / font-size also parsed
"""

from __future__ import annotations

import re
import uuid
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag


# ─── tag → annotation map ────────────────────────────────────────────────────

_TAG_ANNOTATIONS: dict[str, str] = {
    "strong": "bold",
    "b":      "bold",
    "mark":   "highlight",
    "u":      "underline",
    "em":     "italic",
    "i":      "italic",
    "s":      "strikethrough",
    "del":    "strikethrough",
}

_BLOCK_TAGS = {
    "p", "div", "section", "article",
    "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote",
}

_COLOR_NAMES: dict[str, str] = {
    "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
    "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080",
    "black": "#000000", "white": "#ffffff", "gray": "#808080",
    "grey": "#808080", "pink": "#ffc0cb", "cyan": "#00ffff",
}


# ─── style parser ────────────────────────────────────────────────────────────

def _normalize_color(val: str) -> str | None:
    val = val.strip().lower()
    if val in _COLOR_NAMES:
        return _COLOR_NAMES[val]
    if re.match(r"^#[0-9a-f]{3,8}$", val):
        return val
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", val)
    if m:
        return "#{:02x}{:02x}{:02x}".format(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def _parse_inline_style(style: str) -> list[str]:
    annotations: list[str] = []
    for decl in style.split(";"):
        decl = decl.strip()
        if not decl or ":" not in decl:
            continue
        prop, val = decl.split(":", 1)
        prop, val = prop.strip().lower(), val.strip().lower()

        if prop == "color":
            c = _normalize_color(val)
            if c:
                annotations.append(f"color:{c}")
        elif prop == "background-color":
            c = _normalize_color(val)
            if c:
                annotations.append(f"bg_color:{c}")
        elif prop == "font-weight" and val in ("bold", "700", "800", "900"):
            annotations.append("bold")
        elif prop == "font-style" and val == "italic":
            annotations.append("italic")
        elif prop == "text-decoration":
            if "underline" in val:
                annotations.append("underline")
            if "line-through" in val:
                annotations.append("strikethrough")
        elif prop == "font-size":
            m = re.match(r"(\d+(?:\.\d+)?)(px|pt|em|rem)?", val)
            if m:
                annotations.append(f"size:{m.group(1)}{m.group(2) or 'px'}")
    return annotations


# ─── recursive span extractor ────────────────────────────────────────────────

def _extract_spans(node: Any, inherited: list[str] | None = None) -> list[dict]:
    inherited = inherited or []
    spans: list[dict] = []

    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text:
                spans.append({"text": text, "annotations": list(dict.fromkeys(inherited))})
        elif isinstance(child, Tag):
            extra: list[str] = []
            tag = (child.name or "").lower()

            if tag in _TAG_ANNOTATIONS:
                extra.append(_TAG_ANNOTATIONS[tag])

            style = child.get("style", "") or ""
            if style:
                extra.extend(_parse_inline_style(style))

            for cls in (child.get("class") or []):
                cls = cls.lower()
                if "highlight" in cls or "mark" in cls:
                    extra.append("highlight")
                elif "bold" in cls:
                    extra.append("bold")

            combined = list(dict.fromkeys(inherited + extra))
            spans.extend(_extract_spans(child, combined))

    return spans


def _merge_adjacent(spans: list[dict]) -> list[dict]:
    """Merge consecutive spans with identical annotations → smaller payload."""
    if not spans:
        return []
    merged = [spans[0].copy()]
    for span in spans[1:]:
        if merged[-1]["annotations"] == span["annotations"]:
            merged[-1]["text"] += span["text"]
        else:
            merged.append(span.copy())
    return [s for s in merged if s["text"].strip() or s["text"] in (" ", "\n")]


def _classify_block(tag: str) -> str:
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return "heading"
    if tag == "li":
        return "list_item"
    if tag == "blockquote":
        return "quote"
    return "body"


# ─── public API ──────────────────────────────────────────────────────────────

def html_to_larf_json(
    html: str,
    *,
    doc_id: str | None = None,
    source_text: str | None = None,
) -> dict:
    """
    Convert LARF annotated HTML → Flutter-ready JSON.

    Returns
    -------
    {
      "document_id": str,
      "paragraphs": [
        {
          "index": int,
          "type": "body" | "heading" | "list_item" | "quote",
          "spans": [
            {"text": str, "annotations": ["bold", "highlight", "underline", ...]}
          ]
        }
      ],
      "metadata": {
        "word_count": int,
        "paragraph_count": int,
        "annotation_types": [str],
        "estimated_read_time_sec": int
      }
    }

    Flutter usage:
        RichText(
          text: TextSpan(
            children: para['spans'].map((s) => TextSpan(
              text: s['text'],
              style: _buildStyle(s['annotations']),
            )).toList(),
          ),
        )
    """
    soup = BeautifulSoup(html, "html.parser")

    # Collect block-level nodes; fall back to whole doc
    blocks = soup.find_all(_BLOCK_TAGS, recursive=False)
    if not blocks:
        body = soup.find("body")
        blocks = body.find_all(_BLOCK_TAGS, recursive=False) if body else []
    if not blocks:
        blocks = [soup]

    paragraphs: list[dict] = []
    all_annotation_types: set[str] = set()

    for block in blocks:
        tag_name = (block.name or "div").lower()
        spans = _merge_adjacent(_extract_spans(block))
        if not spans:
            continue

        for span in spans:
            for ann in span["annotations"]:
                all_annotation_types.add(ann.split(":")[0])

        paragraphs.append({
            "index": len(paragraphs),
            "type": _classify_block(tag_name),
            "spans": spans,
        })

    plain = source_text or soup.get_text(" ")
    word_count = len(plain.split())

    return {
        "document_id": doc_id or str(uuid.uuid4()),
        "paragraphs": paragraphs,
        "metadata": {
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
            "annotation_types": sorted(all_annotation_types),
            "estimated_read_time_sec": max(1, round(word_count / 200)) * 60,
        },
    }
