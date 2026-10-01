# Drawing story — spoken arc for the slides

Connected narrative from the director’s walkthrough of the Excalidraw figures.
Per-drawing talking points also live in each companion’s curated **Ideas**
region (`docs/drawings/<stem>.md`). This file keeps **tone and transitions** so
the arc can be spread across the deck with clear before/after anchors.

Companions stay interpretation aids (SPEC.v18). This story is the placement map
and speaker thread — not a second source of truth for the SVG embeds.

## Anchor map

| # | Drawing | Beat (one line) | In deck today | Place before / after |
| --- | --- | --- | --- | --- |
| 1 | `sprouts` | Gen AI grows sprouts into monsters; specs must be precise yet minimal | `deck-software-part1.md` — “Nom nom” | Opens the whole arc: first slide after the title; before “Before we start” |
| 2 | `4quads` | Shrink the ¬det × automated danger zone | `deck-software-part1.md` — “The new quadrants” | After `sprouts`; before “Three journeys” |
| 3 | `comm-is-hard` | Even twins miss each other; a machine makes it worse | *not embedded yet* | After 4quads’ “sometimes HITL / semi-auto”; before `hard-easy` |
| 4 | `hard-easy` | AI stretches easy→easier and hard→harder; communication stays hard | `deck-software-part1.md` — “Easy easier, hard harder” | After `comm-is-hard`; before “How this works” / Basics |
| 5 | `context-injection` | Static training forever; company truth fights for a tiny context window | `presentation/lessons/context1.md` | After “communication / hard half” setup; opens Context 1 |
| 6 | `hitl` | Optimize for >90% AI+det automation; human only sees the rest | *asset exists; not in a lesson yet* | After context scarcity / when semi-auto is named; before `hitl-options` |
| 7 | `hitl-options` | Minimize the rest: piggyback UIs, static page+prompt back, or AGUI | *not embedded yet* | Right after `hitl`; before SDLC / product goals |
| 8 | `sdlc1` | Idea → magic → product | *not embedded yet* | Opens the “we ship software” beat; immediately before `sdlc2` |
| 9 | `sdlc2` | Name the magic; expand AI beyond code-dominated phases | *asset `sdlc2.svg` exists; not in a lesson yet* | After `sdlc1`; bridge into Spec / beyond-code journey |
| 10 | `intent` | Spec disconnected from code → “why is it like this?” | *not embedded yet* | After SDLC “specs are unstructured”; into Spec 1, calling back to the `sprouts` opener (same plant motif) |
| 11 | `pos` | PO + engineer + AI; specs live next to code and sync back | `presentation/lessons/spec1.md` | After intent gap; with Spec 1 refine/create story |
| 12 | `new-world` | Changeflow flips: documentation becomes accelerant | `presentation/lessons/spec1.md` — “The changeflow flips” | Spec 1 opener or next to `pos`; after “spec beside code” |
| 13 | `quality-gates` | Swiss-cheese gates thin the code mountain before human review | `presentation/lessons/verify2.md` | Closes the arc (Part 2 / Verify); after HITL “reduce what you look at” |

Suggested slide thread if telling the story in one pass:

`sprouts` → `4quads` → `comm-is-hard` → `hard-easy` → (`context-injection`) → `hitl` → `hitl-options` → `sdlc1` → `sdlc2` → `intent` → `pos` → `new-world` → `quality-gates`

---

## The story

### 1. Sprouts — `sprouts`

*Opener:* first slide after the title. Most things start small — and Gen AI
isn’t named Gen AI for no reason.

It generates a lot if you let it. From something tiny and cute, something huge
can grow rather rapidly. To avoid becoming the poor little person eaten by the
plant that was adorable at the beginning, the specification has to be in good
shape so uncontrolled growth doesn’t overgrow us.

One particular takeaway: the spec must be **precise, yet minimal**. We don’t
want to read a novel. To the point. As minimal as it gets, as precise as it
gets. Then the resulting code — always bigger — can still stay in a controllable
field.

And that minimal spec is our **control plane** for the behemoth on the other
side. It becomes the new natural source of truth. Traditionally it’s the other
way around: codebases house only code; the spec lives somewhere else — and that
is a problem. Put them closer, in the same codebase, treat the specification
more like code so they evolve together. You may still coexist on Jira and
Confluence so a broader spectrum of people can talk with you. Living next to
the code is what stops the plant from becoming the monster.

**Slide note:** The hook, before any setup. Spec 1 and `intent` call back to
the plant.

### 2. Four quadrants — `4quads`

There’s always been the battle between automation and human manual labor. And
there’s always been probabilistic methods and deterministic ones. What we want
is to keep the **danger zone** small — the cell that grows fast when LLMs do
non-deterministic work in large quantities, automatically.

