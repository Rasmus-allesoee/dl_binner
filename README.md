# Metagenomic Binning Research

Research toward an original, rigorously evaluated metagenomic genome-binning method. The ambition is a meaningful methodological advance, potentially competitive with the best contemporary methods in a clearly stated setting.

See [current state](docs/STATE.md) for implementation status, completed work, and the next research step.

## Start here

1. Read [AGENTS.md](AGENTS.md) and [PROJECT_INTENT.md](PROJECT_INTENT.md) for working conventions and purpose.
2. Read [current state](docs/STATE.md) for the immediate direction, open dependencies, and where to continue.
3. Follow its links to the relevant evidence, questions, and decisions.

## Research record

| Location | Responsibility |
| --- | --- |
| [Current state](docs/STATE.md) | The current handoff and next block of work |
| [Working with the record](docs/WORKING.md) | Document ownership, provenance, Git, and maintenance conventions |
| [Initial assessment](docs/research/2026-09-16-initial-assessment.md) | Scientific starting point, alternatives, and the recommended next investigation |
| [Questions and hypotheses](docs/research/questions.md) | Questions and testable hypotheses, with status and resolution history |
| [Evidence](docs/evidence/README.md) | Thesis findings, literature and code reconnaissance, and reusable assets |
| [Decisions](docs/decisions/README.md) | Important choices, alternatives, reasoning, and supersession links |
| [Experiments](experiments/README.md) | Protocols, attempts, configurations, results, and conclusions, including failures |
| [Source context](agent_context/README.md) | Original thesis and planning material, plus local reference caches |
| [Historical planning](docs/history/README.md) | Earlier ideas retained as history |

The first experiment now has a small [validation harness and operations guide](experiments/E001-coverage-thinning/OPERATIONS.md), not a new binning model or general benchmark platform. The directory name `dl_binner` is a working name, not an architectural commitment.

## Check the documentation

With Python 3 and Pandoc available:

```sh
python3 scripts/check_docs.py
python3 scripts/check_docs.py --check-context
```

The first command validates links in maintained documents using Pandoc's Markdown parser. The second also checks the recorded local source hashes; missing optional caches are reported separately. Neither runs a scientific experiment or validates a paper's claims.

The research record is maintained in Git. See [the current state](docs/STATE.md) for branch and remote status.

The experimental [first binner package](docs/PROTOTYPE.md) and
[E004 integration record](experiments/E004-first-binner/README.md) describe the
current software implementation and its validation limits.
