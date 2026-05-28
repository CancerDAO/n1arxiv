"""Schema sanity — validates every seed bundle in static/bundles/.

The schema in this repo is a mirror of the canonical schema in
`CancerDAO/opl-cancer`. This test fails if a seed bundle has drifted
from the schema, which is the early-warning signal we want.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((REPO / "schemas" / "n1a_bundle.v0.1.schema.json").read_text(encoding="utf-8"))
BUNDLES_DIR = REPO / "static" / "bundles"


@pytest.fixture(scope="module")
def schema() -> dict:
    return SCHEMA


def test_schema_is_draft_2020_12(schema: dict) -> None:
    assert schema["$schema"].endswith("2020-12/schema"), schema["$schema"]


def test_schema_required_keys(schema: dict) -> None:
    required = set(schema["required"])
    assert {
        "schema_version",
        "opl_version",
        "patient_id_hash",
        "generated_at",
        "data_source",
        "file_index",
        "sha256s",
    }.issubset(required)


def test_schema_data_source_enum(schema: dict) -> None:
    enum = set(schema["properties"]["data_source"]["enum"])
    assert {"real_patient", "reference_case", "synthetic", "methodology_demo"}.issubset(enum)


def _all_bundles() -> list[Path]:
    return sorted(BUNDLES_DIR.glob("*.n1a.zip"))


def test_every_seed_bundle_validates(schema: dict) -> None:
    bundles = _all_bundles()
    assert bundles, "no seed bundles found under static/bundles/"
    for b in bundles:
        with zipfile.ZipFile(b) as zf:
            assert "manifest.json" in zf.namelist(), f"{b}: missing manifest.json"
            manifest = json.loads(zf.read("manifest.json"))
        jsonschema.validate(instance=manifest, schema=schema)


def test_canonical_mirror_marker_in_description(schema: dict) -> None:
    """Drift-detection nudge: the description should name itself as the mirror."""
    desc = schema.get("description", "")
    assert "MIRROR COPY" in desc.upper() or "CANONICAL" in desc.upper(), desc