Find ways to push work *out* of that highly automated × highly non-deterministic
quadrant: make it more deterministic while staying high on automation when you
can. Sometimes you can’t. Then give control back — human-in-the-loop, a
semi-automated process — so it’s less automatic rather than fully auto and fully
¬det.

**Slide note:** The room’s opening stake, right after the `sprouts` hook. Everything later is about
shrinking that red cell without pretending sampling goes away.

### 3. Communication is hard — `comm-is-hard`

*Transition:* And communication is already the hard half of the work.

Give the same values to two people — make them twins, grown up together. Same
genetics, same education, most likely. Everyone knows how dissimilar twins can
still be. Same room, same situation, completely different behaviour. Two people
talking are already likely to miss each other. Communication is hard.

Now throw in someone who doesn’t share those values — a machine. That does not
make it simpler. It makes it harder.

**Slide note:** Sit this between the quadrants and the easy/hard stretch. It
earns the claim that “hard stays hard.”

### 4. Easy / hard — `hard-easy`

*Transition:* Follow-up to that previous picture.

What we see in the field: AI makes hard things harder, and easy things easier.
It stretches the poles; it does not flatten difficulty. We have to accept that
communication is hard and will stay hard.

A large portion of the work *is* communication — prioritizing, selecting what
matters, holding a broad picture of the software landscape, business needs,
customer feedback, so many areas. That is still not where AI taps in easily. We
have to bridge that gap.

**Slide note:** Already on Part 1 after the quadrants. If `comm-is-hard` is
added, this becomes the “and here’s the field observation” beat.

### 5. Context injection — `context-injection`

*Transition:* So how does anything we care about even reach the model?

The brain is pre-trained. It already knows a lot from static training —
infrastructure, the railroads, the tools everyone uses. That is baked into the
weights. Forever. Ingrained. It does not go away when you throw something into
context.

Against that, only a tiny short-lived speck is reserved for what *you* care
about: the context window. Into that limited space you have to fit standards,
processes, skills that describe how to do a task, the chat itself, the task,
domain knowledge the brain doesn’t have, company tools it doesn’t know, business
needs. None of that is in the model until you tell it — and all of it spends the
same scarce budget.

Load paths differ. In Claude, `AGENTS.md` loads at the start and stays for the
session; skills load on demand. Different mechanisms, same precious space.

**Slide note:** Context 1 already carries this figure. Bridge from “hard stays
hard / communication gap” into “so we write context on purpose.”

### 6. Human in the loop — `hitl`

*Transition:* Back to the danger zone — when we need semi-automation, or we
wake up already inside it.

Step back. What are we optimizing for? Give AI as much deterministic automation
as possible. Over ninety percent of the work distribution; only a tiny rest for
the human to look into.

Data cleansing: you don’t want millions of records — only the ones that couldn’t
be resolved automatically. Translate that to code and PRs: a lot of code to go
through, and you want to look only at what really matters. How do we shrink
that? Improve the quality of what lands, or reduce how much of it there is —
two angles, worth taking separately next.

**Slide note:** Ties 4quads’ “give control back” to a concrete distribution bar.
Leads into options, and later into quality gates.

### 7. HITL options — `hitl-options`

*Transition:* Now that we know what matters — minimize, facilitate, and
simplify the leftover for the human.

If the process is very custom, provide a decision-making surface. Or piggyback
on what already exists: IDE + VS Code plugin, Cursor, Terminal UI with Claude
Code, Claude Desktop + MCP. Natural-language infrastructure is already there;
tie your process-specific bits on top.

UI-heavy? Prefer IDE + plugin. Sometimes simpler: a self-contained static web
page with all the context the human needs, then context/prompt propagation back
into chat — spit out a prompt carrying what they decided. If that’s not enough:
custom UI that speaks to agents (CopilotKit over AGUI), or IDE + plugin extended
with AGUI.

Today we mostly focus on Claude Code and its share/extend mechanisms. Keep the
other ideas. Coding itself is a human-in-the-loop process — we pick the tools
and UIs and extend their abilities.

**Slide note:** Optional depth after `hitl`. Don’t let it steal Spec 1 time;
park it where tool choice is the topic.

### 8–9. SDLC — `sdlc1` then `sdlc2`

*Transition:* The goal in the end is to develop software.

**`sdlc1`:** Usually it starts simple — an idea, then magic happens, and
eventually a product is delivered. That’s the very simple way to put it.

**`sdlc2`:** Unpack the magic. Design and sketch right after the idea. Then
implement what’s been designed and specified. Then test. Then release. Once it’s
running: maintenance, operations, customers using it and giving feedback. All of
that is necessary to get a product over the finish line.

