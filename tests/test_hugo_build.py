"""Hugo build smoke test.

Gated on `which hugo`. Skips silently if Hugo is not installed so
contributors without Hugo can still run the schema + CI-refusal tests.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _hugo_available() -> bool:
    return shutil.which("hugo") is not None


@pytest.mark.skipif(not _hugo_available(), reason="Hugo not installed")
def test_hugo_build_succeeds(tmp_path: Path) -> None:
    """Run `hugo --gc --minify` and assert it exits 0 and produces
    a non-empty public/ directory."""
    public_dir = tmp_path / "public"
    res = subprocess.run(
        ["hugo", "--gc", "--minify", "--destination", str(public_dir)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"hugo failed:\nstdout: {res.stdout}\nstderr: {res.stderr}"
    assert public_dir.is_dir()
    # The Riaz seed paper must render
    html_files = list(public_dir.rglob("*.html"))
    assert html_files, f"no html generated under {public_dir}"
    combined = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in html_files)
    assert "riaz" in combined.lower() or "methodology reference" in combined.lower()
