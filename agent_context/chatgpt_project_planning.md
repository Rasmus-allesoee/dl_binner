> From: https://chatgpt.com/g/g-p-6aa7b70b26488191b8331d854d385b8d-deep-learning/c/6aa7b736-1bf8-83eb-9cdc-6fcf7654b0bb#

# you asked

message time: 2026-09-14 10:58:29

I want to learn about neural networks, deep learning, and how LLM works. However, I don't want to simply read a bunch of articles online, because this will quickly make me loose motivation.

Instead I want to gain practical understanding and skills on how to train neural networks and make my own deep learning models. But I don't just want to follow a random turtorial that builds a generic project that I am not interested in.

The most optimal way to learn and stay motivated, is to find a project that actually motivates me, and this is where I need your help. Please carefully think about exciting projects/products we can build that requires training neural networks, make deep learning models, and if possible is closely related to LLMs or directly LLMs!

Having a complex deep learning project on my GitHub will also make me look interesting for future jobs.

---

# chatgpt response

The strongest project for you is likely not “build an LLM” in isolation. It is a **real multimodal biology system** where you train increasingly sophisticated neural networks yourself, then eventually connect them to an LLM. That gives you a genuine product and a natural learning ladder instead of a tutorial.

A project can be designed so that every new concept immediately improves the same product: first a tiny neural network, then CNNs, embeddings, transformers, multimodal fusion, and finally LLM/VLM fine-tuning. That is much better pedagogically than jumping straight to fine-tuning an existing LLM and letting libraries hide what is happening.

Your instinct is correct: **do not make “learning deep learning” the project. Make a product you care about, and let deep learning become the machinery required to build it.**

Given your biology background, skull collection, existing skull website, Python experience, and interest in building things that have actual value, one project stands out far above the others.

## My strongest recommendation: build a multimodal skull-identification AI

Not merely:

> upload skull → classifier says “red fox”

Build something substantially more ambitious:

> **Give the system several photographs of an unknown skull + measurements + geographic location, and have it identify the most likely species, retrieve similar reference specimens, quantify its uncertainty, and explain which morphological features support the identification.**

Eventually, it could become part of your skull website.

You have actually circled around a version of this idea before: identifying skulls using images combined with context such as location and size. I think that idea is even better as a **deep-learning learning project** than merely as a website feature. 

I'd tentatively call the project **SkullNet** below.

---

# Why SkullNet is unusually good for learning deep learning

The beautiful thing is that we can make the project grow alongside your knowledge.

You don't need to learn neural networks for three months and *then* start the interesting project.

Your progression can instead look like this:

```text
Skull measurements
       ↓
small neural network
       ↓
skull photographs
       ↓
CNN
       ↓
learned visual embeddings
       ↓
Vision Transformer
       ↓
multiple skull views
       ↓
multimodal transformer
       ↓
location + measurements + images
       ↓
contrastive image/text learning
       ↓
LLM
       ↓
vision-language skull identification model
```

Each stage gives you a working model.

And almost every major deep-learning concept naturally appears somewhere along the way.

---

# Phase 1 — Build your first neural network yourself

Start absurdly simple.

Input:

```text
skull length
skull width
skull height
mandible length
cranium width
...
```

Output:

```text
fox       0.72
badger    0.17
raccoon   0.08
other     0.03
```

Build a tiny multilayer perceptron in PyTorch.

Something conceptually like:

```text
11 measurements
      ↓
Linear(11 → 32)
      ↓
ReLU
      ↓
Linear(32 → 32)
      ↓
ReLU
      ↓
Linear(32 → species)
      ↓
Softmax
```

But rather than treating this as boilerplate, I would want you to implement the training loop yourself and understand every line.

You'd learn:

**tensors → parameters → forward pass → loss → gradients → backpropagation → optimizer → epochs → batches → validation**

That is basically the foundation underneath modern deep learning.

