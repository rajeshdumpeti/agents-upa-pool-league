# ingestion/rules_loader.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Dict, Any
import re


PAGE_RE = re.compile(r"^#\s*Page\s+(\d+)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    text: str
    source_file: str
    page: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuleLoader:
    """
    Normalize Markdown (from pdf_to_md) into paragraph-sized sections
    with stable IDs so downstream agents can cite them reliably.
    """

    def __init__(self, min_chars: int = 40) -> None:
        self.min_chars = min_chars

    def load_markdown_files(self, md_paths: Iterable[str]) -> List[Section]:
        sections: List[Section] = []
        for path_str in md_paths:
            path = Path(path_str)
            if not path.exists():
                continue
            sections.extend(self._parse_file(path))
        return sections

    # ---- internals -----------------------------------------------------

    def _parse_file(self, path: Path) -> List[Section]:
        text = path.read_text(encoding="utf-8")
        lines = [ln.rstrip() for ln in text.splitlines()]

        sections: List[Section] = []
        page = 1
        para_acc: List[str] = []
        para_index = 0

        def flush_paragraph() -> None:
            nonlocal para_acc, para_index
            paragraph = "\n".join(para_acc).strip()
            if len(paragraph) >= self.min_chars:
                para_index += 1
                sec_id = f"SEC-{path.stem}-p{page}-s{para_index}"
                sections.append(
                    Section(
                        id=sec_id,
                        title=f"Page {page}",
                        text=paragraph,
                        source_file=path.name,
                        page=page,
                    )
                )
            para_acc = []

        for ln in lines:
            m = PAGE_RE.match(ln)
            if m:
                # New page marker; flush any pending paragraph
                flush_paragraph()
                page = int(m.group(1))
                para_index = 0
                continue

            if ln.strip() == "":
                # blank line ends a paragraph
                flush_paragraph()
            else:
                para_acc.append(ln)

        # flush tail
        flush_paragraph()
        return sections
