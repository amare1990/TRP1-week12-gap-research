
---

## `pair_DAY_3/tool_grounding_analysis.md`


# Tool Grounding Analysis

## Original Assumption

Before reading Yosef’s explainer, I assumed that embedding similarity thresholds in my Week 7 Data Contract Enforcer were mostly stable across model checkpoints.

The implicit assumption was:

> If two schema descriptions have cosine similarity above a calibrated threshold, that threshold means roughly the same thing before and after instruction tuning or preference optimization.

That assumption was incomplete.

Yosef’s explainer clarified that post-training can reshape representation geometry non-uniformly. This means that even if a model becomes better at instruction-following, the hidden-state or embedding geometry used for retrieval-style similarity can shift.

---

## Failure Mode — The Measuring Stick Changes Shape

My Week 7 pipeline used embedding similarity for:

- schema drift attribution
- clustering related contract violations
- semantic lineage matching
- attribution confidence

The risk is that post-training does not simply rotate or uniformly scale the embedding space.

Instead, it can stretch or compress specific semantic regions depending on the instruction or preference data used during alignment.

That means a threshold such as:

```python
THRESHOLD = 0.90
```

may not preserve the same meaning after a model update.

A pair that previously scored 0.95 might drop to 0.92.

An unrelated schema that previously scored 0.89 might rise to 0.92.

The ranking may survive, but the confidence margin can collapse.

Concrete Production Risk

The dangerous case is not only that retrieval returns the wrong nearest neighbor.

The more subtle failure is that the system may still return the right neighbor, but with a much smaller margin.

For example:

Before post-training:

```
schema_v1 vs schema_v2_minor_drift = 0.958
schema_v1 vs unrelated_schema      = 0.899
margin                             = 0.059

```

After post-training:

```
schema_v1 vs schema_v2_minor_drift = 0.932
schema_v1 vs unrelated_schema      = 0.920
margin                             = 0.012
```

The top result is still correct, but the attribution is much less reliable.

This matters because Week 7’s enforcement report should not treat both cases as equally confident.

Implemented Verification Pattern

I added a verification script:

```
data-contract-enforcer/scripts/verify_embedding_drift.py
```

The script compares a base checkpoint and a post-trained checkpoint over a small schema-drift scenario.

It checks:

absolute cosine similarity shift,
related-vs-unrelated margin shift,
threshold decision instability,
rank-based attribution stability.

The key diagnostic is:

```
related_margin = sim(schema_v1, schema_v2_minor_drift) - sim(schema_v1, unrelated_schema)
```

This is more useful than checking only raw cosine values because the margin tells us whether the attribution remains discriminative.

New Engineering Rule

The updated rule for the Week 7 Data Contract Enforcer is:

Never reuse embedding similarity thresholds across model checkpoints without recalibration.

A safer production policy is:

Pin the embedding model version used for enforcement reports.
Recompute calibration thresholds after every checkpoint change.
Track similarity-margin drift, not only top-1 nearest neighbor.
Prefer rank-based attribution when absolute thresholds are unstable.
Add a warning when related-vs-unrelated margins compress below a safe operating band.
What Changed

Before this work:

embedding thresholds were treated as portable
semantic similarity was assumed to be stable
lineage confidence depended on raw cosine scores
model upgrades could silently affect attribution quality

After this work:

embedding thresholds are treated as checkpoint-specific
similarity margins are measured explicitly
rank-based attribution is preferred for portability
model upgrades require recalibration
the failure mode is documented and reproducible

The core conceptual shift is:

Post-training may improve instruction-following while making retrieval-style similarity less stable.

That changes how I would defend the Week 7 architecture in front of a senior engineer.

---