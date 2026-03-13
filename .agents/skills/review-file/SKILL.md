---
name: review-file
description: "Review a file for convention violations. Supports lab/tasks/ files (conceptual + convention review), wiki/ files, contributing/conventions/ files, AGENTS.md, instructors/lab-plan.md (lab plan review), and instructors/meetings/ report.md files (cross-checked against the transcript and files discussed). Writes the review report to instructors/file-reviews/ (or report-review.md alongside the source for meeting reports)."
argument-hint: "<path>"
---

Review a single file for problems — first conceptual and pedagogical issues (for task files), lab plan review (for lab plans), or transcript cross-check (for meeting reports), then convention violations. Accepted locations: `lab/tasks/`, `wiki/`, `contributing/conventions/`, `AGENTS.md`, `instructors/lab-plan.md`, and `instructors/meetings/` (report.md files only).

## Steps

1. Parse `$ARGUMENTS` to get the file path. Accept:
   - Paths under `lab/tasks/` (e.g., `lab/tasks/setup.md`, `lab/tasks/required/task-2.md`)
   - Paths under `wiki/` (e.g., `wiki/api.md`)
   - Paths under `contributing/conventions/` (e.g., `contributing/conventions/writing/common.md`)
   - The repository root `AGENTS.md` file
   - The lab plan file `instructors/lab-plan.md`
   - Meeting report files matching the pattern `instructors/meetings/week-N/meeting-M/report.md` (e.g., `instructors/meetings/week-2/meeting-1/report.md`)
   If the path is missing or does not match one of these patterns, ask the user.
2. Read the target file.
3. Read the convention files that apply to the target file:
   - **For `lab/tasks/` files:**
     - [`contributing/conventions/writing/tasks.md`](../../../contributing/conventions/writing/tasks.md) — Section 13 defines the ten review dimensions (D1–D10) for conceptual review; Section 3 and Section 12 define task structure and design principles for convention review
     - [`contributing/conventions/writing/common.md`](../../../contributing/conventions/writing/common.md) — writing conventions (4.1–4.23)
   - **For `lab/tasks/setup.md` and `lab/tasks/setup-simple.md` (in addition to the above):**
     - [`contributing/conventions/writing/setup.md`](../../../contributing/conventions/writing/setup.md) — setup file structure and conventions
   - **For `wiki/` files:**
     - [`contributing/conventions/writing/common.md`](../../../contributing/conventions/writing/common.md) — writing conventions (4.1–4.23)
     - [`contributing/conventions/writing/wiki.md`](../../../contributing/conventions/writing/wiki.md) — wiki file structure and section patterns
   - **For `contributing/conventions/` files:**
     - [`contributing/conventions/conventions.md`](../../../contributing/conventions/conventions.md) — conventions for writing conventions
   - **For `AGENTS.md`:**
     - [`contributing/conventions/agents/agents.md`](../../../contributing/conventions/agents/agents.md) — AGENTS.md conventions (agent-neutral content, format and structure)
   - **For `instructors/lab-plan.md`:**
     - [`contributing/conventions/writing/lab-plan.md`](../../../contributing/conventions/writing/lab-plan.md) — lab plan structure, content rules, and review dimensions (D1–D7)
   - **For `instructors/meetings/` report.md files:**
     - [`contributing/conventions/meetings/meeting-report.md`](../../../contributing/conventions/meetings/meeting-report.md) — meeting report format rules (Sections 3–4) and the five review categories (Section 5)
