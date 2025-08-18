from pathlib import Path

from ingestion.pdf_to_md import pdf_to_md


def test_pdf_to_md_handles_missing_files(tmp_path: Path):
    # Should not raise, just return empty list when nothing exists
    out = pdf_to_md(["./data/does-not-exist.pdf"], out_dir=tmp_path.as_posix())
    assert isinstance(out, list)


def test_pdf_to_md_creates_output_dir(tmp_path: Path):
    # No PDFs provided, ensure it still creates the out dir and returns []
    out_dir = tmp_path / "md"
    out = pdf_to_md([], out_dir=out_dir.as_posix())
    assert out == []
    assert out_dir.exists()
