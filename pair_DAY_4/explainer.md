# What Your Bootstrap and Agreement Numbers Actually Mean?

By Amare Kassa

---

In your SignalForge Week 11 evaluation stack, you report several strong statistical results:

* `+48.84pp` held-out lift
* `95% CI [34.88, 62.79]`
* paired bootstrap evaluation
* `p = 0.0`
* inter-rater exact-match agreement `1.00`

At first glance, these numbers seem straightforward:
the new critic performs much better, the result is statistically significant, and the evaluators perfectly agree.

But the deeper question is not:

> “Are the numbers high?”

The deeper question is:

> “What statistical mechanism allows those numbers to justify the claims being made?”

That distinction matters because evaluation statistics are not only measurement tools. They are also arguments. They determine how confidently we communicate:

* model improvements
* deployment readiness
* benchmark validity
* reliability claims

And strong numbers are easy to overstate when we do not fully understand the dependence structure and assumptions underneath them.

## Why the Bootstrap Is Paired

The most important statistical choice in your evaluation stack is not the confidence interval itself.

It is the fact that the bootstrap is *paired*.

That choice is load-bearing.

Your evaluation compares two critics:

* the previous critic
* Path B

on the *same held-out tasks*.

Each task therefore produces a paired outcome:

| Task | Old Critic | Path B  |
| ---- | ---------- | ------- |
| 1    | wrong      | correct |
| 2    | correct    | correct |
| 3    | wrong      | wrong   |
| 4    | correct    | wrong   |

The key idea is that the two systems are *not independent samples*.

Both critics are evaluated on identical underlying task difficulty.

Some tasks are naturally easy.
Some are ambiguous.
Some are adversarial.

That shared difficulty creates statistical dependence between the two systems.

Paired bootstrap preserves that dependence structure.

An unpaired bootstrap would break it.

## What the Paired Bootstrap Actually Preserves

In paired bootstrap resampling, you resample entire task rows:

```text id="2rj7fc"
(task_i_old_result, task_i_new_result)
```

together as a unit.

That means:

* easy tasks remain easy for both systems
* hard tasks remain hard for both systems
* correlation structure between systems is preserved

This is crucial because the evaluation question is not:

> “How accurate is each critic independently?”

The question is:

> “How much better is Path B on the same distribution of tasks?”

That is a difference-estimation problem.

The paired bootstrap estimates the distribution of:

```text id="pvnr9n"
(new_accuracy - old_accuracy)
```

while preserving shared task difficulty.

This dramatically reduces variance.

Why?

Because much of the noise cancels out.

If both critics struggle on the same hard tasks, paired analysis isolates the *relative improvement* instead of repeatedly re-estimating unrelated task difficulty variation.

That is why paired evaluation is usually the correct statistical mechanism for benchmark comparisons where systems are evaluated on the same examples.

## What Would Go Wrong With an Unpaired Analysis

Suppose you ignored pairing and treated the systems as independent samples.

Now the bootstrap repeatedly mixes:

* different easy tasks
* different hard tasks
* different ambiguity levels

between systems.

That artificially inflates variance because the resampling no longer controls for shared task difficulty.

You would partially confuse:

* benchmark composition noise
  with
* actual model differences.

The resulting confidence interval would become noisier and less efficient.

In some cases, it could even reverse conclusions on small datasets.

The paired structure is therefore not a technical detail.
It is the mechanism that makes the comparison statistically aligned with the actual evaluation question.

## What the Confidence Interval Does — and Does Not — Mean

Your reported interval:

```text id="5j36qt"
95% CI [34.88, 62.79]
```

does *not* mean:

> “There is a 95% probability the true improvement lies in this interval.”

That is one of the most common misunderstandings in applied ML evaluation.

Frequentist confidence intervals describe a property of the *procedure*, not a probability distribution over the parameter itself.

The correct interpretation is closer to:

