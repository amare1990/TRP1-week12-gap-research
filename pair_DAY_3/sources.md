# Canonical Sources

## 1. Direct Preference Optimization: Your Language Model is Secretly a Reward Model

Rafailov et al. (2023)

https://arxiv.org/abs/2305.18290

Why it matters:
This is the foundational DPO paper introducing the preference optimization objective used in Yosef’s Week 11 judge training. It explains how DPO replaces explicit RLHF reward modeling with direct preference likelihood optimization and clarifies the role of the beta KL regularization term.

Key concepts used in the explainer:
- DPO objective function
- preference likelihood optimization
- KL-constrained policy updates
- reference-model anchoring
- preference separation mechanics

---

## 2. Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback

Bai et al. / Anthropic (2022)

https://arxiv.org/abs/2204.05862

Why it matters:
This paper explains the broader RLHF and preference-training framework underlying modern alignment systems. It provides important context for understanding reward overoptimization, calibration failures, and why preference optimization can improve alignment while degrading uncertainty representation.

Key concepts used in the explainer:
- preference training dynamics
- reward-model behavior
- alignment tradeoffs
- calibration degradation
- production failure modes in aligned systems

---

# Tool / Pattern Used

## Tooling Pattern: Distribution Collapse Inspection via Held-Out Judge Traces

The analysis used Yosef’s `judge_traces.jsonl` outputs from held-out evaluation runs to inspect:
- unique score diversity
- repeated verdict tokens
- contradictory generations
- score entropy collapse

A lightweight diagnostic pattern was proposed:

```python
unique_scores = set()

for trace in judge_outputs:
    unique_scores.add(trace["score"])

print(unique_scores)

Expected calibrated behavior:

{1,2,3,4,5}

Observed collapsed behavior:

{2,4}

This diagnostic demonstrates how preference-separation success can coexist with calibration collapse in small-data DPO training regimes.