4. (**For `instructors/meetings/` files only**) Derive the transcript path by replacing `report.md` with `transcripts/transcript-by-speaker.txt` in the report path (e.g., `instructors/meetings/week-2/meeting-1/transcripts/transcript-by-speaker.txt`). Read the transcript. If the report's **Metadata → Files discussed** section lists any files, read each of them.
5. **Conceptual review** (only for `lab/tasks/` files): Analyse the file against each dimension (D1–D10) from Section 13 of [`contributing/conventions/writing/tasks.md`](../../../contributing/conventions/writing/tasks.md). For each problem found, record: the dimension, the line number(s) or section, a short description, severity (`[High]`, `[Medium]`, or `[Low]`), and a suggested fix.
6. **Lab plan review** (only for `instructors/lab-plan.md`): Analyse the file against each dimension (D1–D7) from [Review dimensions](../../../contributing/conventions/writing/lab-plan.md#10-review-dimensions) in [`contributing/conventions/writing/lab-plan.md`](../../../contributing/conventions/writing/lab-plan.md). For each problem found, record: the dimension, the line number(s) or section, a short description, severity (`[High]`, `[Medium]`, or `[Low]`), and a suggested fix.
7. **Meeting report review** (only for `instructors/meetings/` files): Analyse the report against the five categories in Section 5 of [`contributing/conventions/meetings/meeting-report.md`](../../../contributing/conventions/meetings/meeting-report.md). For each finding, cite the relevant transcript line or report line number, and assign severity (`[High]`, `[Medium]`, or `[Low]`).
8. **Convention review** (for `lab/tasks/`, `wiki/`, `contributing/conventions/`, and `AGENTS.md` files only): Go through the target file **line by line**. Check it against **every** convention in the applicable convention files. Flag each violation with its line number and assign severity (`[High]`, `[Medium]`, or `[Low]`).
9. Scan for `<!-- TODO ... -->` comments. Report each one with its line number and the comment text.
10. Scan for empty sections: a heading immediately followed by another heading, a `<!-- TODO ... -->` comment, or end of file, with no real content lines in between. Report each empty section with its line number and heading text.

## Rules

- The convention files are the single source of truth. Check every rule they contain — do not skip any.
- Do not invent rules beyond what the convention files state.
- Be strict: flag every violation, no matter how small.
- Do not fix anything — only report.
- If a convention does not apply to the file (e.g., the file has no Docker commands), skip that category and note "Not applicable."
- For `lab/tasks/setup.md` and `lab/tasks/setup-simple.md`: skip task-only conventions (Section 3 template, acceptance criteria format). Apply all [`contributing/conventions/writing/common.md`](../../../contributing/conventions/writing/common.md) conventions and all [`contributing/conventions/writing/setup.md`](../../../contributing/conventions/writing/setup.md) conventions.
- For `contributing/conventions/conventions.md` itself: apply its own rules — the file is self-referential and must comply with the conventions it defines.
- When referring to a section in the reviewed file, link to it using a markdown link whose URL is a **relative path from the review file** to the reviewed file, followed by `#` and the heading anchor. Do not use bare local anchors (`#...`) that would resolve to the review file itself. Do not use repo-root-relative or absolute paths.

## Output format

Write the report to:
- **For `instructors/meetings/` files:** `report-review.md` in the same directory as the source file (e.g., `instructors/meetings/week-2/meeting-1/report-review.md` for `instructors/meetings/week-2/meeting-1/report.md`).
- **For all other files:** `instructors/file-reviews/<repo-root-path>`, where `<repo-root-path>` is the file's path from the repository root (e.g., `instructors/file-reviews/lab/tasks/setup.md` for `lab/tasks/setup.md`). Create intermediate directories if they do not exist.

The report must be self-contained so another session or agent can act on it without extra context. Structure:

1. **Header** — file path reviewed, date, convention files used, transcript path (for meeting reports only).
2. **Conceptual findings** (only for `lab/tasks/` files) — grouped by dimension (D1–D10). Under each dimension, list findings as numbered items with severity, line number(s) or section, description, and suggested fix. If a dimension has no findings, write "No issues found."
3. **Lab plan findings** (only for `instructors/lab-plan.md`) — grouped by dimension (D1–D7). Under each dimension, list findings as numbered items with severity (`[High]`, `[Medium]`, or `[Low]`), line number(s) or section, description, and suggested fix. If a dimension has no findings, write "No issues found."
4. **Meeting report findings** (only for `instructors/meetings/` files) — grouped by review category (5.1 Transcript coverage, 5.2 Accuracy, 5.3 Files discussed, 5.4 Format compliance, 5.5 Internal consistency). Under each category, list findings as numbered items with severity (`[High]`, `[Medium]`, or `[Low]`), the relevant transcript or report line number, description, and suggested fix. If a category has no findings, write "No issues found."
5. **Convention findings** (for `lab/tasks/`, `wiki/`, `contributing/conventions/`, and `AGENTS.md` files only) — grouped by convention number or section (e.g., "4.2. Terminal commands", "Section 3. Task document structure", "Section 2. Agent-neutral content"). Under each group, list findings as numbered items with severity (`[High]`, `[Medium]`, or `[Low]`) and line numbers. If a group has no findings, write "No issues found."
6. **TODOs** — list every `<!-- TODO ... -->` comment with its line number and text. If none, write "No TODOs found."
7. **Empty sections** — list every heading that has no content (only a TODO comment, another heading, or EOF follows). Include line number and heading text. If none, write "No empty sections found."
8. **Summary** — a `| Category | Count |` table followed by an `**Overall**:` assessment paragraph. Include one row per category that applies to the file type, plus a bold **Total** row:

   **For `lab/tasks/` files:**

   ```
   | Category | Count |
   |---|---|
   | Conceptual [High] | N |
   | Conceptual [Medium] | N |
   | Conceptual [Low] | N |
   | Convention [High] | N |
   | Convention [Medium] | N |
   | Convention [Low] | N |
   | TODOs | N |
   | Empty sections | N |
   | **Total** | **N** |
   ```

   **For `wiki/`, `contributing/conventions/`, and `AGENTS.md` files:**

   ```
   | Category | Count |
   |---|---|
   | Convention [High] | N |
   | Convention [Medium] | N |
   | Convention [Low] | N |
   | TODOs | N |
   | Empty sections | N |
   | **Total** | **N** |
   ```

   **For `instructors/lab-plan.md`:**

   ```
   | Category | Count |
   |---|---|
   | Lab plan [High] | N |
   | Lab plan [Medium] | N |
   | Lab plan [Low] | N |
   | TODOs | N |
   | Empty sections | N |
   | **Total** | **N** |
   ```

   **For `instructors/meetings/` files:**

   ```
   | Category | Count |
   |---|---|
   | Meeting report [High] | N |
   | Meeting report [Medium] | N |
   | Meeting report [Low] | N |
   | TODOs | N |
   | Empty sections | N |
   | **Total** | **N** |
   ```

   After the table, write an `**Overall**:` paragraph summarising the current state of the file and the most important remaining issues.

After writing the file, print its path in the conversation so the user can find it.