PyTorch's current tutorials still expose exactly these primitives—`Dataset`, `DataLoader`, `nn.Module`, autograd, loss functions and optimizers—so we don't need some artificial educational framework around it. ([PyTorch Documentation](https://docs.pytorch.org/tutorials/?utm_source=chatgpt.com))

And importantly:

**No MNIST. No iris flowers. No generic tutorial dataset.**

Your skull project starts on day one.

---

# Phase 2 — Teach a neural network to see skulls

Now things become much more interesting.

Create a dataset such as:

```text
red_fox/
badger/
raccoon_dog/
roe_deer/
otter/
mink/
...
```

with lateral, dorsal and ventral skull photographs.

First train a small **CNN from scratch**.

That teaches you what convolution actually does:

```text
pixels
 ↓
edges
 ↓
textures
 ↓
local structures
 ↓
teeth / orbit / sagittal crest / rostrum
 ↓
species prediction
```

You can inspect intermediate feature maps and literally see what the network learns.

Then compare your hand-built CNN against a pretrained image model that you fine-tune.

That gives you a legitimate experiment:

> How much does transfer learning improve skull identification over a CNN trained from scratch?

Already Github-worthy.

---

# Phase 3 — Stop treating identification as simple classification

This is where the project starts becoming significantly more sophisticated.

Instead of teaching:

```text
image → species
```

teach the neural network:

```text
image → embedding
```

Perhaps:

```text
badger skull     → [0.13, -0.42, 0.73, ...]
fox skull        → [0.61,  0.20, -0.11, ...]
wolf skull       → [0.57,  0.16, -0.06, ...]
```

The neural network learns a **morphological space**.

Similar skulls should lie near each other.

You could then visualize it:

```text
              wolf
                •
             fox •
                 \
                   • raccoon dog


                       • badger
```

Suddenly you are learning:

- embeddings
- representation learning
- cosine similarity
- metric learning
- triplet loss
- contrastive loss
- dimensionality reduction
- nearest-neighbour retrieval

And your website could have:

> **Find morphologically similar skulls**

which is far more interesting than a classifier.

---

# Phase 4 — Let it use multiple photographs

A competent human doesn't identify a skull from a single random photograph.

You might provide:

```text
lateral
dorsal
ventral
frontal
```

Each image passes through the image encoder:

```text
lateral ──→ encoder ──→ embedding ─┐
dorsal  ──→ encoder ──→ embedding ─┤
ventral ──→ encoder ──→ embedding ─┤→ fusion model → species
frontal ──→ encoder ──→ embedding ─┘
```

Now you have a genuinely **multimodal/multi-view architecture**.

The fusion model could initially just average embeddings.

Later, replace that with attention:

```text
                  ┌ lateral embedding
                  ├ dorsal embedding
Transformer  ←────┼ ventral embedding
                  └ frontal embedding
```

The transformer learns which views matter for a particular identification.

That is your first natural introduction to **attention**.

And attention is the core idea underlying LLMs.

---

# Phase 5 — Add biological context

Now SkullNet becomes something considerably more unusual.

Suppose the image alone gives:

```text
Species A: 44%
Species B: 41%
Species C:  8%
```

But we also know:

```text
skull length: 142 mm
latitude: 55.4
longitude: 10.4
country: Denmark
```

Create separate neural-network branches:

```text
                skull images
                     ↓
                image encoder
                     ↓
                visual embedding
                     │
                     │
measurements → MLP ──┤
                     ├──→ fusion network → prediction
location ─→ encoder ─┤
                     │
taxonomy ─→ embedding┘
```

Now you're learning **multimodal deep learning**.

This also solves a real biological problem.

If SkullNet sees something visually compatible with both:

> *Vulpes vulpes*

and some morphologically similar species that does not occur anywhere near Denmark, the geographic information should affect the posterior probability.

That's far closer to how an expert actually identifies specimens.

---

# Phase 6 — Train a CLIP-like skull model

This is where we start approaching the conceptual world of modern foundation models.

Instead of just training:

```text
image → species label
```

give it pairs:

```text
[skull photograph]

"The European badger has a broad cranium,
large sagittal crest..."
```

Train:

```text
Image encoder ─────────→ embedding
                            ↑
                         similarity
                            ↓
Text encoder ──────────→ embedding
```

The model learns to place matching images and descriptions near each other.

That's essentially the central idea behind **contrastive image-language models such as CLIP**: learn a joint representation of images and natural-language descriptions. ([OpenAI](https://openai.com/index/clip/?utm_source=chatgpt.com))

That opens some extremely cool capabilities.

You could search:

> skull with very pronounced sagittal crest and short rostrum

without having explicitly programmed those categories.

Or:

> show me skulls morphologically similar to *Meles meles*

This is starting to look like real machine-learning research rather than a tutorial.

---

# Phase 7 — Build a tiny GPT yourself

I would make this a **side project inside the main project**.

Don't try to make ChatGPT.

Make something ridiculously small.

Perhaps:

**SkullGPT-10M**

Train it on taxonomic/morphological text.

But implement the important parts yourself:

```text
text
 ↓
tokenizer
 ↓
token IDs
 ↓
token embeddings
 ↓
positional information
 ↓
self-attention
 ↓
MLP
 ↓
transformer block
 ↓
...
 ↓
next-token probabilities
```

Then train it using:

```text
"the red fox skull has a relatively slender..."
                                     ↓
                                  predict
                                   "rostrum"
```

You would learn directly:

- tokenization
- embeddings
- queries
- keys
- values
- attention matrices
- causal masking
- multi-head attention
- transformer blocks
- residual connections
- layer normalization
- cross-entropy
- next-token prediction
- sampling
- temperature
- context windows

At that point, statements such as

> "an LLM is a decoder-only transformer trained with next-token prediction"

will no longer be abstract knowledge.

You'll have built one.

It will probably produce terrible text.

That's fine.

**The point is that you'll understand why GPT works.**

---

# Phase 8 — Fine-tune a real LLM

Only after building the little one would I move toward existing large models.

Take an open pretrained model and teach it skull-specific behaviour.

For example:

```text
User:
I have a skull measuring 146 mm.
Dental formula...
Found in Denmark.
What should I inspect?

Model:
Examine the following structures...
```

Rather than modifying billions of pretrained parameters, you can use parameter-efficient fine-tuning such as **LoRA**, which freezes most of the original model and trains small low-rank matrices. Hugging Face's current PEFT tooling is explicitly designed to make this kind of LLM adaptation feasible with far less memory and computation. ([Hugging Face](https://huggingface.co/docs/peft/index?utm_source=chatgpt.com))

Now concepts like:

```text
base model
fine-tuning
LoRA
rank
quantization
QLoRA
instruction tuning
```

actually mean something.

---

# Phase 9 — The crazy final version: a skull VLM

This is the version I find most exciting.

Make your image encoder communicate with an LLM.

Conceptually:

```text
             SKULL IMAGES
                   ↓
             Vision encoder
                   ↓
           visual embeddings
                   ↓
            projection layer
                   ↓
                   ↓
"What species?" → LLM → "Most likely Vulpes vulpes..."
```

Then add:

```text
measurements
location
collection database
reference specimens
taxonomic descriptions
```

Eventually:

> **Upload four photographs of an unknown skull.**

SkullNet responds:

> Likely *Vulpes vulpes* — 87%.
>
> The elongated rostrum, relatively narrow zygomatic width and carnassial morphology are consistent with *Vulpes*. The skull length of 142 mm further supports this identification. *Nyctereutes procyonoides* remains the second candidate.
>
> Here are the three most similar specimens in the reference collection.

And highlights the anatomical areas influencing its decision.

That is a **vision-language model applied to zoological identification**.

Now your GitHub repository isn't:

> "Fine-tuned BERT sentiment classifier."

It is:

> **Multimodal deep-learning system for taxonomic identification of mammalian skulls using multi-view computer vision, morphometrics, geographic priors and vision-language models.**

That is considerably more interesting.

---

# Even the dataset engineering would be impressive

You aren't necessarily constrained to your personal collection.

For example, Smithsonian Open Access currently exposes millions of reusable digital assets and provides both an API and bulk data; its CC0 collection includes 2D and 3D material. ([Smithsonian Institution](https://www.si.edu/openaccess/devtools?utm_source=chatgpt.com))

GBIF also exposes specimen metadata/media programmatically, although the licences of individual media need to be respected. ([techdocs.gbif.org](https://techdocs.gbif.org/en/openapi/images?utm_source=chatgpt.com))

So another whole engineering component could become:

```text
museum APIs
     ↓
download specimens
     ↓
taxonomy normalization
     ↓
licence validation
     ↓
image QC
     ↓
view classification
     ↓
dataset versioning
     ↓
training set
```

That's valuable experience in its own right.

---

# Other projects I considered

There are several that I think would suit you, but I rank them below SkullNet.

| Project | Deep learning | LLM relevance | Personal relevance | GitHub value |
|---|---:|---:|---:|---:|
| **SkullNet multimodal AI** | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| Biological tiny-LLM from scratch | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Insect species identification AI | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★★ |
| Scientific-paper reasoning/search model | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Metagenomics transformer | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| Cycling performance prediction model | ★★★★☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ |

A **metagenomics transformer** could also be extremely strong given your background, but I see a danger: it starts resembling academic work again.

An insect-identification model would be excellent too, particularly given your macrophotography, but computer-vision species identification already has many implementations.

The skull problem is much stranger.

That's an advantage.

---

# I would structure your learning around one rule

We **do not use high-level libraries to hide something until you understand what they're hiding.**

For example:

First:

```python
loss.backward()
optimizer.step()
```

and understand exactly what those operations conceptually mean.

Later use sophisticated training frameworks.

For transformers, first implement attention ourselves.

Later use Hugging Face.

For LLMs, first train the tiny garbage GPT.

Later fine-tune a billion-parameter model.

That prevents the project from becoming:

```python
model = AutoModel.from_pretrained(...)
trainer.train()
```

followed by:

> "I guess I know deep learning now."

You won't.

---

# The resulting GitHub repository could become substantial

Something like:

```text
skullnet/
│
├── data/
│   ├── ingestion/
│   ├── taxonomy/
│   └── validation/
│
├── skullnet/
│   ├── nn/
│   │   ├── mlp.py
│   │   ├── cnn.py
│   │   ├── attention.py
│   │   └── transformer.py
│   │
│   ├── vision/
│   ├── multimodal/
│   ├── language/
│   └── evaluation/
│
├── experiments/
│   ├── 001_measurements_mlp/
│   ├── 002_cnn_from_scratch/
│   ├── 003_transfer_learning/
│   ├── 004_metric_learning/
│   ├── 005_multiview/
│   ├── 006_multimodal/
│   ├── 007_clip/
│   ├── 008_tiny_gpt/
│   └── 009_vlm/
│
├── notebooks/
├── tests/
├── app/
│
└── README.md
```

And the README would document the progression from your first neural network all the way to the final architecture.

That progression itself becomes part of the portfolio:

**"I didn't merely call an AI API. I built the components to understand them."**

---

## Where I think we should actually begin

I would **not start coding SkullNet yet**.

Our first task should be designing **SkullNet v0.1**, particularly the dataset, because available training data determines what is realistically possible.

Then I'd make your first deep-learning milestone deliberately small:

> **Train a neural network that identifies a limited set of mammalian species from skull morphology, while implementing the PyTorch training process ourselves.**

From there, every few steps we add one genuinely new piece of deep learning.

I can turn this into a full **project + learning roadmap**, where each stage specifies **what we build, what neural-network concept it teaches, what you implement yourself, what mathematics you need at that point, experiments to run, and the concrete GitHub deliverable**. That would effectively become your custom deep-learning course built around SkullNet rather than generic exercises.

---

# you asked

message time: 2026-09-14 15:24:42

Overall, this whole SkullNet project plan sounds excellent for learning the practical skills of deep learning and LLMs. Your proposed learning rules and progressive learning as part of the GitHub repository is very nice.

While reading your plan, I quickly wrote down my thoughts a long the way. They provide context about me, my interests, and my current situation. However, you seem to already have a good understanding about who I am, what I like, how I work, and so on.

I thought about the insect-identification AI myself. But as you correctly notice, while it is super interesting and more useful, because there will be a much larger demand due to curious naturalists taking picture of insects, there already are tons of big insect identification apps like iNaturalist, making it impossible for my AI to add any new value.

## Rant:
While this skull-identification idea is very interesting, the main downside is that skulls is a very niche subject and not something that is optimal for making commercial.

I am currently umeployed after finishing my master's degree in biology/bioinformatics. I hate the job market and all the fakeness and ass-licking involved, which is why taking the the self-employed route is most ideal for me, and it will also benefit from my obsessive working style. However, I am still open to work for companies or do research if the subject is highly motivating and touches on my deep interests that adds meaning and purpose to my existence.

## Interest:
### Personal, hobby interests:
My current personal interests, and what I spent my free-time on, are:
	1. Cycling, mostly indoor on zwift.
	2. Citizen science contributor through species identification and systematic registration of observations, mostly insects with favorite groups being weevils and moths.
	3. High-end macro photography of insects.
	4. Skull preparation and collecting.

However, these are purly hobby-based. I have little interest in turning them into something commercial for several reasons. First, they are all fairly niche, making their commercial possibilities very limited due to poor demand. Secondly, because while I enjoy doing them, they lack the deep meaning that I am seeking in life. I need a thing that deeply motivates me because it tries to solve one of the biggest human problems.

### Deep, meaningful interests:
Areas that I find deeply interesting and would love to work with are:
	1. Human health: mainly longevity and how to avoid dying to live forever.
	2. Human brain and consciousness: one of the deepest unsolved questions. We just accept the absurdity of existence and our ability to question it without answers.
	3. AI: AI has immense consequences for the future, and will likely end up being the tool to answer all the fundamental questions of the universe, consciousness, and existence.

## The 3 important aspect of life:
The 3 most important aspect of my life are: Health, Happiness, and Money. I always make sure that whatever I am doing, that activity must directly provide or lead to at least one of these aspects of life.

The utopia case is to find an activity in life that achieves all 3 aspects all-in-one. I have yet to find such thing, the main bottleneck being the money aspect. Cycling achieves health and happiness. Photography, insects, and skulls achieves happiness. I tried selling my high-end insect portrait photos as educationally posters and such, but it never got any sales despite all the positive feedback from my 8000 followers on instagram, clearly showing the weak demand.

## Ideal projects:
Now you have gotten some context about my interests and values. We should also keep in mind that a project can function as an investment or stepping stone into something bigger – not all projects provides the immediate end goal of money and happiness. Some requires years of gradual work to get to a place where it's possible to truly get close to my deep, meaningful interests.

Ideally, we find ideas to products/services/SaaS that have potential for commercial value, which if successful can earn me some money, and in the long run can provide me good income. This first project is mostly about learning neural networks, deep learning, and LLMs, and therefore it doesn't have to be strictly relevant to my deep interests. 

After this project, I will likely have developed skills that allow me to start on more specialized projects that comes closer to my interests. Or this new deep learning project on github has increased my chances of getting a research job within my deep interests! Most of the jobs I have been applying for are withing bioinformatics with focus on human health, omics, biomedicin, drug descovery, etc. 

## Conclusion:
After writing this brainstorm above, I realised that I may have gotten far ahead of myself. One doesn't usually start with a big complex project when one wants to learn a field. So maybe the skull-identification AI is not that bad of an idea, even though it's not related to my deep interests! It will allow me to slowly gain the practical skills of deep learning, because my motivation will not be drained because I find the project personally interesting. I can then use these skills to later dig deeper into other more commercially relevant areas.

Please share your opinion on the ideal product/project to build based on this newly added context about me. It may still be SkullNet, or you may have a new list of idea with some being more ideal. Once we have dialed in the ideal project, we will move over to codex and start working in a new repo.

---

# chatgpt response

The new context changes the **goal of the first project**, but not necessarily the best project. I would separate “the thing worth building now” from “the domain you ultimately want to work in,” because forcing both into one project is likely to make the first project unnecessarily difficult.

I checked the current landscape as part of this. Your instinct about insect identification is even stronger than it first appears: iNaturalist’s September 2026 model covers **123,618 taxa** and is trained from millions of observations. Competing head-on there would mostly turn the project into “rebuild a mature system with vastly less data.”

Your brainstorm actually makes me **more confident that SkullNet is the right first project**, but for a different reason than before.

The key distinction is this:

> **SkullNet should not be your attempt to find your life's work or build your first successful company. It should be your deep-learning laboratory.**

You are trying to solve two different optimization problems. Project 1 should maximize **learning × motivation × probability of completion × portfolio value**. Later projects can increasingly maximize **meaning × health impact × commercial potential**.

Trying to maximize all of them immediately would probably push you toward a biomedical project that is scientifically harder, more data-constrained, more regulated, less visually intuitive, and therefore a worse environment for learning neural networks from first principles.

## The mistake isn't starting with a big project

I would modify one thing you said.

Starting with a big project isn't necessarily a problem.

Starting with a **big first milestone** is the problem.

There's an enormous difference between:

> "I'm going to build a state-of-the-art multimodal skull VLM."

and:

> "I'm building SkullNet. Version 0.1 is a tiny neural network that learns from skull measurements."

The *vision* can be ridiculously ambitious while each implementation step stays small.

That's actually ideal for how you tend to work. There is always another layer to attack when the previous one becomes boring.

---

# I would rank the projects differently now

For **your first serious deep-learning repository**, this is approximately how I would score them:

| Project | Learning | Motivation | Feasibility | Career signal | Commercial potential | Meaning alignment |
|---|---:|---:|---:|---:|---:|---:|
| **SkullNet** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ |
| **ECG deep-learning system** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ |
| **Cancer multi-omics model** | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| **Drug-discovery model** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★★★ |
| **Biomedical LLM** | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| **Longevity predictor** | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★★* | ★★★★★ |
| **Insect identifier** | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ |

The asterisk beside longevity is important: commercially it sounds fantastic **if it actually works**. Scientifically, however, it is extremely easy to build something that produces impressive-looking predictions without actually learning something meaningful about lifespan or biological aging.

And insect identification is now an even clearer "no" as the main product. iNaturalist's September 2026 model covers **123,618 taxa** and uses millions of observations. You could absolutely learn from rebuilding a smaller version, but there is almost no strategic reason to compete with that ecosystem. ([inaturalist.org](https://www.inaturalist.org/blog/136035-the-new-computer-vision-and-geomodel-with-over-1-500-new-taxa?utm_source=chatgpt.com))

---

# Why I would still choose SkullNet

There are five characteristics that make it unusually good as **Project Zero → Project One**.

### 1. You already understand the domain

This matters more than it seems.

When the neural network behaves strangely, you won't simultaneously be asking:

> Is my ML wrong, or do I just not understand ECG physiology?

You know what a fox skull looks like. You understand measurements, teeth, morphology, age effects, orientation, damaged specimens, taxonomic similarity, etc.

That leaves your cognitive effort available for understanding the **machine learning**.

With cancer transcriptomics, you'd frequently be learning the biology, dataset conventions, statistical pitfalls and deep learning simultaneously.

---

### 2. Neural-network behaviour will be visually understandable

Suppose we learn an embedding space and see:

```text
wolf ───── fox ───── raccoon dog

        badger

                     roe deer
```

You can look at that and reason biologically about why the model structured its latent space that way.

Or we visualize attention:

```text
             high attention
                   ↓
              carnassials
                  ███
       ┌──────────────────┐
       │                  │
       │      skull       │
       │                  │
       └──────────────────┘
                  █
             sagittal crest
```

That's enormously useful for learning.

Compare that with:

```text
Gene ENSG00000141510 embedding dimension 742 = -0.381
```

Much harder to build intuition.

---

### 3. It naturally contains almost the entire deep-learning curriculum

This remains the strongest argument for SkullNet.

We don't have to artificially inject concepts into it.

Measurements naturally lead to MLPs.

Images naturally lead to CNNs.

Morphological similarity naturally leads to embeddings and contrastive learning.

Several skull views naturally lead to attention.

Images + measurements + geography naturally lead to multimodal architectures.

Morphological descriptions naturally lead to text encoders.

Image/text pairs naturally lead to CLIP-like training.

Identification explanations naturally lead to language models.

Images + language naturally lead to VLMs.

That's almost suspiciously convenient.

---

### 4. The dataset problem itself becomes valuable engineering

SkullNet is niche, but niche is actually useful here.

There isn't a polished:

```text
pip install skullnet-dataset
```

waiting for you.

We'll have to create a real data pipeline.

The Smithsonian, for example, provides specimen metadata, 2D images and 3D models, with substantial portions available under CC0 and programmatic access through its API. ([Smithsonian Institution](https://www.si.edu/openaccess/faq?utm_source=chatgpt.com))

So part of the repo could eventually become:

```text
Museum APIs
     ↓
specimen discovery
     ↓
license filtering
     ↓
taxonomy normalization
     ↓
image acquisition
     ↓
quality control
     ↓
view detection
     ↓
train / validation / test splitting
     ↓
dataset versioning
```

That's not annoying peripheral work.

That's **real ML engineering**.

And it makes the GitHub project much more impressive than a notebook trained on a perfectly prepared Kaggle CSV.

---

### 5. Nobody expects SkullNet to become a unicorn

Strangely, I consider that an advantage.

There's no pressure to contort every technical decision into:

> BUT HOW WILL WE MONETIZE THIS?

We can use the project ruthlessly for learning.

If something becomes genuinely useful, excellent.

If twenty people in the world use it, that's also fine.

Its return on investment can instead be:

```text
SkullNet
   │
   ├── deep-learning knowledge
   ├── PyTorch experience
   ├── transformers
   ├── computer vision
   ├── multimodal AI
   ├── data engineering
   ├── ML evaluation
   ├── scientific ML
   ├── deployed ML system
   ├── strong GitHub project
   └── evidence that Rasmus can actually build ML systems
                    │
                    ↓
         health / biotech / AI opportunities
                    │
                    ↓
              future products
```

That is potentially far more economically valuable than whatever revenue SkullNet itself produces.

---

# But there is one project that genuinely challenges SkullNet

**ECG AI.**

If you told me:

> "No, I want the first project to touch human health."

this would probably be my recommendation.

For example:

> **Train a deep-learning system that learns representations of 12-lead ECGs, detects cardiac abnormalities, learns embeddings of cardiac states, and eventually uses transformers/self-supervised learning.**

It has several advantages.

ECGs are signals rather than images, so you'd learn a different and highly useful branch of deep learning. There are also substantial open datasets. PhysioNet, for example, hosts open 12-lead ECG datasets, including one with more than 10,000 patients, and has run challenges specifically around automated cardiac-abnormality classification. ([PhysioNet](https://physionet.org/content/?topic=12&utm_source=chatgpt.com))

It could progress like:

```text
raw ECG
   ↓
1D neural network
   ↓
CNN
   ↓
ECG embeddings
   ↓
self-supervised representation learning
   ↓
transformer
   ↓
multimodal ECG + patient metadata
   ↓
clinical text + ECG
   ↓
medical multimodal model
```

This is **very good**.

It also immediately signals:

> biology + bioinformatics + deep learning + human health

to employers.

So why don't I rank it above SkullNet?

Because you're a beginner in deep learning *and* not an electrophysiologist.

That creates a serious danger of the project becoming:

> "The benchmark says AUROC = 0.91, therefore apparently this works."

You can learn the mathematics and engineering without developing the same intuitive understanding of what the model is doing.

I would rather attack ECG once neural networks themselves no longer feel mysterious.

---

# And then there is the project that fits your CV almost perfectly

**Multimodal cancer genomics.**

That would connect your existing bioinformatics background directly to deep learning.

Something like:

```text
RNA expression ───────────┐
                          │
DNA mutations ────────────┤
                          │
methylation ──────────────┼→ multimodal model → phenotype
                          │
clinical variables ───────┤
                          │
histopathology image ─────┘
```

Now we're talking about:

- biological embeddings
- autoencoders
- representation learning
- attention
- transformers
- multimodal fusion
- survival models
- interpretability
- feature attribution
- potentially foundation models

And the datasets are real. TCGA molecularly characterized more than **20,000 primary cancer and matched normal samples across 33 cancer types**, with genomic, epigenomic, transcriptomic and proteomic information available through the NCI ecosystem. ([Cancer.gov](https://www.cancer.gov/ccg/research/genome-sequencing/tcga?utm_source=chatgpt.com))

The NCI explicitly describes the GDC as providing harmonized genomic, clinical, biospecimen and whole-slide-image data for developing AI models. ([NCI Genomic Data Commons](https://gdc.cancer.gov/content/gdc-and-artificial-intelligence-ai?utm_source=chatgpt.com))

That makes a future repository like:

> **Multimodal Transformer for Cancer Phenotype Prediction from Transcriptomic, Genomic and Histopathological Data**

extremely relevant to the jobs you've been targeting.

But again: **after SkullNet, not instead of SkullNet.**

---

# I would actively avoid a longevity project for now

This might sound counterintuitive given how strongly the subject motivates you.

I think longevity is actually **too important to you** to make it your beginner project.

The labels are difficult.

"Biological age" itself is not a clean ground truth. Lifespan is massively confounded. Longitudinal human data are difficult to obtain. Health records introduce access and privacy issues. And many attractive datasets are controlled.

You could very easily spend months building:

> **DeepAgeNet — AI predicts biological age!**

and end up with a model primarily learning smoking status, socioeconomic variables, sex, body composition or cohort-specific artifacts.

It would *look* like you're working on longevity while providing remarkably little insight into longevity.

I'd rather come back to aging when you actually have enough ML sophistication to recognize those traps.

---

# Same argument for drug discovery

Drug discovery sounds almost perfectly aligned:

**AI + human health + potentially enormous commercial value + fundamental biology.**

Eventually, yes.

But it brings another stack of concepts:

```text
SMILES
molecular graphs
protein structure
binding affinity
ADMET
GNNs
molecular fingerprints
docking
chemical validity
experimental labels
dataset leakage
```

If you're simultaneously wondering what backpropagation does, this is unnecessary complexity.

Again:

**excellent Project 3; unnecessarily difficult Project 1.**

---

# And I wouldn't make your first project a biomedical LLM either

Despite your strong interest in LLMs.

The danger is that modern tooling makes it far too easy to accidentally learn almost nothing.

You download a model:

```python
AutoModelForCausalLM.from_pretrained(...)
```

apply LoRA, train it, and suddenly you have:

> "My biomedical LLM."

But you've skipped most of the intellectual machinery.

That's why the **tiny GPT inside SkullNet** is important.

I want you to reach the moment where you implement:

```text
Q = XWq
K = XWk
V = XWv

Attention(Q,K,V)
```

and understand why the hell multiplying those matrices allows a model to reason about relationships between tokens.

Then when we eventually use a huge pretrained transformer, it won't be magic anymore.

---

# So I now see a three-project trajectory

This is the one sequence I would actually recommend:

1. **SkullNet — learn deep learning.** Build progressively from a tiny MLP through CNNs, embeddings, attention, transformers, multimodal learning, a tiny language model, and eventually a VLM. Optimize for understanding and experimentation, not revenue.

2. **Human-health deep-learning project — specialize.** After SkullNet, choose something like ECG representation learning or cancer multi-omics. Now reuse the neural-network knowledge in a serious biomedical problem. This becomes highly relevant to biotech/research employment and starts connecting AI with the problems you actually care about.

3. **High-risk/high-value project — pursue meaning and commercial potential.** Aging/longevity, therapeutic discovery, neuroscience/consciousness, medical AI, or whatever specifically captures you once you've developed enough expertise to recognize an unsolved problem where you can genuinely contribute.

That third project is where I would start asking:

> Can this become a company?

Not SkullNet.

---

# There is also an important psychological advantage

Suppose we start with cancer genomics because it's "career optimal."

Your brain immediately knows there is an external motive:

> I'm doing this because employers will like it.

That can turn learning into work.

SkullNet has the opposite structure.

You already want to know:

> Can a network actually distinguish these skulls?

Then we encounter a problem:

> The species classifier doesn't generalize well to unusual angles.

That gives us a reason to learn augmentation.

Then:

> Closely related species are confused.

Now we have a reason to learn embeddings.

Then:

> Some anatomical views matter more than others.

Now attention becomes useful.

Then:

> Measurements would help.

Now multimodal fusion becomes useful.

Then:

> Could the model understand morphological descriptions?

Now transformers become useful.

**The technical concepts arrive because you need them.**

That is exactly the learning environment you originally said you wanted.

---

# One modification I would make to the original SkullNet concept

I would **not design SkullNet as a skull-identification app first**.

I'd design the repository as an **experimental deep-learning system whose scientific problem is skull identification**.

That distinction matters.

Instead of spending two weeks making beautiful React upload components, authentication, accounts and deployment, we'd spend that effort asking things like:

```text
Does normalization improve the morphometric MLP?

What happens when we remove skull length?

Can a CNN trained from scratch generalize?

What changes with transfer learning?

What does the embedding space look like?

Does contrastive learning cluster genera?

Does adding geographic information improve calibration?

Can attention correctly combine lateral + dorsal views?

Can the model recognize specimens it has never seen before?

Does the network rely on biologically sensible regions?

What happens under distribution shift?
```

Every one becomes a documented experiment.

That is **much better GitHub material** than merely shipping an interface.

Your existing skull website can eventually become the frontend if we reach something worth deploying.

---

## My recommendation

I would commit to **SkullNet**.

But mentally rename its purpose:

> **SkullNet is the vehicle through which I learn modern deep learning from first principles, culminating in multimodal transformers and vision-language models.**

Commercial success is explicitly **not a success criterion**.

Success means that at the end you can look at the architecture of something like GPT, CLIP or a modern multimodal model and no longer see a mysterious black box—you understand the constituent ideas because you've implemented smaller versions yourself.

And because the entire process lives in one clean repository with proper experiments, tests, documentation, datasets and progressively more sophisticated models, the repository simultaneously becomes evidence for a future employer or research group that you did substantially more than complete an online ML course.

After that, I would currently put **cancer multi-omics / biomedical multimodal AI** at the top of the list for Project 2, with **ECG representation learning** as a close alternative. Those bring you directly into human health using public real-world data without yet forcing us into the much murkier scientific problems surrounding true longevity.

So I think your original idea survived the extra scrutiny: **build SkullNet first. Use it to become dangerous with deep learning. Then point those skills at problems that actually matter to you.**

---

# you asked

message time: 2026-09-14 21:50:07

https://github.com/Rasmus-allesoee/hadal-binning-benchmark.git
You have me convinced to start with SkullNet! Below are various thoughts that popped up in my head while and after reading your answer.

## ECG AI:
Not super interested in ECG, but I definitely see the appeal for this human health-oriented project. The main downside is that there are likely many highly specialised AI tools build for this, so the commercial value is probably not high. But it's good as a beginner project, although worse than skullnet.

## Three-project trajectory:
This sounds like a fantastic plan! 

## Conclusion:
I agree that we should make the SkullNet project to start with to learn the field. After this or when I feel comfortable, we go all in on a bioinformatic deep learning project in the field of human health, biomedicine, drug discovery, longevity, genes, diseases and omics. 

The goal of this project should be to create a product/project on github that future biotech/biomedical companies or research insitutions simply can't ignore, thereby giving me a higher change of landing a job, and getting one step closer to answer some of the fundamental questions that drive me – SOLVE HUMAN DEATH!

The main reason I can't get a job at the moment, is because I technically just have a flawlessly graded MSc degree in "classical biology" with no professional experience in bioinformatics. So I will always end up quickly being screened out in favour of people who have a MSc degree in bioinformatics or biomedical informatics. My only way to sneak through the small opening in the door to human health, drug discovery and longevity research, is to work hard and make my independent project at home to prove my skills and insane work ethics!

## Note on metagenomics:
Just wanted to also share my MSc thesis so you have some context of what I did (see the github link). Metagenomics is the only field in omics where I already have a strong foundation through my thesis work. So in theory, we could make a complex project by building our own metagenomic binning algorithm! Since I already have the foundation, it allows us to directly scale the project into some high-end complex stuff, rather than some more basic human health projects, later leading to complex human health stuff.

I have thoroughly benchmarked all the SOTA binning algorithms, so we could look at the architecture and algorithms of all the SOTA deep learning binning algorithms (freely available on GitHub) and take the best parts to build or very own. Then I can easily run it through benchmarks in the end, because I know all about benchmarking.

The only question about this direction, is that metagenomics may not be super relevant to human health and that stuff. But it may still be relevant and transferable enough for biotech/health companies and research units to see my capabilities and this increase my change of being hired or at least noticed. And the fact that I already have spend 1 full year building a strong foundation is also highly valuable (if it's relevant…).

---

# chatgpt response

Your metagenomics idea changes my view of the **second** project substantially. Because you already understand binning, benchmarking, workflow engineering, and the failure modes of existing tools, a new binning method would not be “another beginner ML project”; it could start much closer to a genuine research-engineering contribution. I’m checking your benchmark repository and the current binning landscape before judging how strong that bridge into biomedical AI really is.

Your repository confirms that the existing foundation is much stronger than “I used a few metagenomics tools.” The main benchmark alone has a **129-rule Snakemake workflow, 11 binners, three multi-sample strategies, strain simulations, ensemble analysis, quality/chimerism/taxonomy evaluation, and computational-efficiency analysis**.  That materially changes the opportunity cost of walking away from metagenomics after SkullNet.

There is also an important update in the field that makes the bridge stronger than I expected: **TaxVAMB was published in Nature Biotechnology in April 2026** and reports its largest gains specifically on human-microbiome data by combining abundance/composition with taxonomic information in a semi-supervised bimodal VAE.  Meanwhile, a 2026 preprint, **BiomeGPT**, applies a transformer foundation model to 13,300+ human gut metagenomes across 32 phenotypes.  Metagenomics is therefore not merely transferable to biomedical AI; one branch of it already sits directly inside precision medicine and human-health foundation-model research.

Yes. With this added context, I would now **change the three-project trajectory slightly**.

I no longer think the best sequence is simply:

> SkullNet → generic biomedical DL project → ambitious health project.

I think your existing metagenomics work gives you an unusually valuable shortcut:

> **SkullNet → research-grade deep-learning metagenomics method → ambitious human-health/biomedical AI**

That middle project could be far stronger for you than another conventional biomedical portfolio project.

## Your metagenomics background is more valuable than you are giving it credit for

I inspected the repository. This is not a superficial MSc bioinformatics project. You already built a reproducible benchmark covering **11 binners, three multi-sample binning strategies, strain-resolution simulations, ensemble methods, taxonomic evaluation, chimerism, quality assessment and computational efficiency**. The main real-data workflow alone contains 129 Snakemake rules, 24 helper scripts and 15 software environments.  

That means you already possess something extremely valuable:

**domain-specific taste.**

A beginner can learn PyTorch syntax fairly quickly. It takes much longer to understand:

- what a MAG actually represents;
- why strain heterogeneity causes problems;
- when abundance profiles help;
- why multi-sample binning behaves differently;
- how contamination/completeness metrics can mislead;
- how dereplication affects conclusions;
- why real and simulated benchmarks disagree;
- what computational costs actually matter;
- what constitutes a fair binner comparison.

You've already spent a year acquiring that.

Throwing it away after learning deep learning would be strategically wasteful.

---

# And metagenomics is much closer to human health than “marine microbes” makes it feel

The domain **metagenomics** is not inherently environmental.

Your thesis happens to use hadal sediment metagenomes.

The same fundamental computational problem applies to:

```text
Atacama trench
      ↓
metagenomic reads
      ↓
assemblies
      ↓
contigs
      ↓
MAG recovery
```

and:

```text
human gut
      ↓
metagenomic reads
      ↓
assemblies
      ↓
contigs
      ↓
MAG recovery
```

The biological question changes radically; much of the underlying computational machinery does not.

Human-microbiome metagenomics is already tied to diagnostics, patient stratification, antimicrobial resistance, therapeutic development, immunology, metabolism and disease research. Recent reviews explicitly discuss metagenomics as part of precision medicine and microbiome-derived therapeutics. ([PubMed Central (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12562794/?utm_source=chatgpt.com))

There are even direct connections with areas you mentioned. The gut microbiome is being studied as a therapeutic target in **cancer immunotherapy**, and microbial metabolism contributes to individual variation in **drug response**. ([Nature](https://www.nature.com/articles/s41573-025-01211-7?utm_source=chatgpt.com))

So the path is not:

```text
deep-sea metagenomics

        HUGE GAP

human medicine
```

It's more like:

```text
environmental metagenomics
          │
          │ same computational foundations
          ↓
human microbiome
          │
          ↓
host–microbe biology
          │
          ├── immunology
          ├── cancer
          ├── metabolism
          ├── pharmacology
          ├── neurological disease
          └── precision medicine
```

That is a legitimate bridge.

---

# Building your own binner could be an exceptionally strong Project 2

This part of your idea I like a lot.

Once SkullNet has taught you deep learning, you would enter the next project with two separate skill sets:

```text
          Deep learning
          from SkullNet
               │
               ↓
        ┌──────────────┐
        │ NEW BINNER   │
        └──────────────┘
               ↑
               │
   1 year of metagenomic
  binning + benchmarking
```

That intersection is where things become interesting.

And the current binning landscape is basically a miniature deep-learning curriculum already.

| Binner / approach | Important ML idea |
|---|---|
| VAMB | variational autoencoder |
| SemiBin2 | self-/semi-supervised deep learning, Siamese networks |
| COMEBin | multi-view contrastive learning |
| GraphMB | graph neural networks + assembly graphs |
| CompleteBin | transformer/genome-language-model embeddings + contrastive learning |
| TaxVAMB | semi-supervised multimodal VAE + taxonomy |

VAMB learns latent representations from composition and abundance. ([GitHub](https://github.com/RasmussenLab/vamb/blob/master/README.md?utm_source=chatgpt.com)) COMEBin constructs multiple augmented contig views and uses contrastive learning before graph/community clustering. ([GitHub](https://github.com/ziyewang/COMEBin?utm_source=chatgpt.com)) GraphMB incorporates assembly-graph structure using graph neural networks. ([OUP Academic](https://academic.oup.com/bioinformatics/article/38/19/4481/6668279?utm_source=chatgpt.com)) CompleteBin pushes toward transformers, pretrained genome-language-model information and dynamic contrastive learning. ([Sciety](https://sciety.org/articles/activity/10.1101/2025.04.20.649691?utm_source=chatgpt.com))

And the field has already moved since your thesis.

**TaxVAMB was published in Nature Biotechnology in April 2026.** It uses a semi-supervised bimodal VAE combining sequence/abundance information with hierarchical taxonomic information, and reports particularly large gains on human-microbiome datasets. ([Nature](https://www.nature.com/articles/s41587-026-03098-0?utm_source=chatgpt.com))

That is practically screaming:

> "Rasmus, there is a natural bridge from your thesis into modern biomedical deep learning."

---

# But I would change one part of your proposed strategy

I wouldn't begin with:

> Let's inspect all SOTA binners, steal the best component from each and combine them.

That sounds sensible but often produces a Frankenstein architecture without a scientific reason for existing.

Instead:

### Study the architectures → identify a failure mode → formulate a hypothesis → build the architecture needed to test it.

For example, after SkullNet we might discover one of these:

```text
Problem:
Closely related strains are merged.

Hypothesis:
Existing representations fail to retain information
needed for strain-level discrimination.

Question:
Can another representation-learning objective preserve it?
```

Or:

```text
Problem:
Short low-abundance contigs are poorly binned.

Hypothesis:
TNF + abundance become unreliable as contigs shorten.

Question:
Can sequence-language-model embeddings provide useful
information where engineered composition features fail?
```

Or:

```text
Problem:
A model trained/optimized on one environment transfers poorly.

Hypothesis:
The latent representation contains environment-specific
information rather than genome-specific information.

Question:
Can domain-invariant representation learning improve
cross-biome generalization?
```

Or:

```text
sequence
       \
abundance ----\
               \
taxonomy --------> learned multimodal representation
               /
gene content --/
             /
assembly graph
```

Perhaps an adaptive model can learn **when to trust each modality**, rather than concatenating everything indiscriminately.

Those are examples, not yet recommendations. We'd do a proper literature/code review first because several obvious combinations have already been attempted.

---

# Your benchmarking experience gives you another major advantage

A lot of ML portfolio projects stop here:

> My model got accuracy = 94%.

You could do something much closer to real computational biology research.

Your existing infrastructure already handles independent evaluation using tools such as CheckM2, GTDB-Tk, GUNC, dRep and skani. 

So a future project could become:

```text
                    OUR MODEL
                        │
                        ↓
                predicted MAGs
                        │
        ┌───────────────┼──────────────┐
        ↓               ↓              ↓
    simulated          CAMI       real datasets
        │               │              │
        └───────────────┼──────────────┘
                        ↓
                independent QC
                        │
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
 completeness      contamination     chimerism
       ↓                ↓                ↓
 strain recovery   taxonomic novelty   runtime
       │                │                │
       └────────────────┼────────────────┘
                        ↓
                 SOTA comparison
```

Then proper:

- ablations;
- multiple random seeds;
- hyperparameter controls;
- runtime/VRAM/RAM analysis;
- simulated ground truth;
- real data;
- environment transfer;
- strain-level evaluation;
- statistical comparisons;
- reproducible workflows.

That's considerably closer to a paper than a portfolio demo.

A 2025 independent evaluation of modern deep-learning binners is also interesting here: it found SemiBin2 and COMEBin among the strongest overall, but importantly, **better embedding quality did not always translate into better final binning**. Workflow and clustering decisions mattered considerably. ([PubMed Central (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12636519/?utm_source=chatgpt.com))

That's exactly the sort of nuance your previous benchmarking experience lets you exploit.

---

# We can make the project explicitly biomedical

This is the crucial strategic modification.

I would **not** make the second project:

> "A better binner for hadal sediments."

Your existing thesis already proves that competence.

I'd make it something closer to:

> **Deep representation learning for metagenome-assembled genome recovery, with particular emphasis on complex human microbiomes.**

Benchmark it on both:

```text
CAMI ground-truth datasets
          +
human gut metagenomes
          +
environmental metagenomes
```

That gives you two valuable claims simultaneously:

**Methodological:**  
The algorithm generalizes across metagenomic environments.

**Career:**  
You have applied modern deep learning to human microbiome genomics.

And because you know environmental data extremely well, environmental datasets become your **out-of-distribution/generalization test** rather than a liability.

That's actually elegant.

---

# We could potentially go one step beyond binning

This is where I think the long-term trajectory gets particularly interesting.

Imagine Project 2 eventually produces a useful learned representation:

```text
contig
   ↓
DNA transformer / encoder
   ↓
latent biological representation
```

Why should that representation only be useful for binning?

Perhaps later:

```text
             contig representation
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
     binning      taxonomy     gene/function
                                   ↓
                               phenotype
```

Or at community level:

```text
human gut metagenome
          ↓
microbial representations
          ↓
community representation
          ↓
     host phenotype

      healthy
      IBD
      cancer
      treatment response
      etc.
```

This isn't science fiction. A 2026 preprint called **BiomeGPT** pretrained a transformer on more than 13,300 human gut metagenomes spanning 32 phenotypes to learn microbiome representations and then fine-tuned those representations for health/disease prediction. ([BioRxiv](https://www.biorxiv.org/content/10.64898/2026.01.05.697599v1?utm_source=chatgpt.com))

So metagenomics could eventually be the path through which you encounter **foundation models + human disease**.

That suddenly aligns quite well with your long-term direction.

---

# What this could do for your employment problem

I would also reframe one statement you made.

You don't merely have to persuade an employer that:

> "Although my MSc says Biology, I can also code."

Your portfolio could eventually tell a considerably stronger story:

```text
BSc/MSc Biology
      ↓
computational MSc thesis
      ↓
large reproducible metagenomic benchmark
      ↓
independent deep-learning education
      ↓
SkullNet:
implemented neural networks → CNNs → transformers → multimodal AI
      ↓
independent ML-method development
      ↓
novel deep-learning metagenomic binner
      ↓
human microbiome validation
      ↓
biomedical / health AI
```

At that point, the degree title becomes progressively less informative than the body of work.

You still can't guarantee bypassing automated CV screening. But once a technical person actually looks at those repositories, the question stops being:

> "Does this biology graduate know bioinformatics?"

and becomes:

> "Why has this person independently built and benchmarked multiple computational-biology systems?"

That's a much better problem to have.

And importantly, Project 2 would demonstrate things employers care about that SkullNet alone cannot:

**real omics data + HPC + deep learning + scientific validation + workflow engineering + biological interpretation.**

---

# So my updated trajectory is this

**Project 1 — SkullNet: learn the machinery.**

Keep everything we discussed. Start simple, implement things ourselves, progressively reach CNNs, representation learning, contrastive learning, attention, transformers, tiny GPTs and multimodal models.

Its job is to transform neural networks from magic into engineering.

↓

**Project 2 — Next-generation metagenomic deep-learning method: prove research capability.**

Return to the field where you already possess unusual domain knowledge.

Don't merely run models. **Develop one.**

Study the architecture and source code of the major binners, identify a genuine unsolved weakness, formulate a hypothesis, implement the method, perform ablations and benchmark it ruthlessly using your existing expertise.

Make human-microbiome datasets an important part of its evaluation.

If it genuinely improves something, publication becomes a realistic aspiration rather than merely a GitHub exercise.

↓

**Project 3 — Human biomedical AI: attack the domain you ultimately care about.**

Now we go hard into something such as:

- cancer multi-omics;
- human genetics;
- disease prediction;
- pharmacogenomics;
- therapeutic target discovery;
- molecular/drug representation learning;
- host–microbiome interactions;
- aging biology;
- eventually longevity.

At that point you'd no longer be entering as "a biologist trying some AI."

You'd enter with **two independent ML systems behind you and an omics-method-development project in an area you already know deeply.**

---

There is even a potentially more elegant trajectory where Project 2 gradually **turns into Project 3** rather than ending: first develop better microbial genome representations, then move from microbial genome recovery → human gut microbiome representations → host phenotype/drug-response prediction → host–microbe multi-omics. Recent work on microbiome precision medicine, cancer immunotherapy and pharmacomicrobiomics shows that this bridge is scientifically real. ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S3050632825000186?utm_source=chatgpt.com))

So I would not view that year of metagenomics as a detour from the things you ultimately care about. **It may be your strongest existing entry point into them.**

---

# you asked

message time: 2026-09-14 22:22:12

Great, glad you liked the metagenomics project idea. And you are still certain that we should still start with SkullNet instead of moving directly to building the metagenomic binning tool where I already have the foundation? And by the way, I don't think building a SOTA metagenomic binning algorithm is a simple task, so if project 3 is an independent final big project that I care about, then it may be far in the future?

Just want to be sure that I don't start on the wrong thing, potentially wasting my time (although none of this is wasting time compared to most people watching movies, gaming, or having fun with friends – I am grinding😈👹)

---

# chatgpt response

No. With everything you've now told me, I am **no longer certain SkullNet should come first**.

I think there is a stronger option: **make the metagenomic binning project the main long-term learning project, but do not begin by trying to build a SOTA binner. Build toward one progressively.**

That changes my recommendation.

The reason is simple: SkullNet was attractive because it gave us a motivating domain in which increasingly difficult neural-network concepts arise naturally. But your metagenomics background gives us almost the same advantage **while also being much more valuable for your career trajectory**.

You already understand the biological problem, existing tools, benchmarking methodology, MAG quality assessment, strain resolution, workflow design, HPC, and the weaknesses of current approaches. Your existing repository demonstrates that foundation very clearly. 

So starting completely fresh with skulls may now have a meaningful opportunity cost.

## The important distinction

I would **not** recommend:

> Day 1: "Let's invent a SOTA metagenomic binner."

That would be a bad beginner deep-learning project.

I *would* recommend:

> **Create one repository whose ultimate ambition is a novel metagenomic binner, and make the early versions deliberately simple so that the project itself teaches you deep learning from first principles.**

In other words, apply exactly the SkullNet learning philosophy to metagenomics.

Something like:

```text
Metagenomic DL project
        │
        ├── 00. Neural-network fundamentals
        │
        ├── 01. Contig feature classifier
        │
        ├── 02. Autoencoder
        │
        ├── 03. VAE
        │
        ├── 04. Learned contig embeddings
        │
        ├── 05. Contrastive learning
        │
        ├── 06. Multi-sample abundance
        │
        ├── 07. Assembly graph / GNN
        │
        ├── 08. DNA transformer
        │
        ├── 09. Multimodal architecture
        │
        ├── 10. Novel binning hypothesis
        │
        └── 11. Full SOTA benchmark
```

Now we haven't sacrificed the pedagogical progression at all.

We've simply moved it into the domain where you already have a major competitive advantage.

---

# Your first neural network could still be extremely simple

For example, before touching VAMB-style architectures, we could construct a controlled simulated dataset where contigs have known source genomes.

Your first model could literally be:

```text
Input
 ├── tetranucleotide frequencies
 ├── contig length
 └── coverage

            ↓

small MLP

            ↓

source genome
```

That's not supposed to be a useful binner.

It's an educational experiment.

You implement:

- tensors;
- train/validation/test splits;
- batches;
- forward passes;
- activations;
- loss;
- backpropagation;
- optimizers;
- learning rates;
- regularization;
- evaluation.

Exactly what SkullNet's morphometric MLP would have taught you.

Except now you're learning it using metagenomic data.

Then we deliberately remove the labels and ask:

> How can a neural network learn useful representations without knowing the genome beforehand?

Boom.

Now there is a genuine reason to learn autoencoders.

---

# Then VAMB becomes something you actually understand

Instead of beginning with:

> "VAMB uses a VAE."

and treating that as a black box, we'd first build a normal autoencoder ourselves:

```text
TNF + abundance
       ↓
     encoder
       ↓
 latent space
       ↓
     decoder
       ↓
reconstruct input
```

Plot the latent space.

Understand why reconstruction forces useful compression.

Then introduce probabilistic latent variables:

```text
             encoder
                ↓
         μ             log σ²
          \             /
           \           /
            reparameterize
                  ↓
                  z
                  ↓
               decoder
```

Then understand:

- KL divergence;
- latent distributions;
- reconstruction loss;
- the reparameterization trick;
- why VAEs behave differently from ordinary autoencoders.

Only then do we open VAMB and say:

> Right. Now let's see how the professionals used this idea for binning.

That would be an excellent learning experience.

---

# Then every SOTA binner becomes a lesson

Your thesis benchmark becomes almost like a curriculum.

You already benchmarked things such as VAMB, SemiBin2, COMEBin, GenomeFace and CompleteBin. 

Now we reverse-engineer the intellectual progression behind them.

```text
basic neural network
        ↓
autoencoder
        ↓
VAE
        ↓
representation learning
        ↓
contrastive learning
        ↓
Siamese networks
        ↓
multi-view learning
        ↓
graph neural networks
        ↓
transformers
        ↓
genome language models
        ↓
multimodal representations
```

That's an extraordinary deep-learning syllabus.

And you already have the downstream infrastructure needed to determine whether any learned representation actually improves genome recovery.

---

# This also solves one weakness of SkullNet

SkullNet was excellent pedagogically, but eventually we'd face the question:

> Where do we get enough properly labelled skull photographs?

And then potentially spend huge amounts of effort building datasets, cleaning image licensing, normalizing orientations, dealing with species imbalance, etc.

That is legitimate ML work, but it isn't particularly connected to where you ultimately want to go.

With metagenomics, you already know how to generate controlled simulation data and work with real datasets.

Your repository even has a dedicated CAMISIM strain-resolution study. 

We can exploit that.

For example:

```text
Known simulated genomes
        ↓
simulate community
        ↓
reads
        ↓
assembly
        ↓
contigs
        ↓
OUR MODEL
        ↓
predicted bins
        ↓
compare against true genomes
```

That's beautiful for learning because **we actually possess ground truth**.

---

# And yes: a genuinely SOTA binner could become enormous

I agree with your correction.

I was probably treating:

> "Project 2: build a next-generation binner"

too casually.

If we're serious about producing a method competitive with VAMB, SemiBin2, COMEBin, TaxVAMB, GenomeFace, CompleteBin, etc., that is not merely an intermediate portfolio project.

It could become a major independent research program.

It may involve:

```text
architecture research
+
dataset engineering
+
HPC
+
representation learning
+
clustering
+
graph methods
+
sequence models
+
hyperparameter optimization
+
ablation studies
+
multiple environmental datasets
+
human microbiome datasets
+
simulated ground truth
+
strain-level evaluation
+
computational profiling
+
publication-quality benchmarking
```

That's substantial.

And that's actually another argument **for starting it earlier**, not later.

Because we don't need to finish it before deriving value from it.

Version 0.1 can teach you neural networks.

Version 0.3 can teach you VAEs.

Version 0.5 can teach you contrastive learning.

Version 0.7 might already produce interesting scientific results.

Version 1.0 might eventually be something worth publishing.

---

# So I would collapse Project 1 and Project 2

This is now the trajectory I prefer:

### Project 1 — Deep-learning metagenomic binning research

**Primary objective initially:** learn deep learning.

**Long-term objective:** develop a genuinely novel binning method.

**Secondary objectives:** create an exceptional computational-biology GitHub portfolio, potentially generate publishable work, and build a bridge toward human microbiome/biomedical research.

The crucial rule would be:

> **We do not introduce a deep-learning technique merely because a SOTA binner uses it. We first understand the problem it solves, implement a minimal version ourselves, experiment with it, and only then incorporate it into the research architecture.**

That preserves everything I liked about SkullNet.

---

### Project 2 — Human biomedical AI

Once you're sufficiently comfortable with deep learning, we don't necessarily have to wait until the binner is "finished."

That's another thing I would change.

The trajectory doesn't need to be:

```text
finish A completely
      ↓
finish B completely
      ↓
start C
```

It can become:

```text
Metagenomic DL project
████████████████████████████████████████→

                Human-health project
                         █████████████████████→
```

Once you've learned enough through metagenomics, you can branch into human health while continuing binner research when interesting ideas arise.

So your fear that Project 3 could be five conceptual mountains away is unnecessary.

The projects can overlap.

---

# And metagenomics itself can gradually become Project 2

There's an even more interesting possibility.

Start with general genome binning:

```text
contig
 ↓
representation
 ↓
MAG
```

Then test on human gut metagenomes.

Then perhaps the representation becomes useful beyond binning:

```text
DNA sequences
      ↓
foundation representation
      ↓
 ┌────┼───────────┐
 ↓    ↓           ↓
MAG taxonomy   function
                 ↓
              phenotype
```

Eventually:

```text
human microbiome
       +
host genomics
       +
transcriptomics
       +
clinical metadata
       ↓
multimodal biomedical model
```

Then there's no hard boundary between your metagenomics project and human-health research at all.

It becomes a bridge.

---

# What do we lose by skipping SkullNet?

There **is** a tradeoff.

SkullNet gives much better visual intuition.

A CNN looking at skulls is immediately understandable. You can see input images, saliency maps and embedding clusters.

Metagenomic latent representations are more abstract.

Something like:

```text
z₁ = -0.382
z₂ =  1.291
z₃ =  0.044
```

is inherently harder to build intuition around.

And computer vision would expose you to CNNs much more naturally.

But CNNs are not a prerequisite for understanding LLMs or modern representation learning.

For your goals, I'd rather spend those cognitive resources learning:

**VAEs → representation learning → contrastive learning → transformers → biological sequence models**

because that path is much closer to bioinformatics and modern biological AI.

We can always make a small CNN experiment later if you want that knowledge.

---

# My recommendation has therefore changed

If you asked me **before** showing me the depth of your metagenomics background:

> SkullNet or metagenomics?

I'd say **SkullNet**.

If you ask me **now**, knowing you already spent a year deeply benchmarking genome-binning methods and built the infrastructure you've shown:

> **Start the metagenomic deep-learning project.**

Not because it is easier.

It isn't.

Because we can structure the first 10% so that it **is** beginner-friendly, while the remaining 90% gives you effectively unlimited headroom.

That's rare.

You would get:

```text
personal interest
        +
existing expertise
        +
deep-learning education
        +
bioinformatics relevance
        +
research potential
        +
publication potential
        +
human-health bridge
        +
strong GitHub portfolio
```

SkullNet mainly beats it on immediate visual fun.

For your stated goals, that isn't enough to justify the detour.

And no, I wouldn't consider SkullNet wasted time. But **opportunity cost is real even when you're doing productive things**. You could spend 500 productive hours on something useful when those same 500 productive hours could compound an existing year of specialist knowledge into something much rarer.

That is the deciding factor for me.

**I would shelve SkullNet—not kill it—and make the new metagenomic deep-learning/binner repository our main project.** The next thing we should do is design its learning/research architecture before Codex writes a single line: what knowledge we build from scratch, what early toy experiments we run, what parts of your existing benchmark we can reuse, and where the boundary lies between *learning exercise* and *novel research*.

---

# you asked

message time: 2026-09-15 11:11:01

I like this idea of starting with the ambitious project of creating our own SOTA metagenomic binner, as it feels the most natural continuation of my strong thesis work. The SkullNet is still an exciting project, but I can leave that as a more personal, fun, hobby project for later.

And you know me well by now; I can work harder than anyone and am always up for a complex problem to solve – the harder and more ambitious, the better!

I actually still have access to the Ucloud HPC of my old university! This makes this project even more relevant to do first before I loose access to machines with 2 TB of ram, 64 cpus and H200 gpus.

## What do we lose by skipping SkullNet?:
I agree that the visual intuition that can be gained from SkullNet is highly valuable. To be fair, if I didn't have to think about future jobs, then I would without a question have selected SkullNet, beause the process of building this product is more exciting, rewarding and fun to me. So my gut wants to build SkullNet, but my brain says SOTA binner.

The progressive learning program from CNN to multimodal transformer to CLIP to LLM to final VLM is very intriguing, and so is the dataset engineering aspect. The SkullNet project is definitely ideal for learning the basics about deep learning and LLMs, and it can keep my highly motivated throughout. But I agree that the SOTA binning project is likely much more fruitful for bio jobs, and most importantly, it takes direct advantage of 1 year of relentless learning about the complex field of metagenomics.

The SkullNet project is too interesting to ignore, so we will should preserve it as a hobby project that I can build later or on the side! It may be that I end up switching to this project if I loose all motivation for the sota binner project.

## Vague broad vs deep concentrated knowledge:
One argument against the metagenomic route is that it just gives me more specialized, deep knowledge within a field that I already know. My thesis is likely already enough to show employers that I can do metagenomics, so on paper it doesn't make me a better candidate than I already am. In contrast, if I did a completely different human health bioinformatic project, then my skills and knowledge will be more broad, likely making me a stronger overall candidate for the most common human health bioinformatic jobs.

But then again, the main argument for the metagenomic route is that my project can likely reach a much higher ceiling (at least initially, relative fast), making it more complex and impressive with research and publication potential. And I already have social connections through my co-supervisor to metagenomics .So it's a really hard balance and decision to make!

---

# chatgpt response

The breadth-vs-depth concern is the first serious argument *against* the binner that I think deserves weight. The deciding question is not “metagenomics or human health?” but **whether the binner can be designed to prove a much broader set of computational-biology skills than your thesis already proves**.

I think your concern is valid, but it changes **how we design the trajectory**, not my choice of what to start now.

The best strategy is not maximum specialization or maximum breadth. It is:

> **Build one unusually deep flagship project now, while deliberately creating breadth afterward rather than trying to obtain breadth through several mediocre projects.**

And the temporary UCloud access pushes the decision further toward the binner.

## The key distinction: domain depth vs capability depth

Your thesis already proves:

> Rasmus knows metagenomic binning.

So if the new project were simply:

> "I did even more metagenomic benchmarking."

I would agree with you. Marginal career value would be limited.

But that's not what we're proposing.

Your existing work demonstrates **bioinformatics application and benchmarking**. 

The new project would ideally demonstrate:

```text
Existing thesis
────────────────────────────
Snakemake
HPC
metagenomics
benchmarking
MAG evaluation
bioinformatics workflows
scientific analysis


New research project
────────────────────────────
PyTorch
neural-network engineering
representation learning
self-supervised learning
VAEs
contrastive learning
GNNs
transformers
genome language models
multimodal ML
architecture design
ML experimentation
ablation studies
model training at scale
novel method development
```

Those aren't redundant.

The *biological domain* remains metagenomics.

The **computational skill profile changes dramatically**.

That distinction matters.

---

## I checked current computational-biology jobs for exactly this reason

There's evidence for both sides of your concern.

A recent computational-biology position asks for an MSc/PhD in computational biology, data science **or natural sciences**, together with Python/R, machine learning, HPC, version control and reproducible workflows. That list maps remarkably well onto what your thesis + proposed binner could demonstrate. ([SmartRecruiters](https://jobs.smartrecruiters.com/SyngentaGroup/744000140248429-principal-scientist-computational-biology?trid=7d1dcdfa-96a8-4e55-bb9c-0db211f5a9b3&utm_source=chatgpt.com))

Genomics England currently describes genomic data-science work involving custom analyses, state-of-the-art genomic/multi-omics methods, and explicitly **benchmarking and improving tools**. ([SmartRecruiters](https://jobs.smartrecruiters.com/GenomicsEngland/744000134301121-genomic-data-scientist-we-have-office-locations-in-cambridge-leeds-london-?trid=7d1dcdfa-96a8-4e55-bb9c-0db211f5a9b3&utm_source=chatgpt.com))

And a current genomics role specifically calls transformer architectures in genomics an advantageous capability. ([Lever](https://jobs.lever.co/e184/578080be-b803-47e2-8215-5da968e68718?utm_source=chatgpt.com))

So there absolutely are jobs where:

> biology MSc + serious genomics + HPC + novel ML method development

is a coherent profile rather than a disadvantage.

But your other concern is also supported.

Biomedical roles working on cancer and precision medicine frequently ask for experience with things like:

```text
single-cell RNA-seq
spatial transcriptomics
epigenomics
proteomics
functional genomics
multi-omics integration
```

rather than simply "omics generally." Current cancer computational-biology positions explicitly emphasize those modalities. ([SmartRecruiters](https://jobs.smartrecruiters.com/UniversityHealthNetwork/744000138708568-postdoctoral-researcher?trid=7d1dcdfa-96a8-4e55-bb9c-0db211f5a9b3&utm_source=chatgpt.com))

So:

**A world-class metagenomic binner would not magically make you experienced in scRNA-seq.**

We shouldn't pretend otherwise.

---

# But I don't think the solution is to abandon depth

Suppose you instead do four projects:

```text
basic scRNA-seq analysis
basic cancer RNA-seq analysis
basic GWAS project
basic drug-discovery model
```

Your CV becomes broader.

But you may merely look like someone who has followed workflows in four areas.

Compare that with:

> "Developed a novel deep-learning algorithm for metagenomic genome reconstruction; implemented and evaluated representation-learning architectures against modern SOTA methods across simulated, environmental and human-microbiome datasets."

That signals something different:

> **This person can independently understand a hard computational problem deeply enough to attempt method development.**

You can't cheaply manufacture that signal.

Breadth, however, is relatively cheap to acquire **afterward**.

Once you're comfortable with biological ML, learning the basic workflow for scRNA-seq or bulk transcriptomics is much easier than becoming genuinely capable of ML method development.

So I'd build the rare asset first.

---

# The UCloud situation is actually a major deciding factor

This new information strongly favors starting the binner **now**.

You currently have access to hardware like:

> H200 GPUs, huge-memory nodes and HPC infrastructure.

That access may disappear.

SkullNet does not particularly need an H200.

Its early CNNs, MLPs and even many transformer experiments could be done later using consumer/cloud hardware.

But something involving:

```text
large metagenomes
millions of contigs
large coverage matrices
foundation-model embeddings
repeated training runs
large hyperparameter experiments
multi-sample datasets
benchmarking many competing binners
```

can genuinely exploit university HPC.

So there's an asymmetry:

```text
                  NOW                  LATER

SOTA binner       ideal HPC access     potentially expensive/problematic

SkullNet          HPC overkill         still completely feasible
```

That makes the opportunity cost much clearer.

If your UCloud access disappears next year and you say:

> "Damn, I spent that period training fox-skull CNNs while I had H200s sitting there."

I suspect that would annoy you considerably more than postponing SkullNet.

---

# Your gut-versus-brain conflict has a solution

You said something important:

> If jobs didn't matter, you'd choose SkullNet without hesitation.

I therefore **would not kill SkullNet**.

I would preserve the plan.

Potentially literally create:

```text
future-projects/
└── skullnet.md
```

with the vision:

```text
morphometric MLP
→ CNN
→ embeddings
→ multi-view model
→ multimodal model
→ CLIP-like training
→ tiny GPT
→ VLM
```

So it doesn't disappear into the graveyard of ideas.

And it gives us an escape hatch.

If six months into metagenomics your motivation collapses, the answer doesn't have to be:

> force yourself harder.

It can be:

> switch to SkullNet and continue learning the same underlying field through a domain that excites you more.

That's not failure.

---

# I would also NOT wait until the binner is finished before broadening

This is critical.

A SOTA binner might never be "finished."

Research works like:

```text
idea
 ↓
experiment
 ↓
failure
 ↓
new idea
 ↓
better model
 ↓
paper?
 ↓
new limitation
 ↓
new architecture
 ↓
...
```

We shouldn't create this dependency:

> "I am forbidden from doing biomedical AI until I beat every binner."

Instead, define **competence gates**.

For example:

```text
PHASE A
Deep-learning fundamentals
        ↓
Can independently train/debug neural networks

PHASE B
Representation learning
        ↓
Understand AE/VAE/contrastive methods

PHASE C
Modern biological ML
        ↓
Transformers/GNNs/self-supervision

PHASE D
Research method
        ↓
Have our own defensible hypothesis + prototype

        ┌─────────────────────┐
        │                     │
        ↓                     ↓
continue binner         human-health project
research                     begins
```

At Phase D, you've already extracted enormous educational value.

The binner can continue indefinitely on one branch while you open another.

---

# I actually think the ideal portfolio eventually looks like a π

Not like a straight line.

Something like:

```text
                  BIOINFORMATICS / BIOMEDICAL AI

 Metagenomics                                      Human health
      │                                                │
      │                                                │
      │                                                │
      │                                                │
      │                                                │
      └────────────── DEEP LEARNING ──────────────────┘
                         │
                         │
                    ML engineering
                         │
                    genomics/HPC
```

One deep pillar:

**metagenomics / genome reconstruction**

Another eventually:

**human biomedical omics**

Connected by:

**deep learning + bioinformatics + computational biology**

That would be a much stronger profile than either:

```text
ultra-specialized metagenomics guy
```

or:

```text
guy who has vaguely tried seven omics technologies
```

---

# And we can deliberately make the binner less niche

I would make **human microbiome data a first-class part of the research project**, not something tacked on at the end.

Instead of branding it around the hadal environment:

> HadalBinner

I'd deliberately make the research question general:

> **Deep representation learning for metagenomic genome reconstruction across complex microbial communities.**

Then evaluation could eventually span:

```text
             OUR MODEL
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
    simulated   human   environmental
      CAMI       gut      metagenomes
                 │
                 ↓
             disease-
             relevant
             microbiomes
```

Now you can legitimately talk to a human-microbiome laboratory without pretending you spent years studying clinical microbiology.

And cross-biome transfer itself could become an interesting research question:

> Does the learned representation generalize between environmental and host-associated microbial communities?

That's scientifically better than simply overfitting the project to your thesis dataset.

---

# Then deliberately buy breadth cheaply

After you've gained the core DL knowledge, I would add **small, sharply scoped biomedical projects** before starting another enormous flagship.

Not six-month projects.

Things whose purpose is specifically:

> "Learn this data modality."

For example:

```text
mini-project 1
single-cell RNA-seq
→ cell QC
→ dimensionality reduction
→ clustering
→ differential expression
→ biological interpretation

mini-project 2
cancer multi-omics
→ mutation + expression + clinical data
→ integration
→ survival / phenotype modelling

mini-project 3
protein/drug ML
→ molecular representations
→ simple GNN
→ property prediction
```

These don't need to be heroic research contributions.

Their function is breadth.

Then your profile says:

> **Deep expertise in one domain + practical familiarity across several biomedical modalities.**

Much stronger.

---

# There is one more factor: publication potential

This deserves substantial weight given your lack of professional experience.

Imagine two CV entries.

### Option A

**Personal project — Cancer Classification with Deep Learning**

> Trained a neural network on TCGA RNA-seq data to classify cancer types.

Perfectly respectable.

But probably thousands of GitHub repositories do something equivalent.

### Option B

**Independent Research — Deep Learning for Metagenomic Genome Reconstruction**

> Developed a novel representation-learning approach for recovering microbial genomes from complex metagenomes. Evaluated against VAMB, SemiBin2, COMEBin, TaxVAMB, etc. across controlled and real datasets. Manuscript/preprint/software release.

That's a completely different signal.

A publication or credible preprint particularly helps attack your problem of:

> "No professional bioinformatics experience."

Because now someone can inspect evidence that you've independently done something resembling actual computational-method research.

Your existing supervisor connections make that possibility less theoretical too. 

---

# So my current decision matrix is roughly this

| Factor | SkullNet | Different biomedical project | SOTA binner |
|---|---:|---:|---:|
| Fun/motivation | **10/10** | 7–9/10 | 8/10 |
| Beginner DL intuition | **10/10** | 7/10 | 8/10 |
| Uses existing expertise | 4/10 | 5/10 | **10/10** |
| Uses UCloud opportunity | 4/10 | 7/10 | **10/10** |
| Immediate CV relevance | 6/10 | **9/10** | **9/10** |
| Novel research ceiling | 7/10 | 8/10 | **10/10** |
| Publication potential | 5/10 | 7/10 | **10/10** |
| Biomedical breadth | 2/10 | **10/10** | 5–7/10 |
| Technical ML depth | 9/10 | 7–9/10 | **10/10** |
| Existing benchmarking infrastructure | 0/10 | 0/10 | **10/10** |

The binner loses primarily on **domain breadth and immediate fun**.

Nearly everything else favors it.

---

## So I would make the call

**Start the metagenomic project.**

But with three safeguards:

1. **It must be a deep-learning learning project before it becomes a SOTA research project.** We don't jump into 20,000 lines of architecture code we don't understand.

2. **Human microbiome and cross-domain generalization should be part of its long-term design.** That keeps the bridge toward biomedical research open.

3. **We explicitly plan for a later breadth phase.** Once your deep-learning competence reaches the right level, start learning other human-health omics without waiting for the binner research to reach some imaginary endpoint.

This gives you **T-shaped knowledge now, eventually π-shaped knowledge**: one unusually deep specialty, strong general computational foundations, and later a second deep pillar in human biomedical AI.

And SkullNet stays preserved as the project you can reach for when you want to remember that neural networks can also be *fun* rather than career strategy.

The next decision should therefore **not** be architecture yet. Before Codex touches the repository, we should define the metagenomic project's research/learning charter: what the eventual ambition is, what we explicitly *don't know yet*, how we progress from first neural network to research architecture, how your existing benchmark repo relates to the new repo, and what criteria prevent us from blindly creating a Frankenstein “all SOTA ideas combined” model. That initial design will matter a lot.

---

# you asked

message time: 2026-09-15 13:14:59

## Small note:
You wrote: "We explicitly plan for a later breadth phase. Once your deep-learning competence reaches the right level, start learning other human-health omics without waiting for the binner research to reach some imaginary endpoint."

- But that's highly demotivating. To do all the groundwork of understanding deep learning in metagenomic and than just leave before reasching the final destination of creating my own final binning tool.


## Define the metagenomic project's research/learning charter:
Before we move on to codex and start the project, let's define the metagenomic project's research/learning charter. 

The initial design, roadmap and scope of the project is very important, as it makes sure we stay on the right track and don't get carried away into doing non-important stuff for the overarching goal/purpose of this project in the grand scheme of things. However, projects will always be dynamic and new knowledge down the road may reveal more fruitful branches, and we should embrace this and that we lack/can't predict this now.

Write it as a comprehensive, detailed, actionable, structured and organized markdown file(s) that will live inside the root, docs or some other folder inside the repo. These files should also ensure the codex agents understand the whole philosophy behind this project, and all the relevant background information about me, my situations and my thoughts. I will also personally upload this whole conversation to the repo as a separate markdown file so that the codex gains context about this initial idea-phase.

---

# chatgpt response

That correction is important. I would make the **final binner itself the destination**, not merely a training ground we abandon once the learning becomes transferable. Breadth comes afterward; during this project, every learning phase should compound toward a finished, independently benchmarked method.

I’m going to make the charter explicitly **completion-oriented**: the project ends only when we have produced and rigorously evaluated our own binning method, even if it does not beat every SOTA tool. The learning phases exist to reach that destination, not as excuses to pivot away early. I’ll also separate stable philosophy from dynamic research decisions so future agents can adapt without silently rewriting the project’s purpose.

The structure is now drafted as five complementary documents rather than one enormous manifesto: a stable charter, progressive roadmap, research strategy, agent context, and living decision log. I also made “SOTA” an **aspiration to test**, not a success criterion—otherwise we would incentivize benchmark gaming or endless work if a genuinely useful method ends up winning only in specific regimes.

I agree with your correction completely: **we should not do all the groundwork merely to leave before attempting the thing that motivated the groundwork.** I therefore rewrote the project philosophy around a fixed destination:

> **Learn deep learning by progressively building toward, then completing, our own metagenomic binning method.**

The architecture is deliberately *not* fixed. The destination is.

I grounded the scientific starting point in your existing benchmark—11 binners, three multi-sample workflow architectures, strain simulation, ensemble analysis, orthogonal MAG evaluation, and the existing Snakemake/HPC infrastructure—so future agents understand that this is a continuation upward from substantial previous work, not a beginner bioinformatics project.  

I created five main files:

- **[PROJECT_CHARTER.md](sandbox:/mnt/data/metagenomic_binner_project_docs/PROJECT_CHARTER.md)** — the highest-level source of truth. Mission, final destination, scope, learning philosophy, anti-goals, UCloud strategy, scientific standards, relationship to your thesis, and rules against scope drift. It explicitly says **finish the binner** and rejects a planned premature biomedical pivot.
- **[docs/ROADMAP.md](sandbox:/mnt/data/metagenomic_binner_project_docs/docs/ROADMAP.md)** — the full progressive learning/research path: first neural network → AE → VAE → dissect an existing binner → contrastive/self-supervised learning → multimodal/structured information → transformers/genome language models → formal research-gap selection → actual novel binner → rigorous benchmark → release/publication-quality finalization.
- **[docs/RESEARCH_STRATEGY.md](sandbox:/mnt/data/metagenomic_binner_project_docs/docs/RESEARCH_STRATEGY.md)** — how we prevent ourselves and Codex from creating AI spaghetti. It defines the literature/code-review process, hypothesis-generation framework, dataset roles, leakage controls, benchmarking principles, ablations, generalization testing, compute evaluation, stopping rules, and what would actually justify a SOTA claim.
- **[docs/AGENT_CONTEXT.md](sandbox:/mnt/data/metagenomic_binner_project_docs/docs/AGENT_CONTEXT.md)** — context specifically for Codex/future agents: your background, existing metagenomic competence, career situation, ambitions, learning style, work style, motivation risks, why SkullNet was deferred, temporary UCloud advantage, and how agents should teach and work with you.
- **[docs/DECISIONS.md](sandbox:/mnt/data/metagenomic_binner_project_docs/docs/DECISIONS.md)** — living research decision log. I already recorded the major decisions we have made: binner over SkullNet, final binner as destination, no predetermined architecture, selective reuse of the thesis benchmark, and treating UCloud access as temporary.

[Download the complete Markdown bundle](sandbox:/mnt/data/metagenomic_binner_project_docs.zip)

One distinction in the charter is particularly important: **“build a SOTA binner” remains the ambition, but “beat every SOTA method” is not the definition of success.** Otherwise we could do excellent independent research, discover an important trade-off or improvement in a particular regime, and irrationally call the project unfinished because CompleteBin beats us on one dataset. The required endpoint is a **novel, coherent, completed, independently benchmarked binner with defensible scientific conclusions**. If that turns out to be SOTA overall or within a meaningful regime, even better.

I also made the roadmap intentionally unusual for a learning project. Phase 1 is not something we throw away before beginning the “real work.” The repository is the real project from the beginning. The simple MLP, first autoencoder, VAE experiments, contrastive experiments, transformer work, and binner dissections progressively answer questions and construct infrastructure that lead toward the final method.

Your separate full conversation transcript will complement these files well. I would treat that transcript as the **historical record of why we arrived here**, while these documents become the maintained specification of **what we decided and how the project should proceed**.