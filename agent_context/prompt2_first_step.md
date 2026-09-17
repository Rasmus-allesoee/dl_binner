Start the next research phase described in the repository and in your previous handoff: complete the targeted paper/code audit and design the first diagnostic experiment.

Read the current repository state and follow the existing instructions and documentation. Use your own judgement about the appropriate scope, methods, and order of work. Do not begin major model implementation or large-scale execution unless your investigation shows that this is now appropriate.

When you finish, report back to me in this chat with:

1. A concise summary of what you did and learned.
2. The exact next step.
3. What you need from me, if anything.
4. A concise copy-paste prompt I should send to you to begin that next step.

Keep the explanation clear and manageable. Do not overwhelm me with a file-by-file change log or repeat the repository structure unless it is directly relevant.

I have added some comments and feedback below. Take them into account where relevant, including my thoughts about simulations and newly added repositories:

"""
## assets.md:
### A004 Local tool source cache; STATE.md (Open dependencies):
I see that you complained about the repositories inside `agent_context/tools_repo` lacks .git metadata. This is because I downloaded them as ZIP rather than running `gh repo clone`. I have now replaced the repos for the main stand-alone binning tools with the real cloned Git repositories, which doesn't end with "-main" or "-master". The other repos are still downloaded via ZIP, as I deem this good enough.

I have also added a few new repos:
* AMBER_evaluation
* CAMISIM
* McDevol
* BBTools (contains QuickBin)
* BASALT-Air (refinement tool)
* amber_binning (binning tool for ancient DNA)
* dcvbin

### A005 Local paper cache:
Yes, mathematical expressions are missing in portions of some extracted text, so it's preferable if you can access the original research paper. I am progressively updating these poor markdown files.

New files that have been added:
* UNCERTAINGEN_paper.md
* QuickBin_paper.md (this is the newly released paper, replacing the pre-print).

Files that have been updated:
* DCVBin_2026_paper.md
* taxvamb_2026_paper.md
* completebin_paper.md
* LorBin_paper.md
* semibin2_paper.md
* genomeface_paper.md
* metabat2_paper.md
* comebin_paper.md
* vamb_paper.md

### Git and continuity:
You wrote: "No remote is configured. An authenticated lookup of Rasmus-allesoee/dl_binner on 2026-09-16 could not resolve that repository. This does not rule out another name or account."
* It's because we have not created the remote GitHub repo yet.

You wrote: "The thesis repository was inspected read-only at commit 4029b810045ff9196be0035e48e7fb32ca4be792; it was clean and had no local remote configured. Its two thesis Markdown files match this repository's copies byte for byte."
* Not sure if we need to include the thesis and all the figures in the remote GitHub repo? It's separate from this binning project and essentially just another research paper like the ones in `agent_context/papers`.

## questions.md
### Q003:
I noticed that you keep talking about creating new simulations. This is fine! However, we should also use the public available benchmark data simulations that are used as a standard by the field. One popular example of such benchmark data simulations are CAMI II and the new CAMI III: https://cami-challenge.org/about/ and https://github.com/CAMI-challenge/CAMISIM.git. The CAMI developers are also the ones that have made CAMISIM that I used to make my custom simulation for my thesis, and the ones that made the AMBER ground truth evaluation tool. So they have the full stack, making benchmarking through similations smooth and connected. However, if the AMBER evaluation framework is restricting you from making a better custom evaluation framework, then go the custom route instead.
"""