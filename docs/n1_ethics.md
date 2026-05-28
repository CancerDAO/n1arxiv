---
title: "N=1 ethics"
---

# N=1 ethics — how N1Arxiv handles consent, identity, and withdrawal

N1Arxiv publishes case reports written by AI scientist teams under
patient direction. The ethics framing below is the platform's
operational stance; it is not legal advice.

## Patient is the sole decision authority

Founder mode (per OPL for Cancer's design philosophy): no human-in-
the-loop external sign-off is required for the patient to publish
their own case. Likewise, no agent or maintainer publishes on the
patient's behalf without their explicit action. The OPL submitter
never auto-PRs; the patient pushes. The maintainer reviews for
**framing sanity**, not for **clinical sign-off**.

## Consent attestation

For `data_source: real_patient` bundles, the bundle's
`ethics_declaration.md` must contain the canonical consent string
(case-insensitive, whitespace-collapsed):

> **The patient has provided informed consent for this N=1 case
> report to be published on N1Arxiv.**

CI refuses real_patient PRs missing this attestation. The attestation
must be made by the patient (or their legal representative); a
caregiver-only attestation does not suffice.

## Identity hashing

The bundle's `manifest.json` stores `patient_id_hash` — a SHA-256
prefix of the raw `patient_code`. The raw `patient_code` never leaves
the patient's machine. The content stub renders the hash, not the
code. Inferring a real patient from the hash + cancer-type + date
combination is the failure mode we worry about; submitters should
review their bundle's manuscript for inadvertent
quasi-identifier combinations (≥3 of: hospital name, cancer subtype,
treatment dates, geographic region) and redact before submission.

## Banner enforcement

Non-`real_patient` bundles (`reference_case`, `methodology_demo`,
`synthetic`) are banner-stamped at three layers:

1. Inside the bundle, at the top of `manuscript.md`
2. In the Hugo content stub's front matter (`banner: "…"`)
3. Rendered on the site detail page via the `banner` template

Stripping the banner during submission is grounds for refusal at
maintainer review.

## AI authorship

Every bundle's `ai_authorship_disclosure.md` lists each contributing
expert and attests "no human author beyond patient & supervising
clinician." The Henry G29 gate refuses bundles where this disclosure
is missing or incomplete. See
[`docs/ai_authorship_policy.md`](ai_authorship_policy.md).

## Not clinical guidance

The site renders the banner **"N=1 reports are not clinical
guidance"** on every page. This is not boilerplate; it is the
operational stance. Readers seeking treatment guidance should not
treat these papers as decision-grade evidence.

## Withdrawal

Patients may withdraw a paper at any time. The withdrawal flow:

1. Open a withdrawal-request issue (or contact a maintainer directly)
2. The bundle file `static/bundles/<paper_id>.n1a.zip` is **removed**
3. The content stub `content/papers/<paper_id>.md` is **preserved**
   with the body replaced by:

   ```
   ---
   title: "[WITHDRAWN_BY_PATIENT]"
   withdrawn: true
   ---

   This paper was withdrawn by the patient. The bundle has been
   removed. Citations to this paper_id should be updated.
   ```

4. The content stub remains so existing citations don't 404; this
   honours both the patient's withdrawal and the citing community.

Git history is preserved. v0.1 does not attempt bit-erasing takedown
via `git filter-branch` — this is an honest limit of git as a public
publication surface. A future v0.2 may add a curated "removed
bundles" registry if the community needs stronger guarantees.

## Caveats

- N1Arxiv is **not** a regulatory submission surface. Publishing here
  does not constitute IND/IDE/IRB documentation.
- AI-authored content can hallucinate. The Henry G29-G33 gates inside
  each bundle exist precisely to mitigate this; reviewers should still
  read the content critically.
- The maintainer review is not a peer review. It is a framing-sanity
  check (banner intact, N=1 language consistent, no obvious PHI).
  Substantive scientific review is left to the open-science community
  via post-publication comments (issues, citing PRs).
