---
title: "AI authorship policy"
---

# AI authorship — CRediT for AI contributors

N1Arxiv accepts papers where the **primary authors are AI experts**.
This is not a hedge or a curiosity exemption; it is the platform's
design centre. The patient directs the work; the AI team writes the
report. We expect this authorship model to become a norm in N=1
research.

## CRediT mapping

Every bundle includes `ai_authorship_disclosure.md`, which lists each
contributing expert against the [CRediT](https://credit.niso.org/)
contributor-role taxonomy:

| CRediT role | Typical OPL expert(s) |
| --- | --- |
| Conceptualization | Patient (records the goal); Iain (literature framing) |
| Methodology | Aviv (study design); Vince (analysis plan) |
| Software | Bert (NGS interpretation); Aviv (statistics) |
| Validation | Henry (audit); reviewer-pairing agents |
| Formal analysis | Aviv; Bert; Maya (synergy) |
| Investigation | Iain (Wave 1 retrieval); Frances (regulatory) |
| Resources | Rick (clinical trial registry); Dennis (cross-border) |
| Data curation | Rosa (records OCR) |
| Writing — original draft | Iain (intro); Aviv (results); Vince (discussion) |
| Writing — review & editing | Henry (audit); Frances (ethics framing) |
| Visualization | Aviv (figures); Mary (palliative tradeoffs) |
| Supervision | Sid (PI) |
| Project administration | Sid |
| Funding acquisition | Patient (self-funded by definition) |

A bundle whose `ai_authorship_disclosure.md` lacks the contribution
table fails Henry G29 and is refused at CI.

## What the policy does NOT do

- It does not require a human co-author. Many N=1 patients have no
  collaborator beyond their AI team.
- It does not require institutional affiliation. The patient is the
  affiliation.
- It does not require IRB approval. Single-subject self-experimentation
  has long-standing precedent in critical-care and rare-disease research.
- It does not require pre-registration. (A future v0.2 may add an
  opt-in pre-registration surface.)

## What the policy DOES require

- The supervising clinician (if any) is named in
  `ai_authorship_disclosure.md` — even if their role is "consulted
  but did not author".
- Every claim in `manuscript.md` is anchored either to a PMID or to
  an integrator call (G30). LLM-generated prose without anchors is
  blocked.
- The AI model identities are recorded in `reproducibility.md` (which
  OPL version, which LLM models, which integrator versions). This is
  the AI-equivalent of "methods section".

## Future work

- A CRediT-aware front-end widget on the paper detail page (v0.2)
- Cross-paper expert citation graph — see how often Aviv or Bert
  contributed across the corpus (v0.2)
- A formal "AI-author identity" schema beyond `expert_name: role`
  pairs (v0.3)
