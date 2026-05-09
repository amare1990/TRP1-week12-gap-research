# Grounding Evaluation Analysis

## Purpose

Day 4 focused on evaluation and statistics. My question was about why aggregate metrics can look healthy while important LLM failures remain hidden inside specific conditions, categories, or routing paths.

After reading my peer’s explainer, I added a small slice-analysis script to make this failure visible in my own Week 10/11 evaluation data.

## Command

```bash
uv run python pair_DAY_4/scripts/evaluate_slice_metrics.py
```

What the Script Measures

The script computes both global and sliced metrics over held_out_traces.jsonl.

It reports:

number of examples
pass rate
number of failures
number of unique outputs
most common output count
most common output share
most repeated output

It computes these metrics globally, then slices by:

condition
category

---

## Observed Output

# Evaluation Slice Metrics
Loaded traces: 60

## Global
{
  "n": 60,
  "pass_rate": 0.6,
  "failed": 24,
  "unique_outputs": 17,
  "most_common_output_count": 17,
  "most_common_output_share": 0.283,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

## By condition

auto_optimization
{
  "n": 20,
  "pass_rate": 0.4,
  "failed": 12,
  "unique_outputs": 3,
  "most_common_output_count": 16,
  "most_common_output_share": 0.8,
  "most_common_output": "Thanks for the context. I can share a measured observation and avoid assuming more than the public signal supports."
}

baseline
{
  "n": 20,
  "pass_rate": 0.4,
  "failed": 12,
  "unique_outputs": 3,
  "most_common_output_count": 17,
  "most_common_output_share": 0.85,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

method
{
  "n": 20,
  "pass_rate": 1.0,
  "failed": 0,
  "unique_outputs": 11,
  "most_common_output_count": 3,
  "most_common_output_share": 0.15,
  "most_common_output": "Thanks for the context.\nUse question-first wording and separate observed facts from hypotheses.\nUseful next step: a brief exploratory call only if the signal and timing are relevant on your side."
}

## By category

bench_overcommitment
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 4,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

cost_pathology
{
  "n": 6,
  "pass_rate": 1.0,
  "failed": 0,
  "unique_outputs": 3,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

dual_control
{
  "n": 6,
  "pass_rate": 1.0,
  "failed": 0,
  "unique_outputs": 3,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

gap_overclaiming
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 4,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Thanks for the context. I can share a measured observation and avoid assuming more than the public signal supports."
}

icp_misclassification
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 5,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Congrats on the raise. Since you are aggressively hiring, Tenacious can help scale your engineering team fast."
}

multi_thread_leakage
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 3,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

scheduling
{
  "n": 6,
  "pass_rate": 1.0,
  "failed": 0,
  "unique_outputs": 5,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

signal_overclaiming
{
  "n": 6,
  "pass_rate": 1.0,
  "failed": 0,
  "unique_outputs": 3,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

signal_reliability
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 5,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}

tone_drift
{
  "n": 6,
  "pass_rate": 0.333,
  "failed": 4,
  "unique_outputs": 3,
  "most_common_output_count": 2,
  "most_common_output_share": 0.333,
  "most_common_output": "Tenacious can provide offshore engineers quickly. Would you like a 30-minute call?"
}


---
Why This Matters

Before Day 4, I treated global metrics as if they were sufficient summaries of model behavior.

But my peer’s explainer clarified that an aggregate metric is a compression over potentially different behavioral regimes. If the dataset mixes different conditions, the global average can remain moderate even when one subgroup is failing badly.

The key statistical insight is:

averages do not lie, but they erase structure.

This is exactly what happened in my earlier collapse analysis. The global similarity metric suggested that collapse was not happening overall, but condition-level inspection showed repeated fallback templates inside specific regimes.

Expected Interpretation

The slice analysis is meant to answer:

Could one important subgroup get worse while the global metric stays flat or acceptable?

If yes, then the global metric is not enough.

The important output is not only the global pass rate. The important outputs are the subgroup summaries:

Which condition has the highest repeated-output share?
Which category has the lowest pass rate?
Which slice has many failures despite acceptable global performance?
Which output template repeats inside a condition?
Design Change

This analysis changes my evaluation methodology.

Going forward, I should not report only:

global pass rate
global similarity
overall judge score

I should also report:

pass rate by condition
pass rate by category
repeated-output share by condition
repeated-output share by category
worst-slice performance

--- 

Before

My evaluation treated global summaries as sufficient:

overall pass/fail rate
overall similarity score
overall judge behavior

This made it possible for condition-level failures to be statistically diluted.

After

The evaluation now includes mechanism-aware slices:

condition-level summaries
category-level summaries
repeated-output diagnostics
worst-slice inspection

This makes hidden failures visible instead of allowing them to disappear inside averages.

Conclusion

The grounding change is not just an extra report. It changes what I consider valid evidence.

A global metric is now only a top-line summary. It is not sufficient evidence that the system is reliable across behaviorally different conditions.

For production-style LLM evaluation, I should trust a global metric only when the important slices agree with it.

---