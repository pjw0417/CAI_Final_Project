# MINT math pilot report

Answers are regraded in memory with the current pilot extractor. Source JSONL files are unchanged.

## max_token_2048_1_task.jsonl

Tasks: **1** · Model: openai/gpt-oss-20b · Output limit: 2048 tokens per call

| Stage | Calls | Correct | Incorrect | Unscored | Hit limit | Tokens p50 / p95 / max | Total tokens | Mean seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial | 1 | 1 | 0 | 0 | 0 | 1,404 / 1,404 / 1,404 | 1,404 | 4.63 |
| Generic review | 1 | 1 | 0 | 0 | 0 | 335 / 335 / 335 | 335 | 1.07 |

**Initial → review outcomes:** correct → correct: 1

Review changed the extracted answer on **0** task(s).

**Tasks to inspect:** 0

| Task | Initial | Review | Initial tokens | Review tokens |
| ---: | --- | --- | ---: | ---: |

Correctness is provisional exact numeric scoring. Unscored answers are excluded from graded accuracy; tasks that hit the limit remain in the attempted-task denominator. Review results cover only tasks where a review call occurred.

## max_token_2048_20_tasks.jsonl

Tasks: **20** · Model: openai/gpt-oss-20b · Output limit: 2048 tokens per call

| Stage | Calls | Correct | Incorrect | Unscored | Hit limit | Tokens p50 / p95 / max | Total tokens | Mean seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial | 20 | 11 | 0 | 9 | 9 | 1,687 / 2,048 / 2,048 | 31,181 | 4.93 |
| Generic review | 14 | 14 | 0 | 0 | 0 | 394 / 924 / 947 | 6,966 | 1.58 |

**Initial → review outcomes:** correct → correct: 11; unscored → correct: 3; unscored → skipped: 6

Review changed the extracted answer on **3** task(s).

| Task | Initial | Review | Initial grade → review grade |
| ---: | --- | --- | --- |
| 10 | `` | `11` | unscored → correct |
| 15 | `` | `2` | unscored → correct |
| 18 | `` | `6` | unscored → correct |

**Tasks to inspect:** 9

| Task | Initial | Review | Initial tokens | Review tokens |
| ---: | --- | --- | ---: | ---: |
| 2 | unscored (limit) | skipped | 2048 | — |
| 5 | unscored (limit) | skipped | 2048 | — |
| 7 | unscored (limit) | skipped | 2048 | — |
| 8 | unscored (limit) | skipped | 2048 | — |
| 9 | unscored (limit) | skipped | 2048 | — |
| 10 | unscored (limit) | correct | 2048 | 804 |
| 15 | unscored (limit) | correct | 2048 | 866 |
| 18 | unscored (limit) | correct | 2048 | 604 |
| 19 | unscored (limit) | skipped | 2048 | — |

Correctness is provisional exact numeric scoring. Unscored answers are excluded from graded accuracy; tasks that hit the limit remain in the attempted-task denominator. Review results cover only tasks where a review call occurred.

## max_token_4096_20_tasks.jsonl

Tasks: **20** · Model: openai/gpt-oss-20b · Output limit: 4096 tokens per call

| Stage | Calls | Correct | Incorrect | Unscored | Hit limit | Tokens p50 / p95 / max | Total tokens | Mean seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial | 20 | 17 | 0 | 3 | 3 | 1,687 / 4,096 / 4,096 | 39,806 | 6.34 |
| Generic review | 17 | 17 | 0 | 0 | 0 | 514 / 1,154 / 1,176 | 10,278 | 1.94 |

**Initial → review outcomes:** correct → correct: 17; unscored → skipped: 3

Review changed the extracted answer on **0** task(s).

**Tasks to inspect:** 3

| Task | Initial | Review | Initial tokens | Review tokens |
| ---: | --- | --- | ---: | ---: |
| 5 | unscored (limit) | skipped | 4096 | — |
| 7 | unscored (limit) | skipped | 4096 | — |
| 8 | unscored (limit) | skipped | 4096 | — |

Correctness is provisional exact numeric scoring. Unscored answers are excluded from graded accuracy; tasks that hit the limit remain in the attempted-task denominator. Review results cover only tasks where a review call occurred.

## max_token_6144_100_tasks.jsonl

Tasks: **100** · Model: openai/gpt-oss-20b · Output limit: 6144 tokens per call

| Stage | Calls | Correct | Incorrect | Unscored | Hit limit | Tokens p50 / p95 / max | Total tokens | Mean seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial | 100 | 86 | 0 | 14 | 9 | 1,050 / 6,144 / 6,144 | 177,971 | 5.78 |
| Generic review | 91 | 87 | 0 | 4 | 1 | 382 / 1,454 / 6,144 | 53,592 | 1.90 |

**Initial → review outcomes:** correct → correct: 85; correct → unscored: 1; unscored → correct: 2; unscored → skipped: 9; unscored → unscored: 3

Review changed the extracted answer on **6** task(s).

| Task | Initial | Review | Initial grade → review grade |
| ---: | --- | --- | --- |
| 33 | `7\%` | `7%` | unscored → unscored |
| 36 | `` | `128` | unscored → correct |
| 59 | `30^\circ` | `30°` | unscored → unscored |
| 62 | `24` | `` | correct → unscored |
| 64 | `160\text{ meters}` | `160` | unscored → correct |
| 89 | `\frac{175}{2}` | `175/2` | unscored → unscored |

**Tasks to inspect:** 15

| Task | Initial | Review | Initial tokens | Review tokens |
| ---: | --- | --- | ---: | ---: |
| 5 | unscored (limit) | skipped | 6144 | — |
| 7 | unscored (limit) | skipped | 6144 | — |
| 8 | unscored (limit) | skipped | 6144 | — |
| 33 | unscored | unscored | 434 | 136 |
| 36 | unscored | correct | 608 | 196 |
| 56 | unscored (limit) | skipped | 6144 | — |
| 59 | unscored | unscored | 2449 | 887 |
| 62 | correct | unscored (limit) | 5654 | 6144 |
| 64 | unscored | correct | 5709 | 701 |
| 67 | unscored (limit) | skipped | 6144 | — |
| 75 | unscored (limit) | skipped | 6144 | — |
| 85 | unscored (limit) | skipped | 6144 | — |
| 89 | unscored | unscored | 2222 | 344 |
| 90 | unscored (limit) | skipped | 6144 | — |
| 97 | unscored (limit) | skipped | 6144 | — |

Correctness is provisional exact numeric scoring. Unscored answers are excluded from graded accuracy; tasks that hit the limit remain in the attempted-task denominator. Review results cover only tasks where a review call occurred.

## Across runs

| Run | Tasks | Initial correct / attempted | Initial hit limit | Review correct / calls |
| --- | ---: | ---: | ---: | ---: |
| max_token_2048_1_task.jsonl | 1 | 1/1 | 0 | 1/1 |
| max_token_2048_20_tasks.jsonl | 20 | 11/20 | 9 | 14/14 |
| max_token_4096_20_tasks.jsonl | 20 | 17/20 | 3 | 17/17 |
| max_token_6144_100_tasks.jsonl | 100 | 86/100 | 9 | 87/91 |

Runs may use different task counts or token limits. Compare accuracy only on the same tasks with the same scoring rule; this table is descriptive.
