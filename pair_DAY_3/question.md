# Final Question

In my Week 7 Data Contract Enforcer project, I used embedding similarity thresholds to attribute schema drift events and cluster semantically related contract violations.

My gap is:

How does instruction tuning during post-training change the geometry of embedding representations inside transformer hidden states, and why can this cause cosine-similarity retrieval behavior to shift even when the model appears “better” at instruction following?

This matters because my Week 7 attribution pipeline assumes embedding similarity remains stable across post-trained checkpoints when performing semantic lineage attribution and drift clustering. If post-training reshapes representation space in non-uniform ways, then retrieval thresholds, clustering behavior, and attribution confidence may silently degrade after model upgrades.

I specifically want to understand:
1. What mechanism during instruction tuning changes internal representation geometry,
2. Why cosine similarity relationships can drift after alignment,
3. Whether this effect is concentrated in specific layers or token types,
4. How production systems detect or mitigate embedding drift after post-training updates.

A successful explainer would include:
- a concrete visualization or experiment comparing embeddings before and after tuning,
- the load-bearing mechanism in plain engineering language,
- and practical implications for retrieval, evaluation, or attribution systems used in FDE workflows.