**What Changed**
Implemented Gate 0 locally and prepared Gate 1.

- **Dataset:** switched to the gastrointestinal subset of [CAMI II HMP](https://cami-challenge.org/datasets/toy-human-microbiome-project/), aligning development with your human-health focus.
- **Mapper:** provisionally selected [strobealign 0.17.0](https://raw.githubusercontent.com/ksahlin/strobealign/v0.17.0/README.md). Bowtie2 is the comparison/fallback. Advertised speedups are not assumed to hold here; BWA-MEM2 was a conventional choice, not a scientific requirement.
- **Compute:** revised everything for CPU-only execution. COMEBin remains conditional on measured affordability. E001 has an 800-core-hour ceiling, preserving the remaining budget for subsequent research.
- **Validation:** 56 portable tests passed. Native Linux checks are prepared but **not yet run**. No scientific training or bulk downloads occurred.

The GI files also required an explicit assembly-to-truth ID conversion, now implemented with strict checks.

Committed as `a0cf055` on clean branch `e001-gate0`. Nothing was published.

**Read These**
- [D004](/Users/rasmusallesoeenielsen/Documents/dl_binner/docs/decisions/D004-human-cpu-preflight.md): decisions and alternatives.
- [E001 Protocol](/Users/rasmusallesoeenielsen/Documents/dl_binner/experiments/E001-coverage-thinning/README.md): revised experiment.
- [Operations Guide](/Users/rasmusallesoeenielsen/Documents/dl_binner/experiments/E001-coverage-thinning/OPERATIONS.md): preflight commands, limits and required outputs.

**Exact Next Step**
Prepare an **8-vCPU, 24-GB UCloud session**, run the synthetic mapping/AMBER checks, and inspect their returned outputs before acquiring the GI assembly/truth inventory.

**What I Need**
Your UCloud application name/version, persistent working-directory path, and approximate access expiry. No storage increase is needed for this initial preflight.

**Next Prompt**
```text
Read AGENTS.md, PROJECT_INTENT.md and docs/STATE.md. Guide me through E001’s owner-run UCloud preflight: prepare code transfer and exact commands for the mapping/AMBER synthetic checks. Inspect returned outputs before proceeding to GI assembly/truth inventory. Do not start scientific training or bulk read downloads. Maintain documentation and commit completed local work.
```