# Why Your DPO-Trained Judge Learned “PASS 4” and “FAIL 2” Instead of Real Scoring

By Amare Kassa

---

In your Week 11 judge system, the training metrics initially look extremely successful.

Inside `week11_unsloth.py`, the LoRA-adapted Qwen2.5-7B was trained with `DPOTrainer` using the default `beta=0.1`, and the loss fell sharply across three epochs:

| Epoch | Loss  |
| ----- | ----- |
| 1     | 0.636 |
| 2     | 0.306 |
| 3     | 0.094 |

Ordinarily, a curve like this suggests the preference optimization process is working well.

But when the trained judge was evaluated on 39 held-out traces from `judge_traces.jsonl`, the system revealed a very different failure mode:

* every PASS verdict produced exactly `score=4.0`
* every FAIL verdict produced exactly `score=2.0`
* the model never emitted 1, 3, or 5
* several generations repeated the verdict twice
* two traces contradicted themselves (`FAIL 2 → PASS 4`)

That combination tells us something important about what Direct Preference Optimization (DPO) actually optimizes — and what it does not.

The core misunderstanding is assuming DPO trains *calibrated scores*.

It does not.

DPO trains *relative preference separation*.

That distinction is the entire load-bearing mechanism behind the collapse.

---

# What DPO Actually Optimizes

The DPO objective is:

Direct Preference Optimization (DPO) Loss$$ \mathcal{L}_{DPO} = -\log\sigma\left(\beta\left[\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)}-\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right]\right)$$

Where: 

$y_w$ = preferred response
$y_l$ = rejected response

$\pi_\theta$ = trained model

$\pi_{ref}$ = frozen reference model

$\beta$ = KL regularization strength

Notice what is missing from the objective:

* no regression target
* no ordinal ranking supervision
* no calibration constraint
* no entropy objective over scores 1–5

The optimizer only asks:

> “Can the model assign higher probability to the preferred completion than the rejected completion?”

That means the model can minimize loss while collapsing internally to:

| Semantic State | Learned Output |
| -------------- | -------------- |
| Preferred      | `PASS 4`       |
| Rejected       | `FAIL 2`       |

Once that separation becomes reliable, the optimizer has very little incentive to preserve richer score geometry.

The model does not “care” whether:

* PASS becomes 4 or 5,
* FAIL becomes 1 or 2,
* or whether uncertainty is represented at all.

As long as:

* preferred > rejected,

the DPO loss falls.

That is why the training curve looked healthy while the judge behavior became degenerate.

---

# Why the Small Dataset Made Collapse Worse

Your setup used:

* 194 preference pairs
* LoRA adaptation
* a 7B model
* only 3 epochs

That is an extremely small preference-training regime.

In low-data DPO settings, the optimizer often learns:

* coarse decision boundaries,
  not
* nuanced reward structure.

The easiest solution for the model was likely:

```text id="e9p0r7"
good response  -> PASS 4
bad response   -> FAIL 2
```

because this cleanly separates preferred and rejected examples while minimizing loss quickly.

This is a form of **reward-expression collapse**.

The model still performs binary discrimination, but it loses the ability to express:

* confidence,
* ambiguity,
* uncertainty,
* or fine-grained ranking.

The score space compresses into two stable attractors.

Importantly, this is not necessarily visible in the training loss.

The optimizer succeeded at the objective it was given.

The problem is that the objective was narrower than the behavior you actually wanted.

---

# What the Beta KL Term Actually Does

Most people misunderstand the `beta` parameter.

`beta` is not:

* a diversity controller,
* a score calibration mechanism,
* or a protection against score collapse.

It is a constraint on how far the trained policy drifts from the reference model.

Larger `beta`:

* penalizes deviation more strongly,
* keeps outputs closer to base Qwen behavior,
* slows aggressive preference overfitting.

Smaller `beta`:

* allows larger policy shifts,
* amplifies preference gradients,
* increases collapse risk.

But the critical point is:

> KL regularization preserves distributional proximity, not score geometry.

Even with `beta=0.1`, the model can still:

* collapse score diversity,
* lose ordinal structure,
* and compress uncertainty,

