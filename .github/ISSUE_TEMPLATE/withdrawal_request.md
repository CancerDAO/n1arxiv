---
name: Withdrawal request
about: Use this to withdraw your N=1 case report from N1Arxiv. Patients are the sole decision authority.
title: "[Withdrawal] "
labels: withdrawal
---

## Paper to withdraw

paper_id: `<YYYY-MM-DD-slug>`

## Who is making this request

<!-- patient / legal representative / supervising clinician acting on behalf of patient -->

## Reason (optional)

<!-- You are not required to give a reason. If you choose to, it
helps the maintainer team improve the platform. -->

## Confirmation

- [ ] I am the patient (or their legal representative) named in
      `manifest.json` of the bundle for this paper_id.
- [ ] I understand that the bundle file will be **removed** but the
      content stub will be **preserved** as `[WITHDRAWN_BY_PATIENT]`
      to avoid breaking citations.
- [ ] I understand that git history is **preserved** (this is a
      public surface; bit-erasing takedown is not attempted in v0.1).

A maintainer will action this within a few days and reply on this
issue when the withdrawal PR is merged.