Where we apply AI mostly today is where code dominates. That isn’t the only
place we can and should. Extend from implementation and testing into release and
ops (infrastructure as code). Bring user feedback and ops signals —
monitoring, observability — back in. Go more exotic: early design, architecture
as Mermaid before the infrastructure even exists, and let that high-level
knowledge guide implementation, testing, release.

Main takeaway: expand into areas where code is *not* dominating — specs living
unstructured in Confluence, wikis, Jira, GitHub issues; diagrams that go stale
fast. Bridge AI into those phases. Every one of them is still a
human-in-the-loop process.

**Slide note:** Pair as a vertical: `sdlc1` joke, then `sdlc2` resolve. Bridges
“beyond traditional code” into the spec/control-plane story.

### 10. Intent — `intent`

*Transition:* Back to the plant from the opener — what happens if spec and
code are disconnected.

“Why should I write a spec if I can just interrogate the AI and battle through
in chat?” Sure you can. Then someone’s being eaten alive by the codebase,
screaming, and everyone’s asking *why is it like this?* — and nobody can find
the intent. Shrugs. *Is this even normal?* Maybe. Or maybe you want to avoid
that, and the best way is to bring the specification next to the code so the
question marks don’t come up at all.

This happens every day to every one of us — even without AI. We share country,
education, lived experience. The AI learned to talk, not to walk, and doesn’t
manipulate objects in the same world, so it doesn’t understand your problems.
We already face the gap without AI. Spec beside code is how you keep that gap
from appearing in the first place.

**Slide note:** Direct answer to the Spec 1 / Effort Shift objection. Calls
back to the `sprouts` opener.

### 11. Product owners — `pos`

*Transition:* Now from the product owner’s perspective.

Different roles, different expertise, all have to share that expertise to ship
something great. AI can mediate — overarching experience from many developers
and product owners — but only if this doesn’t become a minefield. Everyone needs
access to the specifications that now live next to the code, maintained with
the code and reflected back — not only in Jira.

Practical loop: the product owner creates on their tooling; reflect into the
codebase; when the codebase side changes, reflect back automatically into Jira
or the tool of choice. Then everyone contributes the same way, with AI helping
to create a new spec or refine an old one.

It’s much easier for the AI to go through a larger set of specifications if
they’re all structured the same way — treated as code — instead of unstructured
somewhere else. Someone who’s not deep in code can still describe what needs to
be done; AI helps craft a crisp, minimal, readable specification. A document you
can exchange with teammates. If you only combat the problem in chat, nobody can
tell *why* things are how they are. The specification is central documentation
and communication today.

**Slide note:** Already on Spec 1. Pair with create/refine and versioned SPEC
files.

### 12. Changeflow flips — `new-world`

*Transition:* And that flips the whole change flow.

Documentation was always a burden. If you were lucky: requirements came in,
someone wrote code quickly, then documented how it was done. Oftentimes
documentation never happened — requirements straight to code with a short
description, maybe a few lines of docs later, or bounce code ↔ requirements and
skip docs entirely. Lack of documentation was and still is everywhere. That was
the old world.

Throw in automation and AI, and you get a nice twist. Documentation turns from
a **burden into an accelerant**. If every agent session means explaining the
project from scratch, you get bored fast — so you write down what’s important
to get the best help. Natural incentive. Requirements in → create the
documentation necessary → then craft the code. Informal specification first;
formal specification as code derived from it. How it should have been in the
first place — rarely was. Documentation is an accelerant, not a burden anymore.

**Slide note:** Spec 1 already titles this “The changeflow flips.” Keep that
name; it’s the story’s hinge.

### 13. Quality gates — `quality-gates`

*Transition:* Final piece of this little story.

AI generates mountains of code very quickly. Be deliberate about the quality
gates you choose — a layer of Swiss-cheese slices, each filtering out certain
invalid states: impure, imperfect, non-compiling, off-standard. Each slice
reduces how much impure code is left. You only ever want to look at those
mountains once you know all your quality gates have passed.

Go further when it helps: run it and inspect the results yourself before looking
at the code. Not always — but it can matter to focus on resulting behaviour (the
UI) first, and only read the code as a final quality review once it’s done.

**Slide note:** Closes the arc on Verify / gates. Echoes `hitl`: shrink what
the human reviews; behaviour before code when that focus pays off.

---

## Thread in one breath

A tiny spec grows into monster code → danger zone grows → communication was
already hard → AI stretches hard/easy → context is scarce → HITL means automate
the mass, human the rest → pick a surface for that rest → we ship software
(magic → named SDLC) → expand AI past code → spec apart from code lets intent
die → PO and eng share structured specs beside code → docs become accelerant →
gates thin the mountain before review.
