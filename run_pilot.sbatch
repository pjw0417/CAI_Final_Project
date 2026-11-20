#!/bin/bash
# Run from the repository root: sbatch run_pilot.sbatch
# Optional: sbatch --export=ALL,PILOT_COUNT=30,MAX_TOKENS=6144 run_pilot.sbatch
# Adapted from the user's previous PACE ICE assignment script.
#SBATCH --job-name=mint-pilot
#SBATCH --gres=gpu:H100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=mint-pilot-%j.out

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR}"
LLM_MODEL="${LLM_MODEL:-openai/gpt-oss-20b}"
PILOT_COUNT="${PILOT_COUNT:-100}"
MAX_TOKENS="${MAX_TOKENS:-6144}"
export HF_HOME=/storage/ice1/0/4/lheck6/CS6604_ECE6256/hf_cache
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONNOUSERSITE=1

module load anaconda3 2>/dev/null || true
source /usr/local/pace-apps/manual/packages/anaconda3/2023.03/etc/profile.d/conda.sh
conda activate /storage/ice1/0/4/lheck6/CS6604_ECE6256/envs/CAI_A4
PYTHON=/storage/ice1/0/4/lheck6/CS6604_ECE6256/envs/CAI_A4/bin/python

cd "${REPO_ROOT}"
mkdir -p results
PORT=$((20000 + SLURM_JOB_ID % 20000))
VLLM_LOG="results/vllm-${SLURM_JOB_ID}.log"
"${PYTHON}" -m vllm.entrypoints.openai.api_server \
    --model "${LLM_MODEL}" --host 127.0.0.1 --port "${PORT}" \
    --dtype bfloat16 --max-model-len 16384 --gpu-memory-utilization 0.60 --seed 42 \
    > "${VLLM_LOG}" 2>&1 &
VLLM_PID=$!
trap 'kill "${VLLM_PID}" 2>/dev/null || true' EXIT

for attempt in $(seq 1 240); do
    if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then break; fi
    if ! kill -0 "${VLLM_PID}" 2>/dev/null; then
        tail -n 40 "${VLLM_LOG}"
        exit 1
    fi
    sleep 5
done
curl -fsS "http://127.0.0.1:${PORT}/v1/models" | grep -Fq "${LLM_MODEL}"

"${PYTHON}" pilot_math.py \
    --base-url "http://127.0.0.1:${PORT}/v1" \
    --model "${LLM_MODEL}" --count "${PILOT_COUNT}" \
    --max-tokens "${MAX_TOKENS}" \
    --output "results/pilot-${SLURM_JOB_ID}.jsonl"
