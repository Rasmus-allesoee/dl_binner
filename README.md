# dl-binner

An experimental CPU metagenomic binner with our own composition-based contrastive
encoder. One command trains, saves/reloads the checkpoint, embeds, clusters and
exports bins alongside a matched raw-feature control. Optional explicit mean depth
can accompany the assembly. Every contig is retained as assigned, unassigned or
excluded, with its DNA, masks and reason.

This is a usable **development prototype**, not validated whole-MAG recovery,
independent generalization or a state-of-the-art claim. A reproducible tool and
learning through implementation are the primary goals.

## Install and run

Use separate CPU environments for the binner and **Snakemake 9.16.3**. Follow the
[pinned standalone installation guide](docs/INSTALLATION.md); 0.1.0.dev2 is built
locally, not published to a package index. Do not copy linked research environments.
The command installs nothing and needs no database, truth labels, internet connection
or repository checkout.

```sh
/absolute/binner/bin/dl-binner run --fasta assembly.fna --output result \
  --workflow-python /absolute/workflow/bin/python --threads 4
```

Add `--depth mean-depth.tsv` for finite nonnegative mean depth measured against
this exact assembly. Header: `contig_id` followed by ordered unique sample names;
every FASTA ID needs exactly one row. Missing data are refused, never filled
with zeros. Absent depth means sequence-only mode.

Outputs include `learned/bins/`, `raw/bins/`, complete `assignments.tsv` and FASTAs,
`run-summary.json`/TSV, checkpoints, features, logs and resource receipts.
The summary reports assignment/size, **not** completeness or contamination.
`dl-binner run --help` explains options. [Usage and contracts](docs/PROTOTYPE.md#run-the-binner)
cover predictable outputs and recovery.

To continue a matching partial run, repeat the command with `--resume`. Completed
stages are verified and reused; changed inputs/settings/runtime/outputs are refused.
Fresh runs never overwrite populated results. Interfaces and journals may evolve;
accepted older manifests are not migrated to fit a newer package.

## Validation and limits

- Configurable 500-bp eligibility, 20 epochs/seed 11, four CPU threads maximum,
  interop one and loader zero. Short/excluded DNA and noise are retained.
- Default sampled working RSS limit 8 GB and overall invocation timeout two hours.
  Sampling is approximate; tiny serial stages may not saturate the CPU budget.
- [E004](experiments/E004-first-binner/README.md) validates the learned path;
  [E005](experiments/E005-linux-pilot/README.md) has capped GI development
  assembled-sequence recovery evidence, with fragmentation and no >=90% recovered
  genome. That derivative overlaps earlier development data.
- [E006](experiments/E006-cli-usability/README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
  accepts native Mac/reviewed CPU/Linux contracts, exact reload, serial scheduling,
  complete exports, strict resume and bounded failures.
- No full-community scaling, independent whole-MAG quality, separate depth benefit
  or architecture superiority is established. Different contigs may be co-genomic
  negatives in training. Frozen GLM remains a future comparison.

Python 3.10 Mac and 3.12 CPU/Linux have accepted native evidence; the declared
3.10–3.12 binner range is not a fully tested matrix. Windows is unsupported.
[E007](experiments/E007-pr-readiness/README.md) owns current packaging acceptance
and the distinction between local validation and pending CI.

## Software checks

The ordinary [product suite](tests/product/) uses small generated synthetic inputs,
installed packages and a separate workflow interpreter; no ignored research caches.
[Commands](docs/INSTALLATION.md#run-product-regressions) retain logs/exit/resource
receipts outside the checkout. These tests do not measure biological utility.
Older `tests/test_*.py` and experiment reviews remain opt-in research checks with
original dependencies, not silently skipped members of the product suite.

Documentation checks require Python and Pandoc:

```sh
python3 scripts/check_docs.py
python3 scripts/check_docs.py --check-context
```

## Project record and release status

Read [AGENTS](AGENTS.md), [PROJECT_INTENT](PROJECT_INTENT.md) and [STATE](docs/STATE.md)
for current scope. [WORKING](docs/WORKING.md) defines record ownership;
[D011](docs/decisions/D011-first-binner-prototype.md) owns design rationale.
[Experiments](experiments/README.md), [evidence](docs/evidence/README.md) and
[decisions](docs/decisions/README.md) retain findings and failures.
[History](docs/history/README.md) is context, not current requirements.

The next deliverable is a private implementation PR, not public publication.
No project license has been selected. Public redistribution needs an owner license
decision and historical-source packaging review; nothing is published here.
