# Project Experiment Plan

## Goal

Test whether `gpt-oss-20b` solves more problems when a fixed generation-token allowance is split between an initial answer and a revision after feedback. Use the same problems and total allowance for every condition.

## How we will use MINT

MINT will provide the problems and reference answers. We will start with its math subset, then consider coding tasks for the full project. We will **not modify MINT's core evaluation loop** for the first experiment. Instead, we will keep the cloned repository as a benchmark source and write our own small runner for the exact two-call sequence and token splits in the proposal. We will reuse or adapt its answer checker after auditing it; any scoring changes will live in our code and be documented. This keeps our results reproducible and avoids mixing tool use or extra turns into the fixed-budget comparison.

## Experiment sequence

The natural-behavior pilot comes first. The proposal then has **three controlled experiments**:

| Stage | Comparison | Main question |
| --- | --- | --- |
| Pilot | No feedback, then optional generic review on a small task set | How long does the model naturally reason, when does it stop, and what kinds of mistakes can revision fix? |
| Experiment 1 | Informative feedback with 75/25, 50/50, and 25/75 initial/revision token splits | Which allocation gives the highest final accuracy at the same total allowance? |
| Experiment 2 | Informative feedback vs. generic review, both starting from the **same saved 50/50 initial answers** | Does external error information help beyond asking the model to check itself? |
| Experiment 3 | 50/50 informative-feedback revision vs. one answer using the full allowance | Is feedback-guided revision better than spending the allowance on one answer? |

For the milestone, use about 20–30 paired MINT math problems and one total allowance chosen from the pilot. For the full project, repeat at multiple allowances and with multiple runs. Add coding problems and up to three feedback rounds only after the two-call design is working and its extra costs can be measured.

## What we will measure

- **Accuracy:** correctness of the first answer and final answer in each condition.
- **Repair and regression:** counts of incorrect-to-correct and correct-to-incorrect changes after revision.
- **Compute:** assigned token limits, actual generated tokens (including reasoning), prompt tokens, runtime, and whether output stopped naturally or hit a limit.
- **Behavior:** whether the model changes its answer, uses the feedback, repeats an error, or produces no scorable final answer.
- **Comparison uncertainty:** paired accuracy differences with 95% paired bootstrap confidence intervals for the full study. Keep per-task results so every comparison uses the same problems.

## Steps

1. **Set up the model on PACE ICE.** Use the shared Hugging Face cache at `/storage/ice1/0/4/lheck6/CS6604_ECE6256/hf_cache`. Confirm the `gpt-oss-20b` checkpoint is present, start vLLM on an allocated GPU node, and save the model and vLLM versions.
2. **Prepare MINT math tasks.** Start with 20–30 problems from `mint-bench/data/processed/math/test_prompts.json`. Keep a fixed list of problem IDs. Use MINT’s reference answers, but audit its answer checker: it accepts numeric answers within 5% of the reference.
3. **Observe natural behavior.** Run each problem once without feedback and with a generous output limit. Record the initial answer, actual generated tokens, whether the model stopped naturally or hit the limit, and correctness. On the same problems, try a generic “review your answer” turn. Inspect several full trajectories to see when revision helps or hurts.
4. **Check the feedback.** For incorrect initial answers, prepare informative feedback that identifies an error without giving away the answer. Manually review a sample for accuracy and answer leakage. Save feedback so the experiment can reuse it.
5. **Run the first controlled comparison.** Choose one total token allowance based on Step 3. Run 75/25, 50/50, and 25/75 initial/revision splits, plus a single-answer baseline with the full allowance. Use the same task IDs and generation settings. Compare informative feedback with generic review using identical saved 50/50 initial answers.
6. **Analyze paired results.** Report initial and final accuracy, actual generated tokens, runtime, incorrect-to-correct repairs, and correct-to-incorrect regressions. Show per-problem paired differences and inspect cases where the conditions disagree.
7. **Expand only after the pilot works.** Add more token allowances, repeated runs, coding tasks, and additional feedback rounds for the full project.

## Files we will need

- **Task selection/configuration:** fixed MINT problem IDs, model and endpoint settings, total allowances, token splits, seeds, and prompts.
- **Model serving instructions or job script:** how to start vLLM on an allocated PACE ICE GPU node using the shared cache.
- **Experiment runner:** sends the initial and revision requests, applies each token limit, and saves full responses plus usage metadata.
- **Feedback generator and review file:** creates and stores informative feedback for each relevant initial answer; records manual checks for errors or answer leakage.
- **Answer extraction and scoring:** converts model replies to final answers and checks them against MINT references using a documented rule.
- **Results and analysis:** machine-readable per-call and per-task records, a script that computes metrics and paired comparisons, and milestone tables or plots. Generated outputs should be kept separate from source code.

## Implementation notes

- MINT’s standard loop includes tool use and variable interaction steps, which would mix other effects into this comparison.
- A token limit is a ceiling, not guaranteed token use. Log actual completion tokens, including reasoning tokens, and whether a response was cut off. Keep any continuation or budget-forcing rule identical across conditions.
- Keep prompts, decoding settings, task IDs, feedback source, and answer extraction rules fixed across paired conditions. Save raw responses and metadata for every call.
- The first milestone is a feasibility result on a small paired math subset, not a claim about all MINT tasks or models.

## Current implementation: natural-behavior pilot

`pilot_math.py` loads the first 100 MINT MATH problems by default, sends each to a local vLLM chat endpoint, and then requests a generic review using the initial response. It writes one JSON record per problem with both raw responses, reasoning text when exposed, finish reasons, token usage, runtime, extracted answers, and provisional correctness. It extracts answers from `<answer>...</answer>` or complete `\boxed{...}` expressions in final response text. Existing JSONL files can be rescored with `python pilot_math.py --rescore INPUT.jsonl --output OUTPUT.jsonl`. It does not generate informative feedback or run the three controlled experiments yet.

On PACE ICE, submit `sbatch run_pilot.sbatch` from this repository. The job uses the shared offline cache and the `CAI_A4` environment from the previous assignment, serves `openai/gpt-oss-20b` with a 16,384-token context limit, and writes output under `results/`. Its default output limit is 6,144 tokens per call. To change the pilot size or output limit, submit `sbatch --export=ALL,PILOT_COUNT=30,MAX_TOKENS=4096 run_pilot.sbatch`.

The pilot's exact numeric scorer is deliberately provisional. A response with no complete tagged or boxed final answer, or a nonnumeric answer, receives `null` correctness for manual review. Before reporting accuracy, audit answer extraction and scoring against the selected MINT tasks. The initial and review calls each have their own `MAX_TOKENS` ceiling, so this pilot is for observing behavior, not a fixed-total-budget comparison.

### What we expect to learn from the pilot

The pilot should tell us whether the model produces a scorable final answer reliably, how many tokens it actually uses before stopping, and how often the 6,144-token ceiling cuts it off. We will inspect whether a generic review repairs wrong answers, changes correct answers to wrong ones, or simply repeats the first answer. These observations help choose a useful total allowance, task subset, and answer-extraction rule for the controlled experiments. We are **not** expecting the pilot to establish that feedback improves accuracy: it uses no informative external feedback and does not hold total token use equal between one answer and two turns.

See [commands.md](commands.md) for the exact PACE ICE setup, submission, monitoring, and summary commands. No Apptainer build is needed for this pilot.
