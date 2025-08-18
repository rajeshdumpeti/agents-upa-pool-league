# scripts/preview_rules.py
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

from ingestion.pdf_to_md import pdf_to_md
from ingestion.rules_loader import RuleLoader
from utils.config import ConfigError, load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview rules ingestion: PDF -> MD -> Sections")
    parser.add_argument("--config", default="configs/upa.yaml", help="Path to project config YAML")
    parser.add_argument("--md-out", default="./artifacts/raw_md", help="Directory for .md outputs")
    parser.add_argument("--json-out", default="", help="Optional path to write sections as JSON")
    parser.add_argument("--min-chars", type=int, default=40, help="Min chars per section")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
    except ConfigError as e:
        raise SystemExit(str(e)) from e

    pdfs: List[str] = cfg.get("inputs", {}).get("rules_pdfs", [])
    if not pdfs:
        print("No PDFs configured under inputs.rules_pdfs. Add file paths in your YAML.")
        return

    # Step 1: PDF -> MD
    md_dir = Path(args.md_out)
    md_dir.mkdir(parents=True, exist_ok=True)
    md_paths = pdf_to_md(pdfs, md_dir.as_posix())

    if not md_paths:
        print("No .md files were created (are the PDFs present locally?).")
        return

    # Step 2: MD -> Sections
    loader = RuleLoader(min_chars=args.min_chars)
    sections = loader.load_markdown_files(md_paths)

    # Summary
    print("\n=== Ingestion Summary ===")
    print(f"PDFs: {len(pdfs)}")
    print(f"Markdown files: {len(md_paths)} (saved in: {md_dir})")
    print(f"Sections: {len(sections)}")

    # Show a couple of samples
    for s in sections[:3]:
        print("\n--- sample section ---")
        print(f"id: {s.id}")
        print(f"title: {s.title} | page: {s.page} | source: {s.source_file}")
        print(f"text: {s.text[:200]}{'...' if len(s.text) > 200 else ''}")

    # Optional JSON export
    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "count": len(sections),
            "sections": [s.to_dict() for s in sections],
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote sections JSON → {out_path}")


if __name__ == "__main__":
    main()
