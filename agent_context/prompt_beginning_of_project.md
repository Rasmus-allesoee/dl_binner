Read AGENTS.md and PROJECT_INTENT.md first, then inspect the relevant material in agent_context/ so you understand my thesis work, background, motivation, and the overall goal of this project. Historical documents under docs/history/ are useful context, but they are explicitly not current requirements or a roadmap you must follow.

You are now taking over as my primary research engineer and technical guide for this project.

Our ultimate goal is to develop and rigorously benchmark our own novel metagenomic binning method, with the ambition of reaching SOTA-level performance or making a meaningful methodological advance. I also want to develop a strong conceptual understanding of deep learning through the actual research process, with explanations and small learning experiments introduced when they become relevant rather than through a predetermined curriculum. You will do the coding and detailed technical work; do not expect me to manually implement things.

Start by independently assessing the project and determining what you think we should do next.

Use your own reasoning rather than simply following our old ideas. Consider what we already know from my thesis, what we still need to understand about the current binning landscape, and what the strongest path toward a novel method would be.

Before substantial research or model implementation begins, also establish a strong information and documentation architecture for the repository. This may become a large and complex research project, so we need a robust, coherent, and maintainable system that allows its knowledge, reasoning, experiments, and decisions to accumulate without becoming fragmented or contradictory over months or years.

I do not want to prescribe the exact structure myself. After inspecting the repository and context, design and implement the structure you think will work best for you and future agents.

It should make it easy to determine, at minimum:

* the current state and immediate research direction;
* active questions and hypotheses;
* important decisions and their reasoning;
* experiments that have been run, including relevant configurations, results, and conclusions;
* literature, methods, and existing tools that have been investigated;
* failed experiments, negative results, abandoned ideas, and why they were abandoned;
* unresolved questions and uncertainties;
* which information is current versus historical or superseded;
* how research reasoning, code, data, experiments, and results relate to one another;
* what another agent needs to know to continue the project without reconstructing its history.

Preserve superseded hypotheses, abandoned directions, negative results, and failed experiments as research history while keeping the currently active state and direction unmistakably separate.

Keep this system structured and consistent, but avoid documentation bureaucracy. Prefer clearly defined, well-maintained sources of truth with minimal ambiguity or unnecessary overlap. Organize and split information however you judge will scale best as the project grows over time.

For this first task:

1. inspect and understand the existing repository and context;
2. assess what you believe the strongest immediate research direction is and why;
3. consider serious alternative next steps;
4. identify what we need to establish or investigate before designing our own method;
5. design and implement the initial repository/documentation framework you think will best support the long-term research project;
6. populate it with the useful information we genuinely know now, rather than inventing detailed future plans merely to fill documents;
7. finish by explaining the resulting structure, your assessment of the project, and what you recommend we do next.

Do not begin major model implementation yet. The purpose of this first task is to understand the problem, establish a durable research foundation, and determine the strongest next scientific step.

From this point onward, actively maintain the project's documentation as the research evolves. When evidence changes our decisions, hypotheses, priorities, or direction, update the appropriate current information while preserving useful history, so future agents inherit the latest understanding rather than a pile of contradictory plans.

Treat Git and GitHub as part of the project's research infrastructure when designing the foundation. The evolution of code, documentation, experiments, decisions, and important research milestones should remain traceable over time. Decide how version control and appropriate GitHub features should support this project as it scales, without imposing unnecessary workflow ceremony.

Treat this as an open research problem. The destination is fixed; the route is not.

Take the lead from here.