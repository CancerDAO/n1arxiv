# N1Arxiv

> **N=1 reports are not clinical guidance.**

**N1Arxiv** is a patient-centered preprint platform for AI-team-authored
**N-of-1** case reports. Each paper is the public artifact of a single
patient's session with [OPL for Cancer](https://github.com/CancerDAO/opl-cancer)
(or any other agent that emits a v0.1-compliant `.n1a` bundle).

This repo is the platform itself: a Hugo static site + JSON Schema +
CI submission gates. There is no backend, no account, and no login.
The only state is the public git history.

- **Domain**: `n1arxiv.cancerdao.org` (GitHub Pages, default)  ·  `n1arxiv.org` (placeholder, not yet registered)
- **License**: dual — CC-BY 4.0 for `content/` + `static/`; MIT for `layouts/` + `scripts/` + `tests/` + `.github/`. See [LICENSE](LICENSE).
- **Schema**: `schemas/n1a_bundle.v0.1.schema.json` (mirror of [`CancerDAO/opl-cancer`](https://github.com/CancerDAO/opl-cancer/blob/main/schemas/n1a_bundle.v0.1.schema.json) — any change is a two-PR change).

## Why N=1?

Single-subject ("N-of-1") trials are a recognised study design in
medicine, especially for rare diseases, refractory cases, and
mechanism-of-resistance work. They are not population-scale evidence;
they are rigorous single-subject science. N1Arxiv is the publication
surface for that kind of work — including reports authored
primarily by AI teams under patient direction.

## Submission flow

You produce a `.n1a` bundle by running OPL's Wave 6:

```bash
opl wave6 --patient-dir <PATH> --run-id <ID> --patient-code <CODE> \
    --final \
    --submit-to-n1arxiv \
    --n1arxiv-repo /path/to/your/clone/of/n1arxiv
```

The OPL submitter stages two files inside your clone:

- `static/bundles/<paper_id>.n1a.zip` — the bundle, byte-exact
- `content/papers/<paper_id>.md` — the Hugo content stub

It then prints a PR body draft and the suggested `gh pr create` command.
**The submitter never pushes for you.** Founder mode: the patient is
the sole entity that pushes to the public PR surface.

Step-by-step: see [docs/submission_guide.md](docs/submission_guide.md).

## What CI checks

Every PR touching `static/bundles/**` or `content/papers/**` runs
[`scripts/validate_bundle.py`](scripts/validate_bundle.py) which:

1. Unzips the bundle and validates `manifest.json` against the schema
2. Re-computes SHA-256 for every file listed in `file_index` and refuses
   on any mismatch (no silent corruption)
3. Reads `HENRY_AUDIT.json`; refuses on any G29-G33 = FAIL/BLOCK
4. For `data_source: real_patient`, requires the canonical consent
   attestation string in `ethics_declaration.md`

A maintainer then reviews for content sanity (banner is intact, N=1
framing is consistent) before merging. On merge, `build_site.yml`
runs Hugo and publishes to `gh-pages`.

## Ethics

- Patient identity is **hashed**. The `patient_id_hash` is short,
  one-way, and meaningless without the original `patient_code` which
  never leaves the patient's machine.
- Non-`real_patient` bundles (`reference_case`, `methodology_demo`,
  `synthetic`) are banner-stamped in the manuscript and on the
  content stub front matter.
- AI authorship is disclosed CRediT-style in every bundle's
  `ai_authorship_disclosure.md`. See [docs/ai_authorship_policy.md](docs/ai_authorship_policy.md).
- The patient may **withdraw** a paper at any time. The bundle is
  removed; the content stub is preserved as `[WITHDRAWN_BY_PATIENT]`.
  See [docs/n1_ethics.md](docs/n1_ethics.md).
- N=1 reports are **not** clinical guidance. The site banner
  reiterates this on every page.

## Local development

```bash
# Validate a bundle locally
python scripts/validate_bundle.py static/bundles/<paper_id>.n1a.zip

# Build the site (requires Hugo ≥ 0.110)
hugo --gc --minify

# Run the test suite
pip install -r requirements-dev.txt
pytest -q
```

The Hugo build test (`tests/test_hugo_build.py`) is gated on
`which hugo`; contributors without Hugo installed can still run the
schema + CI-refusal tests.

## See also

- [`CancerDAO/opl-cancer`](https://github.com/CancerDAO/opl-cancer) —
  the AI scientist team that produces `.n1a` bundles
- [ADR-0024 in opl-cancer](https://github.com/CancerDAO/opl-cancer/blob/main/docs/adr/0024-n1arxiv-platform-skeleton.md) —
  cross-repo design rationale
