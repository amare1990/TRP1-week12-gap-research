import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = ROOT / "held_out_traces.jsonl"


def load_traces(path: Path) -> list[dict]:
    traces = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                traces.append(json.loads(line))
    return traces


def summarize_group(traces: list[dict]) -> dict:
    total = len(traces)
    passed = sum(1 for t in traces if t.get("passed") is True)
    failed = total - passed

    outputs = [t.get("output", "") for t in traces]
    repeated_outputs = defaultdict(int)
    for output in outputs:
        repeated_outputs[output] += 1

    most_common_output, most_common_count = max(
        repeated_outputs.items(),
        key=lambda item: item[1],
    )

    return {
        "n": total,
        "pass_rate": round(passed / total, 3) if total else None,
        "failed": failed,
        "unique_outputs": len(repeated_outputs),
        "most_common_output_count": most_common_count,
        "most_common_output_share": round(most_common_count / total, 3) if total else None,
        "most_common_output": most_common_output,
    }


def group_by(traces: list[dict], key: str) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for trace in traces:
        grouped[str(trace.get(key, "unknown"))].append(trace)
    return grouped


def print_section(title: str, rows: dict[str, list[dict]]) -> None:
    print(f"\n## {title}")
    for name, group in sorted(rows.items()):
        summary = summarize_group(group)
        print(f"\n{name}")
        print(json.dumps(summary, indent=2))


def main() -> None:
    traces = load_traces(TRACE_PATH)

    print("# Evaluation Slice Metrics")
    print(f"Loaded traces: {len(traces)}")

    print("\n## Global")
    print(json.dumps(summarize_group(traces), indent=2))

    print_section("By condition", group_by(traces, "condition"))
    print_section("By category", group_by(traces, "category"))


if __name__ == "__main__":
    main()