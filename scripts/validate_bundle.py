#!/usr/bin/env python3
"""N1Arxiv submission validator.

Called by `.github/workflows/validate_submission.yml` on every PR that
touches `static/bundles/**` or `content/papers/**`. Also runnable
standalone:

    python scripts/validate_bundle.py static/bundles/<id>.n1a.zip

Validation steps (all must pass):

  1. Bundle file exists and is a valid zip
  2. `manifest.json` validates against the v0.1 schema
  3. Every file listed in `file_index` exists inside the zip and its
     SHA-256 matches the value recorded in `manifest.sha256s`
  4. `HENRY_AUDIT.json` is present; if its `results[]` lists any of
     G29-G33 with `block: true` OR `status: BLOCK|FAIL`, refuse
  5. If `manifest.data_source == "real_patient"`, require
     `ethics_declaration.md` to contain the canonical consent
     attestation string (case-insensitive, whitespace-collapsed)

Exit code 0 = accept; non-zero = refuse (CI fails the PR).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

import jsonschema


# Henry gates that gate publication on N1Arxiv. Drift from this list is
# coordinated with `CancerDAO/opl-cancer` ADR-0023 (G29-G33).
PUBLICATION_GATES = ("G29", "G30", "G31", "G32", "G33")

# Canonical consent attestation. Matched case-insensitive, whitespace-
# normalised. The string is intentionally specific so casual copy-paste
# of a generic ethics paragraph does not satisfy it. Authors writing
# their own `ethics_declaration.md` should include this sentence
# verbatim when submitting a real_patient bundle.
CANONICAL_CONSENT = (
    "the patient has provided informed consent for this n=1 case "
    "report to be published on n1arxiv"
)


def _norm(text: str) -> str:
    """Lowercase, collapse whitespace — used for consent string match."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _schema_path() -> Path:
    """Resolve the bundled schema regardless of CWD."""
    here = Path(__file__).resolve().parent
    return here.parent / "schemas" / "n1a_bundle.v0.1.schema.json"


def _load_schema() -> dict[str, Any]:
    return json.loads(_schema_path().read_text(encoding="utf-8"))


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def validate_bundle(bundle_path: Path) -> tuple[bool, list[str]]:
    """Returns (accept, reasons[]).

    `accept=False` ⇒ reasons[] is the refusal list.
    `accept=True` ⇒ reasons[] is an informational checklist (logged on
    success so CI logs are useful).
    """
    reasons: list[str] = []

    if not bundle_path.is_file():
        return False, [f"bundle not found: {bundle_path}"]

    try:
        zf = zipfile.ZipFile(bundle_path)
    except zipfile.BadZipFile as exc:
        return False, [f"not a valid zip: {exc}"]

    try:
        try:
            manifest_raw = zf.read("manifest.json")
        except KeyError:
            return False, ["bundle is missing manifest.json"]

        try:
            manifest = json.loads(manifest_raw)
        except json.JSONDecodeError as exc:
            return False, [f"manifest.json is not valid JSON: {exc}"]

        # 1. Schema
        try:
            jsonschema.validate(instance=manifest, schema=_load_schema())
            reasons.append("schema: OK")
        except jsonschema.ValidationError as exc:
            return False, [f"schema: {exc.message} at {list(exc.absolute_path)}"]

        # 2. SHA-256 round-trip for every listed file
        file_index = manifest.get("file_index", [])
        sha_map = manifest.get("sha256s", {})
        names_in_zip = set(zf.namelist())
        for rel in file_index:
            if rel == "manifest.json":
                # manifest itself is not hashed in sha256s — skip
                continue
            if rel not in names_in_zip:
                return False, [f"file listed in file_index but missing from zip: {rel}"]
            expected = sha_map.get(rel)
            if not expected:
                return False, [f"file_index lists {rel} but no sha256 recorded"]
            actual = _sha256_bytes(zf.read(rel))
            if actual != expected:
                return False, [
                    f"sha256 mismatch for {rel}: expected {expected}, got {actual}"
                ]
        reasons.append(f"sha256: {len(file_index)} files verified")

        # 3. Henry G29-G33 gate check
        if "HENRY_AUDIT.json" not in names_in_zip:
            return False, ["bundle is missing HENRY_AUDIT.json"]
        try:
            henry = json.loads(zf.read("HENRY_AUDIT.json"))
        except json.JSONDecodeError as exc:
            return False, [f"HENRY_AUDIT.json is not valid JSON: {exc}"]

        blocked: list[str] = []
        results = henry.get("results") or []
        if not isinstance(results, list):
            return False, ["HENRY_AUDIT.json: 'results' must be a list"]
        seen_gates: set[str] = set()
        for r in results:
            if not isinstance(r, dict):
                continue
            gate = str(r.get("gate") or "")
            status = str(r.get("status") or "").upper()
            block_flag = bool(r.get("block", False))
            # We track G29-G33 specifically — other gates are informational
            if any(gate.startswith(g) for g in PUBLICATION_GATES):
                seen_gates.add(next(g for g in PUBLICATION_GATES if gate.startswith(g)))
                if status in {"BLOCK", "FAIL"} or block_flag:
                    blocked.append(f"{gate} {status or 'BLOCK'}")
        missing_gates = [g for g in PUBLICATION_GATES if g not in seen_gates]
        if missing_gates:
            return False, [
                f"HENRY_AUDIT.json: missing publication gates {missing_gates}. "
                f"All of G29-G33 must be evaluated."
            ]
        if blocked:
            return False, [f"Henry blocks publication: {blocked}"]
        reasons.append(f"henry: all {len(PUBLICATION_GATES)} publication gates PASS")

        # 4. Consent attestation for real_patient
        data_source = str(manifest.get("data_source") or "")
        if data_source == "real_patient":
            if "ethics_declaration.md" not in names_in_zip:
                return False, [
                    "real_patient bundle must include ethics_declaration.md"
                ]
            ethics = zf.read("ethics_declaration.md").decode("utf-8", errors="replace")
            if CANONICAL_CONSENT not in _norm(ethics):
                return False, [
                    "real_patient bundle ethics_declaration.md is missing "
                    "the canonical consent attestation. The exact phrase "
                    f"required (case-insensitive): \"{CANONICAL_CONSENT}\""
                ]
            reasons.append("consent: canonical attestation present")
        else:
            reasons.append(f"consent: not required ({data_source})")

        return True, reasons
    finally:
        zf.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an N1Arxiv submission .n1a bundle.")
    parser.add_argument("bundle", type=Path, help="Path to the .n1a.zip bundle.")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print refusal reasons; success is silent (CI mode).",
    )
    args = parser.parse_args()

    accept, reasons = validate_bundle(args.bundle)
    if accept:
        if not args.quiet:
            print(f"OK — {args.bundle}")
            for r in reasons:
                print(f"  - {r}")
        return 0
    print(f"REFUSED — {args.bundle}", file=sys.stderr)
    for r in reasons:
        print(f"  - {r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
