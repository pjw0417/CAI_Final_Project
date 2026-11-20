# Commands for the MINT Math Pilot

Run these commands on PACE ICE from the root of this project, where `run_pilot.sbatch` and `pilot_math.py` are located.

## 1. Check the shared environment and model cache

```bash
module load anaconda3
source /usr/local/pace-apps/manual/packages/anaconda3/2023.03/etc/profile.d/conda.sh
conda activate /storage/ice1/0/4/lheck6/CS6604_ECE6256/envs/CAI_A4
export HF_HOME=/storage/ice1/0/4/lheck6/CS6604_ECE6256/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONNOUSERSITE=1
python -c 'import vllm; print("vLLM", vllm.__version__)'
ls "$HF_HOME/hub/models--openai--gpt-oss-20b/snapshots"
```

The job script sets these environment variables again on the compute node. If the final `ls` fails, check where the shared cache stores this model before submitting the job.

## 2. Submit a one-problem smoke run

```bash
sbatch --export=ALL,PILOT_COUNT=1 run_pilot.sbatch
```

The command prints a Slurm job ID. A successful run creates `results/pilot-JOB_ID.jsonl` and `results/vllm-JOB_ID.log`.

## 3. Check the job and output

```bash
squeue -u "$USER"
tail -f mint-pilot-JOB_ID.out
```

Replace `JOB_ID` with the ID from `sbatch`. Stop `tail -f` with Ctrl+C. After the job finishes, inspect its first result:

```bash
python -m json.tool results/pilot-JOB_ID.jsonl | head -100
```

For a one-problem smoke run, this file contains one JSON object. For a full pilot, it contains one JSON object per line; use the summary command below instead of `json.tool` on the whole file.

## 4. Submit the pilot

```bash
sbatch run_pilot.sbatch
```

This runs all 100 MINT MATH problems with a 6,144-token ceiling for **each** of the initial and generic-review turns. The batch script serves the model with a 16,384-token context limit. A token ceiling is not guaranteed token use, and a review request includes the first response in its input. To run a smaller check before the full pilot:

```bash
sbatch --export=ALL,PILOT_COUNT=8 run_pilot.sbatch
```

That includes tasks 5 and 7, which hit the output limit in earlier runs. To override both defaults for one job:

```bash
sbatch --export=ALL,PILOT_COUNT=30,MAX_TOKENS=4096 run_pilot.sbatch
```

## 5. Summarize a completed pilot

Run these commands from the project root. Your current `results/` folder contains
files named `max_token_2048_1_task.jsonl`, `max_token_2048_20_tasks.jsonl`,
`max_token_4096_20_tasks.jsonl`, and `max_token_6144_100_tasks.jsonl`.

To print a report for all four files in the terminal:

```bash
python analyze_pilot.py results/*.jsonl
```

To save that report as `results/pilot-report.md`:

```bash
python analyze_pilot.py results/*.jsonl --output results/pilot-report.md
```

To analyze only the 100-task run:

```bash
python analyze_pilot.py results/max_token_6144_100_tasks.jsonl
```

New runs from `run_pilot.sbatch` use filenames such as `results/pilot-JOB_ID.jsonl`.
To analyze one of those, replace `JOB_ID` with the number printed by `sbatch`:

```bash
python analyze_pilot.py results/pilot-JOB_ID.jsonl
```

The analyzer extracts answers from `<answer>...</answer>` or the last complete
`\boxed{...}` in final response text and regrades older files in memory. It does
not alter the JSONL files. A `null` correctness in the source can mean no
extractable numeric answer; check `finish_reason` and `content`. A missing
review means the initial call had no final text. Reasoning text is never scored
as a final answer.

The report shows counts of correct, incorrect, and unscored responses; token
median, p95, and maximum; mean call time; answer changes after review; and the
task IDs that need inspection. Its across-run table is descriptive: runs with
different task counts or token limits are not a controlled accuracy comparison.

Review the raw records before treating the provisional `correct` field as accuracy.

## Apptainer image

**No Apptainer image build is needed for this pilot.** The job runs vLLM and `pilot_math.py` directly in the shared `CAI_A4` Conda environment. The old `recipe/agent.def`, ASR, TTS, and `agent.sif` are not used. Changes to `pilot_math.py` also do not require an image rebuild.
