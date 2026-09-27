# Phase 2 - DEV Ground Truth Annotation

This directory contains the fixed 24-page development Ground Truth subset.

## Scope

- selected pages: 24
- coverage pages: 19
- challenge pages: 5
- final validation pages are intentionally excluded

## Annotation source

`dev_annotations.jsonl` contains one scaffold record per selected page.

Annotate the `rows[*]` objects only.

For each row:
- `active=true` when the row contains report data.
- `active=false` when the row is blank and should not produce OCR data.
- Keep blank/unreadable field values as `null`.
- Preserve Vietnamese diacritics, capitalization, digits, punctuation and visible technical codes.
- Do not infer or normalize business meaning.

## Canonical OCR fields

```text
stt
date
order_code
drawing_code
work_code
target_time
start_time
end_time
total_time
processed_qty
good_qty
ng_qty
process_detail
note
```
### Page-level total time

When a page shows a page-level total for the `total_time` column, it represents
the sum of `total_time` across that page's rows (rows 1..20).

The page-level total is not stored inside `rows[*].ground_truth`.

## Separation rule

This DEV set is for development/debugging only.
Do not use these same pages as the final Phase 9 validation set.

## Selected pages

01. 1207 / T1 / page 003 / coverage / coverage:dense
02. 1207 / T2 / page 004 / coverage / coverage:dense
03. 1207 / T3 / page 005 / coverage / coverage:medium_dense
04. 1207 / T4 / page 006 / coverage / coverage:dense
05. 1236 / T1 / page 004 / coverage / coverage:dense
06. 1236 / T2 / page 002 / coverage / coverage:medium_dense
07. 1236 / T3 / page 004 / coverage / coverage:dense
08. 1236 / T4 / page 006 / coverage / coverage:dense
09. 1263 / T1 / page 002 / coverage / coverage:medium_dense
10. 1263 / T2 / page 004 / coverage / coverage:dense
11. 1263 / T3 / page 004 / coverage / coverage:dense
12. 1263 / T4 / page 006 / coverage / coverage:medium_dense
13. 1570 / T1 / page 002 / coverage / coverage:dense
14. 1570 / T2 / page 002 / coverage / coverage:dense
15. 1570 / T3 / page 002 / coverage / coverage:dense
16. 1575 / T1 / page 005 / coverage / coverage:dense
17. 1575 / T2 / page 004 / coverage / coverage:dense
18. 1575 / T3 / page 002 / coverage / coverage:medium_dense
19. 1575 / T4 / page 006 / coverage / coverage:dense
20. 1207 / T3 / page 001 / challenge / challenge:high_density
21. 1236 / T2 / page 001 / challenge / challenge:highlighted_dense
22. 1263 / T3 / page 001 / challenge / challenge:high_density
23. 1570 / T1 / page 003 / challenge / challenge:high_density
24. 1575 / T3 / page 001 / challenge / challenge:high_density
