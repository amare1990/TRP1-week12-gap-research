
# Thread

1/ My pair-day partner asked a subtle but important post-training question:

Why did a DPO-trained judge achieve near-zero training loss…

while collapsing all outputs into only:

PASS 4  
FAIL 2

with no 1, 3, or 5 scores ever appearing?

That failure reveals something important about what DPO actually optimizes.

2/ In the Week 11 judge system we reviewed, the training loss fell:

0.636 → 0.306 → 0.094

using:
- Qwen2.5-7B
- LoRA adaptation
- DPOTrainer
- 194 preference pairs
- beta=0.1

At first glance, this looked like successful alignment.

3/ But the held-out evaluation traces showed something different.

The judge learned:
- binary separation

but lost:
- score calibration
- uncertainty representation
- ordinal reasoning

Every PASS became 4.  
Every FAIL became 2.

4/ The key mechanism:

DPO does NOT optimize calibrated scores.

It optimizes:

preferred response > rejected response

That means the optimizer only cares whether the chosen completion becomes more probable than the rejected completion.

5/ The easiest low-loss solution for a tiny dataset became:

```text
good response  -> PASS 4
bad response   -> FAIL 2
````

This cleanly separates preference pairs while minimizing loss quickly.

Training succeeded.

Calibration collapsed.

6/ The beta KL term is also commonly misunderstood.

`beta` does NOT:

* preserve score diversity
* prevent collapse
* maintain ordinal geometry

It only constrains how far the trained model drifts from the reference model distribution.

7/ During implementation review, we found an even more important production insight.

The training objective never explicitly required:

* uncertainty calibration
* score spacing
* entropy preservation
* ordinal consistency

So the optimizer had no incentive to preserve them.

8/ The repeated generations exposed another issue:

```text
FAIL 2

FAIL 2
```

and even:

```text
FAIL 2

PASS 4
```

This happened because the judge was still fundamentally an autoregressive next-token predictor, not a constrained scoring engine.

9/ The model learned verdict phrases rather than stable structured judgment behavior.

Once generation entered a high-probability verdict trajectory, decoding repeatedly revisited the same token patterns.

10/ We proposed a simple diagnostic:

```python
unique_scores = set()

for trace in judge_outputs:
    unique_scores.add(trace["score"])

print(unique_scores)
```

Expected:

```text
{1,2,3,4,5}
```

Observed:

```text
{2,4}
```

11/ The deeper production lesson:

A low DPO loss does NOT prove calibrated reasoning.

Preference optimization can improve binary alignment while simultaneously destroying uncertainty representation.

If you only monitor:

* accuracy
* win-rate
* training loss

you can completely miss:

* score collapse
* entropy collapse
* calibration drift

12/ This matters everywhere in production AI systems:

* LLM-as-a-judge
* rerankers
* moderation systems
* safety classifiers
* reward models
* evaluation pipelines

Binary correctness is not the same thing as calibrated reasoning.

13/ Full explainer:

Medium: https://medium.com/@amaremek/at-first-glance-this-looked-like-alignment-success-ed34fea7e7a8?postPublishedType=repub

X/Twitter: x.com/amaremek/status/2052475072711922125

14/ Reviewed implementation artifacts:

* `week11_unsloth.py`
* `judge_traces.jsonl`

---
