Read AGENTS.md, PROJECT_INTENT.md, docs/STATE.md, and the current E001 operations guide. Continue from the current repository handoff.

I have not run anything on UCloud yet. My UCloud setup is:

- Application: Terminal
- Flavor: Ubuntu
- Version: Aug2026
- Service provider: DeIC Interactive HPC (SDU/K8s)
- CPU-only
- No GPU
- Persistent work path: /work/Home/dl_binner/e001/e001-gate0
- Access expiry: unknown

The separate per-tool environments should remain inside the experiment directory under the work path, as currently implemented. Do not move them to a shared environment directory.

Guide me through the owner-run E001 preflight one step at a time: prepare code transfer and exact commands for the mapping/AMBER synthetic checks. Tell me what to select for the UCloud machine type and job duration, then explain the code-transfer process and each command before I run it.

For every major command, explain:

- what it does;
- which files or directories it creates or modifies;
- whether it downloads software or research data;
- its expected resource use;
- what output I should return;
- when I should stop instead of continuing.

Inspect returned outputs before proceeding to GI assembly/truth inventory. Do not start scientific training or bulk read downloads.

Storage is not currently a limiting concern; I can obtain substantially more storage if needed. Do not change the E001 design merely to fit the current conservative storage estimate.

When finished, report back to me in the chat with a proper summary of what was done, the exact next step, and exactly what you need from me (your previous chat summaries and overviews have been too short and lacking information. Maintain documentation and commit completed local work.