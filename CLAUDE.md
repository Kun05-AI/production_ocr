# Production OCR — CLAUDE.md

## Project Goal

Build the complete production OCR system for handwritten manufacturing forms.

Repository:

`D:\production_ocr`

This is a Windows-local project.

Claude must work all the way to the final production product.

---

## Core Rule

**Inspect first. Verify second. Act third.**

Never assume that previous conversation, old documentation, previous test
results, previous assistant output, or remembered architecture matches the
current repository.

Always verify the actual files/code/config/tests/artifacts.

---

## Approval Gates

Claude may autonomously make small, local, reversible changes that do not
change any project contract.

Claude MUST STOP AND ASK before:

- architecture changes,
- schema changes,
- dataset/sample-selection changes,
- DEV/validation split changes,
- dependency installation/removal/version changes,
- destructive operations,
- deletion,
- overwrite/regeneration,
- changes to project-defining requirements,
- changes to phase acceptance criteria,
- changes to project-defining documentation.

When approval is required:

1. Explain what was found.
2. Explain the proposed change.
3. Explain why.
4. List affected files/data.
5. Explain impact.
6. Ask the user.
7. Wait.

Do not proceed without approval.

---

## Ambiguity

Never guess.

If two interpretations are possible, ask the user.

If the repository contradicts the documentation, report the contradiction.

If the user answer still leaves ambiguity, ask again.

---

## Double Check

Every meaningful change follows:

Inspect
→ Plan
→ Ask when necessary
→ Implement
→ Test
→ Inspect actual artifacts
→ Compare with requirements
→ Find gaps
→ Fix
→ Re-test
→ Re-inspect
→ Report

Claude must check its own work and the user must be able to review it.

---

## Phase Completion

Exit code 0 is not Phase PASS.

Unit test PASS is not automatically Phase PASS.

A numerical metric passing is not enough if the actual artifact is wrong.

A phase may only be marked complete after:

- requirements reviewed,
- required artifacts exist,
- tests pass,
- actual output inspected,
- visual checks performed when relevant,
- data integrity verified,
- no unresolved blocking issue remains.

---

## Roadmap — Version 3

P0 Requirement Freeze  
P1 Runtime + Qwen  
P2 Ground Truth Dataset  
P3 Input Engine  
P4 Image Normalization  
P5 Form Registry + Baseline Registration  
P6 Generic Registration + Segmentation  
P7 Qwen OCR  
P8 Validation + Confidence  
P9 Accuracy Evaluation  
P10 Excel Sheet 05  
P11 Telegram QC  
P12 n8n Integration  
P13 Production Hardening

Important:

- Ground Truth = P2.
- Registration = P5.
- Segmentation = P6.
- Accuracy Evaluation = P9.

Do not move Ground Truth back to the old Phase 8.

---

## Baseline-First

Current form:

`T1/v1`

Start simple.

Do not add generic architecture merely for hypothetical future forms.

Only generalize when justified by:
- a real new form,
- a verified limitation,
- or a production requirement.

---

## Current Corpus

19 PDFs.

143 pages.

5 members.

T1/T2/T3/T4 are week/document instances, not form IDs.

All current PDFs use the same current form layout.

Current form profile:

`T1/v1`

---

## Current DEV Ground Truth

24 pages.

19 coverage pages + 5 challenge pages.

This selection is currently frozen.

If visual inspection suggests the selection is inadequate:

- report evidence,
- identify the issue,
- ASK the user,
- do not change the selection automatically.

DEV Ground Truth must remain separate from final validation Ground Truth.

---

## OCR Row Schema

```text
stt
date
order_code
drawing_code
revision
work_code
target_time
start_time
end_time
processed_qty
good_qty
ng_qty
process_detail
note