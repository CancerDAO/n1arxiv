---
title: "FAQ"
---

# Frequently asked questions

## Is this peer-reviewed?

No. N1Arxiv is a **preprint** platform. CI checks structural
invariants (schema, hashes, Henry G29-G33 gates, consent attestation
for real_patient). A human maintainer reviews for framing sanity. No
substantive peer review happens before merge. Post-publication
review is via issues and citing PRs.

## Can I cite a paper here in a journal article?

Yes — like any preprint, with the caveat that the work has not been
peer-reviewed. Use the citation block at the bottom of each paper
detail page.

## Why is the manuscript not on the detail page?

The detail page is a stub. The manuscript lives inside the `.n1a`
bundle, which carries the manuscript + provenance + audit + figures
+ reproducibility in one self-contained artifact. Downloading the
bundle gives you everything; the stub avoids drift between bundle
and site.

## What if a paper is wrong?

Open an issue against the paper. The site is small enough that
maintainers will see it. If the error is severe, the patient may
withdraw or update the paper (a second PR with a v2 of the bundle).

## Can a patient organisation or research group submit instead of an
individual patient?

The patient (or their legal representative) is the sole decision
authority. A group can help prepare the bundle, but the PR is opened
under the patient's account (or with the patient's explicit
attestation in `ethics_declaration.md`).

## What does "founder mode" mean?

It means the patient acts as their own PI. They direct the
investigation, they approve publication, they retain withdrawal
rights. The platform's job is to make that easy without inserting
gatekeepers. See [`docs/n1_ethics.md`](n1_ethics.md).

## Do you have a DOI?

Not in v0.1. The `paper_id` (`YYYY-MM-DD-<slug>`) is the canonical
identifier; the GitHub permalink is the durable URL. DOI registration
(CrossRef / DataCite) is on the v0.2 roadmap.

## Where does the schema live?

The **canonical** schema is in [`CancerDAO/opl-cancer`](https://github.com/CancerDAO/opl-cancer/blob/main/schemas/n1a_bundle.v0.1.schema.json).
This repo ships a byte-identical **mirror** at `schemas/n1a_bundle.v0.1.schema.json`.
Any schema change is a two-PR change (opl-cancer + n1arxiv in lockstep).

## How do I run the validator locally?

```bash
python scripts/validate_bundle.py static/bundles/<paper_id>.n1a.zip
```

The validator is in MIT-licensed code and has no dependency on OPL
itself — you only need `jsonschema` (pip-installable).
