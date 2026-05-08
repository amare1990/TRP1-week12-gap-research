# Thread

1/ My pair-day partner asked a deceptively important evaluation question:

Why can aggregate LLM metrics look healthy while important failures are already happening underneath?

The answer changed how I think about evaluation entirely.

2/ In our Week 10/11 evaluation pipeline, the global metrics looked reassuring:
- average similarity ≈ 0.415
- decent judge scores
- acceptable pass rates

But later debugging revealed condition-level collapse.

3/ Multiple baseline traces across unrelated probe categories were producing the same fallback response template.

The aggregate metric did not reveal that.

Why?

Because averages compress structure.

4/ That was the key insight:

> aggregate metrics are compressions over mixtures of behaviorally different cases.

The problem was not that the average was mathematically wrong.

The problem was that it erased subgroup behavior.

5/ We were mixing:
- retrieval-grounded probes
- routing failures
- policy-sensitive cases
- fallback behavior

into one global metric.

Once that happens, a subgroup can collapse while the overall average still looks stable.

6/ This is why global metrics can hide real LLM failures.

The metric reflects the weighted mixture, not whether one operationally important subgroup is broken.

7/ The same issue explained a problem in our evaluator.

The judge rewarded:
- fluency
- confidence
- polished formatting

while under-penalizing:
- missing grounding
- ignored constraints
- template reuse

8/ That revealed a deeper evaluation problem:

The judge was partially measuring the wrong construct.

“Good-looking response”
is not the same capability as:
“constraint-faithful grounded response.”

9/ The most useful rule from the discussion was:

> Could one important subgroup get worse while the global metric stays flat or improves?

If yes:
aggregate metrics alone are insufficient.

10/ That means slicing is not optional when:
- datasets mix behavioral modes
- failures are rare but costly
- routing paths differ
- benchmarks contain multiple task families

11/ Good evaluation slices usually correspond to mechanisms:
- failure mode
- routing path
- confidence bucket
- retrieval presence
- policy sensitivity
- fallback eligibility

12/ The core lesson:

A metric is only trustworthy when:
- its operational meaning matches the capability claim
and
- slice behavior agrees with the aggregate trend.

13/ Global metrics are still useful.

But they are for:
- top-line reporting
- regressions
- coarse comparisons

Real debugging happens inside condition-level structure.

14/ Full explainer:

Medium link: https://medium.com/@amaremek/why-your-aggregate-llm-metrics-are-probably-hiding-important-failures-27a34f047e25
x/twiiter link: x.com/amaremek/status/2052841984742613227

15/ Repo + evaluation work:

https://github.com/amare1990/tenacious-bench.git