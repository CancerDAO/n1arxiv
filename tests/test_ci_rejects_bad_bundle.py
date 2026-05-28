"""CI-refusal regression — synthetic bad bundles MUST be refused.

These tests build minimal bundles in tmp_path with deliberate
violations and assert that `scripts.validate_bundle.validate_bundle`
returns `accept=False` with a recognisable reason.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import validate_bundle as vb  # noqa: E402


def _good_manifest(
    file_index: list[str],
    shas: dict[str, str],
    data_source: str = "reference_case",
) -> dict:
    return {
        "schema_version": "0.1",
        "opl_version": "2.4.0",
        "patient_id_hash": "abcdef0123456789",
        "generated_at": "2026-05-28T12:00:00+00:00",
        "data_source": data_source,
        "file_index": file_index,
        "sha256s": shas,
    }


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _good_henry_audit() -> bytes:
    return json.dumps(
        {
            "audit_version": "v2.3",
            "status": "pass",
            "results": [
                {"gate": f"G{n}_x", "status": "PASS", "block": False}
                for n in (29, 30, 31, 32, 33)
            ],
        }
    ).encode("utf-8")


def _write_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in files.items():
            zf.writestr(name, payload)


# ─── happy path baseline ────────────────────────────────────────────────


def test_good_bundle_accepted(tmp_path: Path) -> None:
    manuscript = b"# m\n[BACKGROUND] x [PMID:1].\n"
    audit = _good_henry_audit()
    repro = b"# r\n- src, tier: public\n"
    author = b"# a\nNo human author beyond patient and supervising clinician.\n"
    ethics = b"# ethics\nNot a real patient.\n"
    files_in = {
        "manuscript.md": manuscript,
        "HENRY_AUDIT.json": audit,
        "reproducibility.md": repro,
        "ai_authorship_disclosure.md": author,
        "ethics_declaration.md": ethics,
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    manifest = _good_manifest(list(files_in.keys()), shas)
    bundle = tmp_path / "good.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert ok, reasons


# ─── refusal cases ──────────────────────────────────────────────────────


def test_g29_fail_refused(tmp_path: Path) -> None:
    audit = json.dumps(
        {
            "audit_version": "v2.3",
            "status": "block",
            "results": [
                {"gate": "G29_manuscript_authorship_disclosed", "status": "FAIL", "block": True},
                {"gate": "G30_x", "status": "PASS", "block": False},
                {"gate": "G31_x", "status": "PASS", "block": False},
                {"gate": "G32_x", "status": "PASS", "block": False},
                {"gate": "G33_x", "status": "PASS", "block": False},
            ],
        }
    ).encode("utf-8")
    files_in = {
        "manuscript.md": b"# m\n",
        "HENRY_AUDIT.json": audit,
        "reproducibility.md": b"# r\n",
        "ai_authorship_disclosure.md": b"# a\n",
        "ethics_declaration.md": b"# e\n",
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    manifest = _good_manifest(list(files_in.keys()), shas)
    bundle = tmp_path / "g29.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert not ok
    joined = " ".join(reasons).lower()
    assert "henry" in joined and "g29" in joined.lower()


def test_sha_mismatch_refused(tmp_path: Path) -> None:
    files_in = {
        "manuscript.md": b"# m\n",
        "HENRY_AUDIT.json": _good_henry_audit(),
        "reproducibility.md": b"# r\n",
        "ai_authorship_disclosure.md": b"# a\n",
        "ethics_declaration.md": b"# e\n",
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    # Corrupt the recorded SHA for manuscript.md
    shas["manuscript.md"] = "0" * 64
    manifest = _good_manifest(list(files_in.keys()), shas)
    bundle = tmp_path / "sha.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert not ok
    assert any("sha" in r.lower() for r in reasons), reasons


def test_real_patient_without_consent_refused(tmp_path: Path) -> None:
    files_in = {
        "manuscript.md": b"# m\n",
        "HENRY_AUDIT.json": _good_henry_audit(),
        "reproducibility.md": b"# r\n",
        "ai_authorship_disclosure.md": b"# a\n",
        # ethics has prose but no canonical consent attestation
        "ethics_declaration.md": b"# ethics\nGeneral statement of ethics; no consent string.\n",
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    manifest = _good_manifest(list(files_in.keys()), shas, data_source="real_patient")
    bundle = tmp_path / "noconsent.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert not ok
    assert any("consent" in r.lower() for r in reasons), reasons


def test_real_patient_with_consent_accepted(tmp_path: Path) -> None:
    files_in = {
        "manuscript.md": b"# m\n",
        "HENRY_AUDIT.json": _good_henry_audit(),
        "reproducibility.md": b"# r\n",
        "ai_authorship_disclosure.md": b"# a\n",
        "ethics_declaration.md": (
            b"# ethics\nThe patient has provided informed consent for this "
            b"N=1 case report to be published on N1Arxiv.\n"
        ),
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    manifest = _good_manifest(list(files_in.keys()), shas, data_source="real_patient")
    bundle = tmp_path / "withconsent.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert ok, reasons


def test_missing_publication_gate_refused(tmp_path: Path) -> None:
    audit = json.dumps(
        {
            "audit_version": "v2.3",
            "status": "pass",
            "results": [
                {"gate": "G29_x", "status": "PASS", "block": False},
                {"gate": "G30_x", "status": "PASS", "block": False},
                # G31 missing
                {"gate": "G32_x", "status": "PASS", "block": False},
                {"gate": "G33_x", "status": "PASS", "block": False},
            ],
        }
    ).encode("utf-8")
    files_in = {
        "manuscript.md": b"# m\n",
        "HENRY_AUDIT.json": audit,
        "reproducibility.md": b"# r\n",
        "ai_authorship_disclosure.md": b"# a\n",
        "ethics_declaration.md": b"# e\n",
    }
    shas = {k: _sha(v) for k, v in files_in.items()}
    manifest = _good_manifest(list(files_in.keys()), shas)
    bundle = tmp_path / "missgate.n1a.zip"
    _write_zip(bundle, {**files_in, "manifest.json": json.dumps(manifest).encode("utf-8")})
    ok, reasons = vb.validate_bundle(bundle)
    assert not ok
    assert any("g31" in r.lower() or "missing" in r.lower() for r in reasons), reasons


def test_bad_zip_refused(tmp_path: Path) -> None:
    bad = tmp_path / "not.n1a.zip"
    bad.write_bytes(b"not a zip")
    ok, reasons = vb.validate_bundle(bad)
    assert not ok
    assert any("zip" in r.lower() for r in reasons), reasons
