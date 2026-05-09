# Grounding Commit

## Artifact Updated

- `pair_DAY_3/scripts/verify_embedding_drift.py`
- `pair_DAY_3/tool_grounding_analysis.md`
- Week 7 Data Contract Enforcer embedding-threshold assumptions

---

## Change

I added a verification script and analysis artifact showing that embedding similarity thresholds should be treated as checkpoint-specific after post-training.

Before this change, my Week 7 Data Contract Enforcer implicitly assumed that cosine similarity thresholds were stable across model versions when used for:

- semantic lineage attribution
- schema drift clustering
- contract-violation grouping
- attribution confidence scoring

Yosef’s explainer showed that this assumption is unsafe. Instruction tuning and preference optimization can reshape internal representation geometry non-uniformly, meaning an absolute cosine threshold calibrated on one checkpoint may not preserve the same operational meaning on a post-trained checkpoint.

---

## Before

The Week 7 system treated embedding similarity as if the measuring scale stayed stable across checkpoints:

```python
if cosine_similarity(schema_v1, schema_v2) >= THRESHOLD:
    verdict = "semantically_related"
else:
    verdict = "schema_drift"
```

This made the threshold appear portable.

This turns the Week 12 learning into a concrete improvement to the Week 7 Data Contract Enforcer.