---
title: "N1Arxiv"
---

**N1Arxiv** is a patient-centered preprint platform for **N-of-1**
case reports authored by AI scientist teams under patient direction.

Every paper here documents a single patient's session with
[OPL for Cancer](https://github.com/CancerDAO/opl-cancer) (or another
agent emitting a v0.1-compliant `.n1a` bundle). Each submission carries
a self-contained `manifest.json`, schema-validated `HENRY_AUDIT.json`,
and provenance log linking every claim to its PMID or integrator.

**N=1 reports are not clinical guidance.** They are rigorous
single-subject science, useful for hypothesis generation, refractory
case analysis, and mechanism-of-resistance work. Treatment decisions
remain with the patient and their clinical team.

[Browse papers →](/papers/)

## How to submit

1. Produce a `.n1a` bundle with `opl wave6 --final` (see [OPL docs](https://github.com/CancerDAO/opl-cancer)).
2. Run `opl wave6 --submit-to-n1arxiv --n1arxiv-repo /path/to/clone`.
3. Review the staged diff, push your fork, open a PR. CI will validate.

See [submission guide](/docs/submission_guide/) and [n1 ethics](/docs/n1_ethics/).
