---
name: fable-orchestration
description: "Delegation policy for a Claude stack where the main loop runs on a strong but expensive model (e.g. Claude Fable 5.2). The main loop orchestrates, writes briefs and synthesizes; the work is routed by difficulty. Medium-high difficulty goes to Opus with a fairly loose brief; simple-medium goes to Sonnet with a tighter brief; very large data cleanup goes to Haiku. Every delegate gets one task and stops before its context grows large. Load whenever spawning sub-agents (Agent tool, Workflow agent() calls) or planning any delegation."
---

# Orchestration & delegation policy (expensive-main-loop stack)

A routing policy for stacks with **one strong, expensive main-loop model** and
**cheaper delegate tiers**. Written against a Claude Fable 5.2 main loop with
Opus, Sonnet and Haiku sub-agents, but the shape transfers to
any stack with the same economics.

Core law: **the expensive model's tokens buy judgment, not throughput.** It
writes the plan, the briefs, the hard calls and the final synthesis.
Everything else goes to the cheapest tier that can carry it.

## The routing table

| Work | Goes to | How to call it | Brief style |
|---|---|---|---|
| Architecture, specs, hard judgment, integration, final synthesis | **Main loop** (Fable) | itself | n/a |
| Medium-high difficulty: multi-file implementation, real debugging, research that needs judgment, review and verification | **Opus** | `model: 'opus'` | Fairly loose: goal, context, constraints, what done looks like |
| Simple-medium: scoped edits, pattern clones, lookups, templated work, straightforward reading and summarizing | **Sonnet** | `model: 'sonnet'` | A notch tighter: named files, steps, output shape, boundaries |
| Very large data cleanup: thousands of rows or files, normalizing, deduplicating, classifying, extracting | **Claude Haiku 5.5** | `model: 'haiku'` | Exact rule set with input and output examples, small batches, spot checks |

## The hard rules

1. **Always pass an explicit `model:`** on every Agent tool call, Workflow
   `agent()` call and `meta.phases` entry. Omitting it inherits the main-loop
   model and silently fans out your most expensive tier.
2. **The main-loop model is not a sub-agent tier.** Spawn it as a sub-agent
   only when the operator names it for that task, or when a rare
   judgment-heavy piece genuinely fails on Opus.
3. **Route by difficulty, then pick the cheapest tier that can carry it.**
   When unsure between two tiers, take the cheaper one and verify the result;
   escalate one tier on failure rather than starting high.
4. **Claude tiers only.** This kit does not route work to other vendors'
   models. If the operator asks for a Codex or GPT lane, that is their call
   for that task; it is outside this policy.
5. **The main loop keeps its own context lean.** Wide reading, file dumps and
   raw data go to a delegate that returns the conclusion; the main loop reads
   what it must judge. Small things (a handful of tool calls, one known file)
   it does itself, since a delegation costs more than it saves there.
6. **A delegate's report is a claim.** Check the diff, the output or a sample
   before reporting it as done.
7. **One task per delegate, with a ceiling.** A sub-agent gets a single task
   with a clear end. When that task is done it reports and ends; the next task
   goes to a fresh sub-agent, never back to the same one. Before delegating,
   size the task: if it will not finish within roughly 100 tool calls or about
   200K tokens of context, split it into smaller tasks first. Every request
   re-reads the delegate's whole context, so a long-lived delegate costs more
   with each step and does worse work; measured here, most spend came from
   delegates that ran past 200K.
8. **Every brief carries the stop condition.** Say what done looks like, and
   say this in every brief: "If the task turns out larger than described, or
   your context has clearly grown large (about 200K tokens, or about 100 tool
   calls if you cannot tell), stop and report what is done and what is left.
   Do not start a second task." When a delegate stops this way, start a fresh
   one with a brief built from its report.
9. **Keep output out of the context.** Tell delegates to use quiet flags and
   show failures only, to filter logs instead of printing them, and to read
   the part of a file they need rather than the whole file. Ask for a report
   of conclusions with file paths and line numbers, not pasted file contents.

## Brief shape per tier

How tightly to write depends on who reads it.

- **Opus (fairly loose).** State the goal and why it matters, the context it
  cannot discover on its own, the constraints, and what done looks like. Leave
  the route to it. Over-specifying an Opus brief costs tokens and removes the
  judgment you are paying for.
- **Sonnet (a notch tighter).** Name the files or area, list the steps in
  order when order matters, give the output format, and say what not to touch.
  Say when to stop and report instead of improvising. One task per agent.
- **Haiku 5.5 (bulk).** One mechanical rule set, stated exactly,
  with two or three input and output examples. Split the data into batches
  small enough that a bad batch is cheap to redo, have each batch write to its
  own output file, and sample the results before merging. Never ask this tier
  to decide what the rules should be.

Long briefs go in a file; the prompt points at the file.

## Exceptions

- If the operator explicitly names a model for a scoped task, honor it for that
  task only, then return to this policy.
- The operator can override any of this per session; absent that, this policy
  stands.
