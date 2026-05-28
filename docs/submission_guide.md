---
title: "Submission guide"
---

# How to submit an N=1 case report

N1Arxiv accepts submissions as **`.n1a` bundles** (schema v0.1). The
typical author runs [OPL for Cancer](https://github.com/CancerDAO/opl-cancer)
to produce the bundle; other agents emitting v0.1-compliant bundles
work too.

## Step 1 — Produce the bundle

```bash
opl wave6 \
    --patient-dir /path/to/patient \
    --run-id <RUN_ID> \
    --patient-code <CODE> \
    --final \
    --data-source {real_patient|reference_case|methodology_demo|synthetic}
```

This produces `<id>_<date>.n1a.zip` inside your run directory, plus a
matching `manifest.json` and `HENRY_AUDIT.json`. The bundle is
self-validating: the writer refuses to ship if `manuscript.md`,
`ai_authorship_disclosure.md`, `reproducibility.md`, or
`HENRY_AUDIT.json` are missing.

## Step 2 — Stage against your fork

```bash
opl wave6 \
    --patient-dir /path/to/patient \
    --run-id <RUN_ID> \
    --patient-code <CODE> \
    --final \
    --submit-to-n1arxiv \
    --n1arxiv-repo /path/to/your/clone/of/n1arxiv
```

This:

1. Reads `manifest.json` from the just-built bundle
2. Derives `paper_id = <YYYY-MM-DD>-<slug-of-patient-code>`
3. Byte-copies the bundle into `static/bundles/<paper_id>.n1a.zip`
4. Writes a Hugo content stub into `content/papers/<paper_id>.md`
5. Prints the PR body draft and suggested git/gh commands

**The submitter never pushes for you.** Founder mode: the patient is
the sole entity that pushes to the public PR surface.

## Step 3 — Review the staged diff locally

```bash
cd /path/to/your/clone/of/n1arxiv
git status
git diff content/papers/<paper_id>.md
```

Read the content stub. Verify:

- The banner (if non-`real_patient`) is present in the front matter
- The `patient_id_hash` is opaque (never the raw patient_code)
- No accidental PHI slipped past the bundle's redaction layer

## Step 4 — Open the PR

```bash
git checkout -b submit/<paper_id>
git add static/bundles/<paper_id>.n1a.zip content/papers/<paper_id>.md
git commit -m "Submit <paper_id>"
git push -u origin HEAD
gh pr create --base main --title "Submit <paper_id>"
```

Paste the PR body draft (printed by step 2) into the PR description.

## Step 5 — CI runs

`.github/workflows/validate_submission.yml` invokes
`scripts/validate_bundle.py`, which:

1. Validates `manifest.json` against the schema
2. Re-computes SHA-256 for every file in `file_index` (no silent
   corruption)
3. Reads `HENRY_AUDIT.json`; refuses on any G29-G33 = FAIL/BLOCK
4. For `data_source: real_patient`, requires the canonical consent
   attestation string in `ethics_declaration.md`:

   > **The patient has provided informed consent for this N=1 case
   > report to be published on N1Arxiv.**

   (Case-insensitive, whitespace-collapsed. Must be present verbatim.)

## Step 6 — Maintainer review

A human maintainer reviews:

- Banner is intact in the manuscript header AND content stub
- N=1 framing language is consistent
- No identifying details slipped past the patient_id_hash
- The bundle file is the same hash CI verified (defensive sanity)

On merge, `build_site.yml` runs Hugo and publishes to `gh-pages`.

## Withdrawal

Open an issue using the "Withdrawal request" template (or open one
manually). The bundle file is removed; the content stub is preserved
with the body replaced by `[WITHDRAWN_BY_PATIENT]`. Git history is
preserved (this is a public surface; bit-erasing takedown is not
attempted in v0.1). See [`docs/n1_ethics.md`](n1_ethics.md).
