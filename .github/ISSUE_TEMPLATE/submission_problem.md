---
name: Submission problem
about: Use this if your PR was refused by CI or you hit a snag while submitting.
title: "[Submission] "
labels: submission-help
---

## What happened

<!-- describe the error or refusal you saw -->

## Bundle paper_id (if known)

`<YYYY-MM-DD-slug>`

## OPL version that produced the bundle

`<2.4.0 or other>`

## CI log link (if relevant)

<!-- paste a link to the failed workflow run -->

## What you tried

- [ ] Re-ran `python scripts/validate_bundle.py <bundle>` locally
- [ ] Verified `manifest.json` is the unmodified one from Wave 6
- [ ] Checked that `HENRY_AUDIT.json` has all G29-G33 results
- [ ] For `real_patient`: verified `ethics_declaration.md` carries the canonical consent string
