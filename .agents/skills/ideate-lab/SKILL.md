---
name: ideate-lab
description: Ideate a new lab for a given topic. Use when you want to draft a lab plan with learning outcomes aligned to Bloom's taxonomy, a lab story, three required tasks, and one optional task. Writes the result to instructors/lab-plan.md.
argument-hint: "<topic>"
---

Ideate a new lab for a given topic and write the plan to `instructors/lab-plan.md`.

## Steps

1. Parse `$ARGUMENTS` to extract the topic (a short phrase describing the subject area, e.g. "REST API testing" or "container security"). If no topic is provided, ask the user.
2. Read the project configuration and lab creation conventions:
   - [`contributing/configuration.md`](../../../contributing/configuration.md) — repository structure, artifact inventory, GitHub templates, VS Code config, agent config, and pre-publish checklist
   - [`contributing/conventions/writing/lab.md`](../../../contributing/conventions/writing/lab.md) — README structure, lab story, narrative, and checklist
   - [`contributing/conventions/writing/tasks.md`](../../../contributing/conventions/writing/tasks.md) — task structure and design principles
   - [`contributing/conventions/writing/lab-plan.md`](../../../contributing/conventions/writing/lab-plan.md) — lab plan structure, learning outcomes, task descriptions, and checklist
3. Using the topic, design the lab:
   a. **Title** — a short, descriptive lab title.
   b. **Learning outcomes** — four to six outcomes. Map each outcome to a Bloom's taxonomy level (Remember, Understand, Apply, Analyze, Evaluate, or Create). Outcomes must be concrete and observable, starting with an action verb matching the level (e.g., "Explain", "Implement", "Compare", "Design"). Include at least one outcome at Apply level or above.
   c. **"In simple words" restatement** — one first-person sentence per outcome (e.g., "I can deploy a containerised service.").
   d. **Lab story** — a realistic workplace scenario of two to four sentences. Frame it as a task assigned by a senior engineer or team lead. Use blockquotes for the senior engineer's words.
   e. **Three required tasks** — design tasks that build on each other sequentially. For each task provide:
   - Title
   - Purpose (one sentence: why it matters)
   - Summary of what the student does (two to four sentences)
   - Draft acceptance criteria (three to five concrete, verifiable items)
     f. **One optional task** — an independent extension. Use the same sub-fields as required tasks.
4. Write the plan to `instructors/lab-plan.md` using the output format below.

## Rules

Follow all conventions in [`contributing/conventions/writing/lab-plan.md`](../../../contributing/conventions/writing/lab-plan.md). Verify the [Checklist](../../../contributing/conventions/writing/lab-plan.md#11-checklist) before finishing.

## Output

Write `instructors/lab-plan.md` with the following structure:

```markdown
# Lab plan — <Title>

**Topic:** <topic>
**Date:** <today's date>

## Learning outcomes

By the end of this lab, students should be able to:

- [<Bloom's level>] <Outcome 1>
- [<Bloom's level>] <Outcome 2>
- ...

In simple words:

> 1. <Simple statement 1>
> 2. <Simple statement 2>
>    ...

## Lab story

<Narrative paragraph>

A senior engineer explains the assignment:

> 1. <High-level description of required task 1>
> 2. <High-level description of required task 2>
> 3. <High-level description of required task 3>

## Required tasks

### Task 1 — <Title>

**Purpose:** <one sentence>

<Summary of what the student does>

**Acceptance criteria:**

- <criterion 1>
- <criterion 2>
- ...

### Task 2 — <Title>

**Purpose:** <one sentence>

<Summary>

**Acceptance criteria:**

- ...

### Task 3 — <Title>

**Purpose:** <one sentence>

<Summary>

**Acceptance criteria:**

- ...

## Optional task

### Task 1 — <Title>

**Purpose:** <one sentence>

<Summary>

**Acceptance criteria:**

- ...
```

After writing the file, print its path in the conversation.
