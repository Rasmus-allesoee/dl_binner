Read AGENTS.md, PROJECT_INTENT.md, and docs/STATE.md. Continue with the next task described in E001 and STATE: implement E001 Gate 0 and prepare Gate 1.

Before implementing, reassess the current E001/D003 choices in light of my comments below. Use your own judgement, especially regarding:

- CAMI II Marine versus a human-microbiome dataset;
- BWA-MEM2 versus alternative mappers;
- GPU assumptions, CPU/RAM requirements, and the available HPC budget.

Do not treat the existing dataset, mapper, or resource choices as final. Keep E001’s diagnostic purpose in view, and update the protocol and research records if your assessment changes any of them. If you retain the current choices, briefly explain why.

Then implement the appropriate Gate 0 work: the minimal validation harness, native-tool adapters, evaluator tests, and smoke checks. Run portable checks locally, clearly identify native checks that require UCloud, and prepare fresh download and inventory instructions for the selected dataset.

Do not begin scientific training or bulk downloads yet. Maintain the research documentation and commit the completed local work.

When finished, report back to me **in the chat** with:

1. A summary of what you did and decided;
2. Main files created or changed that I should read;
3. The exact next step;
4. What you need from me;
5. A short prompt I should send to you to begin that next step.

My comments/notes:
## Dataset:
Why use the CAMI II Marine dataset rather than a human-microbiome dataset? Remember that the original intent of this project was to strengthen my path toward computational biology, biomedical AI and human health. I don't want to work with environmental stuff. Therefore, wouldn't the optimal dataset be from the human-microbiome? A good dataset could be https://cami-challenge.org/datasets/toy-human-microbiome-project/.

## Mapping:
You suggested `bwa-mem2`. Why exactly this tool? What about bowtie2, strobealign, or minibwa? 

From what I've heard, strobealign should be 3× to 7× faster than bwa-mem2 and 10× to 15× faster than Bowtie2, while cutting memory usage in half. Bowtie2 should have a modest RAM footprint.  Minibwa is the successor of bwa-mem with a different algorithm – it is over three times as fast as the original bwa-mem and twice as fast as bwa-mem2 at comparable accuracy. Bwa-mem2 is also strong but should be very RAM hungry.

I personally only have experience with bowtie2.

## HPC budget:
These are my current access and budget:
* 1-128 vCPU (AMD EPYC 9535) 3-384 GB RAM (DDR5-6000)
* 2.1K CPU core-hours (where 1 hour use of a machine with 1 vCPU consumes 1 core-hour. Machine with 128 vCPU would use 128 core-hours per 1 hour).
* No access to GPU
* Storage: 250 GB. Can likely get access to up to 10 TB easily though.