while remaining relatively close to the original reference distribution overall.

In your case:

* the dataset was tiny,
* the preference signal was effectively binary,
* and the easiest low-loss strategy was binary compression.

The KL term prevented catastrophic language drift.

It did not preserve nuanced scoring behavior.

---

# Why the Repeated and Contradictory Verdicts Happened

The repeated generations:

```text id="b6qf8v"
FAIL 2

FAIL 2

The
```

and contradictory outputs:

```text id="4t9v7w"
FAIL 2

PASS 4
```

reveal something important about autoregressive generation.

Your judge was still fundamentally a next-token predictor.

It was not trained as:

* a constrained classifier,
* a calibrated reward head,
* or a structured scoring engine.

So generation likely unfolded like this:

1. the model emitted a high-probability verdict token
2. decoding continued autoregressively
3. competing continuations re-entered the beam
4. unstable continuation trajectories emerged

Because the model had collapsed into only two dominant verdict attractors (`PASS 4`, `FAIL 2`), generation repeatedly revisited those token patterns.

This becomes especially common when:

* outputs are short,
* formatting constraints are weak,
* greedy decoding dominates,
* and termination behavior is poorly learned.

The model learned verdict *phrases*.

It did not learn stable structured judgment behavior.

---

# Runnable Demonstration

A simplified version of the collapse mechanism looks like this:

```python
training_pairs = [
    ("PASS 5", "FAIL 1"),
    ("PASS 4", "FAIL 2"),
    ("PASS 5", "FAIL 2"),
]
```

The DPO optimizer only learns:

```python
preferred > rejected
```

It is never explicitly trained to preserve:

* ordinal spacing,
* score entropy,
* or calibration geometry.

That means this collapsed solution still minimizes loss:

```text id="eqkkx0"
positive -> PASS 4
negative -> FAIL 2
```

even though the intended score range was:

```text id="rxk5a5"
1, 2, 3, 4, 5
```

A simple diagnostic check would immediately expose the collapse:

```python
unique_scores = set()

for trace in judge_outputs:
    unique_scores.add(trace["score"])

print(unique_scores)
```

Expected calibrated behavior:

```text id="9m2j6k"
{1,2,3,4,5}
```

Observed collapsed behavior:

```text id="v9q3hy"
{2,4}
```

This reveals an important production lesson:

> preference separation improved while score entropy collapsed.

---

# Why This Matters for FDE Systems

This failure mode appears everywhere in production AI systems:

* LLM-as-a-judge
* safety classifiers
* rerankers
* reward models
* moderation systems
* evaluation pipelines

If teams only monitor:

* training loss,
* pass/fail accuracy,
* or win-rate,

they can completely miss:

* calibration collapse,
* uncertainty blindness,
* entropy compression,
* and ranking degradation.

Your judge technically “worked” in the binary sense.

But operationally it failed because it could no longer express nuanced confidence.

That makes:

* thresholding brittle,
* ranking unstable,
* escalation policies unreliable,
* and downstream automation dangerous.

The real lesson is:

> A low DPO loss does not prove calibrated reasoning.

It only proves the model became more confident at preference separation.

Those are not the same thing.

---

# What Would Likely Improve the Judge

Several interventions would likely reduce collapse:

| Intervention                 | Why It Helps                      |
| ---------------------------- | --------------------------------- |
| Larger preference dataset    | Prevents shortcut learning        |
| Explicit ordinal supervision | Preserves score geometry          |
| Slightly larger beta         | Slows aggressive compression      |
| Structured decoding          | Prevents repeated verdict drift   |
| Entropy monitoring           | Detects score collapse early      |
| Scalar reward heads          | Separates scoring from generation |
| Calibration evaluation       | Measures uncertainty quality      |

Most importantly:

> DPO is a preference-ranking objective, not a calibrated scoring objective.

Those are related — but fundamentally different.

---

# Sources

1. Rafailov et al. — *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*
   [https://arxiv.org/abs/2305.18290](https://arxiv.org/abs/2305.18290)

2. Anthropic — *Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback*
   [https://arxiv.org/abs/2204.05862](https://arxiv.org/abs/2204.05862)

---