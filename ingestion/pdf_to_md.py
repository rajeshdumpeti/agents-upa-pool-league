from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


def pdf_to_md(pdf_paths: Iterable[str], out_dir: str) -> list[str]:
    """
    Convert one or more PDF files to simple markdown-like .md files.
    Returns a list of output paths.
    """
    out_paths: list[str] = []
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    for p in pdf_paths:
        pdf_path = Path(p)
        if not pdf_path.exists():
            # Skip missing files quietly for now; we’ll tighten this later.
            continue

        reader = PdfReader(str(pdf_path))
        texts = []
        for i, page in enumerate(reader.pages):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            texts.append(f"# Page {i+1}\n\n{txt.strip()}\n")

        out_name = pdf_path.stem + ".md"
        out_path = out_dir_path / out_name
        out_path.write_text("\n\n".join(texts), encoding="utf-8")
        out_paths.append(str(out_path))

    return out_paths
