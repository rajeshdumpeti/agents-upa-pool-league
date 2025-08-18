# tests/test_rules_loader.py
from pathlib import Path

from ingestion.rules_loader import RuleLoader, PAGE_RE


def _write_md(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p.as_posix()


def test_page_regex():
    assert PAGE_RE.match("# Page 1")
    assert PAGE_RE.match("# page 12")
    assert not PAGE_RE.match("# Something else")


def test_rules_loader_splits_paragraphs(tmp_path: Path):
    md = """# Page 1

This is a paragraph about break types.
It spans multiple lines but should be one section.

This is a second paragraph on the same page.

# Page 2

Another paragraph on a new page."""
    md_path = _write_md(tmp_path, "rules.md", md)

    loader = RuleLoader(min_chars=10)
    sections = loader.load_markdown_files([md_path])

    # We expect 3 sections total: 2 on page 1, 1 on page 2
    assert len(sections) == 3
    # IDs should be stable/deterministic
    assert sections[0].id.startswith("SEC-rules-p1-s1")
    assert sections[1].id.startswith("SEC-rules-p1-s2")
    assert sections[2].id.startswith("SEC-rules-p2-s1")
    # Titles should reflect page
    assert sections[0].title == "Page 1"
    assert sections[-1].title == "Page 2"


def test_min_chars_filters_noise(tmp_path: Path):
    md = """# Page 1

Too short

This one is definitely long enough to be captured as a section
because it has more than the min char threshold."""
    md_path = _write_md(tmp_path, "tiny.md", md)

    loader = RuleLoader(min_chars=30)
    sections = loader.load_markdown_files([md_path])
    assert len(sections) == 1
    assert "definitely long enough" in sections[0].text
