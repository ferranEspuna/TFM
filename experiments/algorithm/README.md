# Algorithm experiments

This folder contains exploratory code for testing the partite hypergraph search algorithm.
It is intentionally separate from the PDF build, so document compilation only needs the root
`requirements.txt`.

Install optional experiment dependencies with:

```bash
python -m pip install -r experiments/algorithm/requirements.txt
```

Then run the experiment script from the repository root:

```bash
python experiments/algorithm/run_experiment.py
```

`RandomPermutationHypergraph` also expects a `random_permutation` module/package if you use
that specific generator.
