# Signoff

**Status: Closed**

Before reading Yosef’s explainer, I treated embedding similarity in my Week 7 Data Contract Enforcer as if cosine thresholds were mostly portable across model checkpoints.

My implicit assumption was:

> “If two schema descriptions are semantically similar, their cosine similarity should remain operationally stable even after instruction tuning or preference optimization.”

I understood that post-training could change model behavior, but I had not fully internalized that it could selectively distort the geometry of representation space itself.

The most important insight from the explainer was understanding that post-training does not uniformly rotate or scale embedding space. Instead, alignment objectives selectively stretch and compress regions of the representation manifold along the axes emphasized by the fine-tuning distribution.

This changed my mental model significantly.

Before this discussion, I viewed embedding similarity as a relatively stable semantic measurement.

Now I understand that:

> embedding similarity is checkpoint-specific because the measuring geometry itself changes after post-training.

The runnable demonstration made this concrete.

The most useful observation was not that the nearest-neighbor ranking changed completely, but that the margin between related and unrelated schemas compressed dramatically after post-training.

That distinction matters operationally because my Week 7 system does not only depend on retrieving the correct nearest neighbor. It also depends on confidence margins for:
- lineage attribution,
- schema drift clustering,
- and semantic enforcement decisions.

The explainer also clarified why rank-based attribution is often safer than relying on absolute cosine thresholds. Even when semantic ranking survives model updates, the absolute threshold values and similarity margins may drift enough to invalidate previously calibrated enforcement logic.

The most important practical insight I gained was:

> Every post-trained checkpoint should be treated as requiring fresh similarity calibration.

This directly motivated the verification script and updated grounding analysis I added in `pair_DAY_3/scripts/verify_embedding_drift.py`.

I now understand:
- why embedding geometry changes after alignment,
- how post-training can silently affect retrieval behavior,
- why threshold portability is dangerous,
- and how to verify embedding drift empirically instead of assuming semantic stability.

Most importantly, I can now distinguish between:
- semantic ranking surviving
vs
- similarity calibration remaining trustworthy.

Those are related, but not the same thing.