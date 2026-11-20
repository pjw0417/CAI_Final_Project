"""Small MINT math pilot against a local OpenAI-compatible vLLM server."""

import argparse
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen


DATA = Path(__file__).parent / "mint-bench/data/processed/math/test_prompts.json"
ANSWER_RE = re.compile(r"<answer>\s*(.*?)\s*</answer>", re.I | re.S)
BOX_RE = re.compile(r"\\boxed\s*\{")


def tasks(path, count):
    with path.open() as source:
        return [json.loads(line) for line in source if line.strip()][:count]


def extract_answer(content):
    """Read the final response only; never infer an answer from reasoning text."""
    content = content or ""
    tagged = ANSWER_RE.findall(content)
    if tagged:
        return tagged[-1].strip() or None
    boxed = []
    for match in BOX_RE.finditer(content):
        start = match.end()
        depth = 1
        for pos in range(start, len(content)):
            if content[pos] == "{":
                depth += 1
            elif content[pos] == "}":
                depth -= 1
                if depth == 0:
                    boxed.append(content[start:pos].strip())
                    break
    return (boxed[-1] or None) if boxed else None


def grade_call(call_record, reference):
    if call_record is None:
        return None
    call_record["answer"] = extract_answer(call_record.get("content"))
    call_record["correct"] = score(reference, call_record["answer"])
    return call_record


def rescore(input_path, output_path):
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Rescored output must have a different path from the input")
    with input_path.open() as source, output_path.open("x") as output:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            for stage in ("initial", "generic_review"):
                grade_call(record.get(stage), record["reference"])
            output.write(json.dumps(record) + "\n")


def score(reference, answer):
    """Exact numeric comparison only; other answers require manual review."""
    if answer is None:
        return None
    try:
        return float(answer.replace(",", "")) == float(str(reference).replace(",", ""))
    except ValueError:
        return None


def call(base_url, model, messages, max_tokens, temperature):
    payload = json.dumps({
        "model": model, "messages": messages, "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    request = Request(
        base_url.rstrip("/") + "/chat/completions", data=payload,
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
    )
    started = time.monotonic()
    with urlopen(request, timeout=900) as response:
        result = json.load(response)
    choice = result["choices"][0]
    message = choice["message"]
    return {
        "content": message.get("content"),
        "reasoning_content": message.get("reasoning_content"),
        "finish_reason": choice.get("finish_reason"),
        "usage": result.get("usage", {}),
        "seconds": round(time.monotonic() - started, 3),
        "response_id": result.get("id"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="For example http://127.0.0.1:8000/v1")
    parser.add_argument("--rescore", type=Path, help="Rescore an existing JSONL without calling the model")
    parser.add_argument("--model", default="openai/gpt-oss-20b")
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.rescore and not args.base_url:
        parser.error("--base-url is required unless --rescore is used")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"Output already exists: {args.output}")
    if args.rescore:
        rescore(args.rescore, args.output)
        return
    with args.output.open("w") as output:
        for task in tasks(args.data, args.count):
            messages = [{"role": "user", "content": (
                f"Solve this problem. End with your final answer in <answer>...</answer>.\n\n{task['prompt']}"
            )}]
            first = call(args.base_url, args.model, messages, args.max_tokens, args.temperature)
            grade_call(first, task["reference"])
            # If the first answer has no final text, record it and do not invent an assistant turn.
            second = None
            if first["content"]:
                second = call(args.base_url, args.model, messages + [
                    {"role": "assistant", "content": first["content"]},
                    {"role": "user", "content": "Review your answer for errors. End with your final answer in <answer>...</answer>."},
                ], args.max_tokens, args.temperature)
            record = {
                "task_id": task["id"], "prompt": task["prompt"], "reference": task["reference"],
                "model": args.model, "temperature": args.temperature, "max_tokens": args.max_tokens,
                "initial": first,
                "generic_review": grade_call(second, task["reference"]),
            }
            output.write(json.dumps(record) + "\n")
            output.flush()
            print(f"task {task['id']}: first={record['initial']['correct']} review={None if second is None else record['generic_review']['correct']}", flush=True)


if __name__ == "__main__":
    main()