> “If we repeatedly resampled comparable held-out datasets and repeated this evaluation procedure many times, 95% of those intervals would contain the true benchmark lift.”

The interval quantifies uncertainty caused by finite sampling from the held-out benchmark.

It does *not* guarantee:

* production performance
* robustness under distribution shift
* future customer outcomes
* stability under changing task mixtures

That distinction matters enormously in production systems.

A strong offline interval means:

> the benchmark evidence is strong under the current evaluation distribution.

It does *not* mean:

> the deployment environment is solved.

## What `p = 0.0` Really Means

Strictly speaking, `p = 0.0` is almost never literally true.

What it usually means is:

```text id="jlwm7d"
p < machine_precision
```

or:

```text id="7m6wkm"
p < 1 / num_bootstrap_samples
```

depending on implementation.

The important point is not:

> “the probability the model is wrong is zero.”

That is not what a p-value measures.

The p-value measures:

> how surprising the observed benchmark difference would be if the null hypothesis were true.

In this case:

* null hypothesis → no real difference between critics
* observed result → very large held-out lift

A tiny p-value means:

> “This observed improvement would be extremely unlikely under the null.”

It does not prove:

* causal correctness
* production readiness
* universal superiority
* benchmark completeness

Strong statistical evidence is not the same thing as complete operational validation.

## Why Perfect Inter-Rater Agreement Is Trickier Than It Looks

Your `1.00` exact-match agreement result is also easy to overinterpret.

At first glance, perfect agreement sounds like:

> “humans completely agree.”

But the interpretation depends heavily on the rubric design.

Your pilot rubric was deliberately mechanical:

* explicit criteria
* crisp pass/fail structure
* constrained judgment space

That changes what agreement actually measures.

High agreement on a mechanical rubric often means:

> the rubric is reproducible.

It does *not automatically* mean:

* the rubric captures deeper semantic quality
* the benchmark fully represents production complexity
* humans broadly agree on the underlying concept outside the rubric

This is a very important distinction in evaluation design.

A rubric can achieve:

* high reproducibility
* high consistency
* strong exact-match agreement

while still measuring a narrow operational definition of correctness.

That is not a flaw.
But it changes what claims are justified.

Your pilot therefore supports a claim like:

> “The rubric can be applied consistently by raters on this task subset.”

It does *not* fully justify:

> “Human consensus about overall model quality has been solved.”

Those are different claims.

## The Real Evaluation Lesson

The deeper lesson across both the bootstrap and agreement analysis is this:

> Evaluation statistics justify narrower claims than people often want them to justify.

Your results strongly support:

* benchmark lift on the held-out distribution
* reproducible application of the rubric
* statistically credible relative improvement

But they do not automatically prove:

* deployment safety
* robustness under shift
* universal task generalization
* complete human consensus

Understanding that boundary is what separates:

* using statistics as decoration
  from
* using statistics as disciplined decision support.

## How I Would Communicate These Results

A statistically honest deployment summary would sound something like:

> “Path B shows a large and statistically robust improvement over the previous critic on the held-out benchmark under paired bootstrap evaluation. The agreement pilot suggests the rubric can be applied consistently on the evaluated subset. However, these results remain benchmark-conditioned and should not be interpreted as guarantees of production robustness or universal evaluator consensus.”

That wording is more careful, but also more trustworthy.

And in production evaluation systems, trustworthiness of claims matters as much as the headline metrics themselves.

---

## Sources

1. Bradley Efron & Robert Tibshirani — *An Introduction to the Bootstrap*
   [https://www.stat.berkeley.edu/~breiman/211f11/efron.pdf](https://www.stat.berkeley.edu/~breiman/211f11/efron.pdf)

2. Eugene Agresti — *An Introduction to Categorical Data Analysis*
   [https://onlinelibrary.wiley.com/doi/book/10.1002/0470114754](https://onlinelibrary.wiley.com/doi/book/10.1002/0470114754)

---