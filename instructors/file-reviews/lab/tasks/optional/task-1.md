# Review: `lab/tasks/optional/task-1.md`

**Date:** 2026-03-10

**Convention files used:**

- `contributing/conventions/writing/tasks.md` — Section 1 (task document template), Section 3 (steps with sub-steps), Section 4 (task design principles), Section 5 (conceptual review dimensions D1–D12)
- `contributing/conventions/writing/common.md` — writing conventions (4.1–4.26)

---

## Conceptual findings

### D1. Learning objective clarity

1. **[Low]** Line 9 — The Purpose lists three actions ("Set up `Grafana`… connect it to `PostgreSQL`… build visualizations using `SQL` queries") rather than stating a single concrete learning outcome. A stronger Purpose would focus on what the student learns, e.g., "Compare a dedicated dashboarding tool (`Grafana`) with a hand-built front-end dashboard by connecting `Grafana` to `PostgreSQL` and building visualizations." Suggested fix: rewrite Purpose to lead with the learning outcome, not the actions.

### D2. Step-by-step completeness

1. **[Low]** Line 90 — Step 1.5 item 2 says "Add at least two panels. Example ideas:" and then provides example queries, but does not give explicit step-by-step instructions for creating a panel (e.g., "Click **Add visualization**", "Select the data source", "Paste the query"). A student unfamiliar with `Grafana` may not know how to create a panel from the query alone. Suggested fix: add 2–3 explicit sub-steps for creating the first panel, then let the student replicate for the second.

### D3. Student navigation

No issues found.

### D4. Checkpoints and feedback loops

1. **[Medium]** Lines 34–43 ([Step 1.2](lab/tasks/optional/task-1.md#12-enable-grafana-in-docker-compose)) — No checkpoint after uncommenting the `Grafana` service block. The student cannot verify the uncommenting was done correctly before starting `Docker`. A syntax error or incomplete uncomment would surface only after `docker compose up` fails. Suggested fix: add a brief checkpoint (e.g., "The `grafana` service should appear without `#` characters at the start of each line").
2. **[Medium]** Lines 45–54 ([Step 1.3](lab/tasks/optional/task-1.md#13-start-grafana)) — This step starts `Docker` containers (infrastructure) but has no collapsible troubleshooting block. Common failures include port 3000 already in use and containers exiting immediately. Suggested fix: add a `<details><summary><b>Troubleshooting (click to open)</b></summary>` block covering these two symptoms.
3. **[Low]** Lines 87–128 ([Step 1.5](lab/tasks/optional/task-1.md#15-build-a-dashboard)) — No checkpoint after building the dashboard. The student has no way to confirm the dashboard looks correct before saving. Suggested fix: add a brief description or screenshot of what a finished two-panel dashboard should look like.

### D5. Acceptance criteria alignment

No issues found.

### D6. Difficulty and progression

No issues found.

### D7. Practical usability

1. **[Low]** Lines 60–64 — Step 1.3 item 3 says to log in with `admin`/`admin`, but step 1.2 item 4 (line 43) offers the option to change credentials in `.env.docker.secret`. A student who changed them may be confused by the default login instructions. Suggested fix: add a note such as "If you changed the credentials in step 1.2, use those instead."

### D8. LLM-independence

No issues found.

### D9. Git workflow coherence

1. **[Medium]** Lines 138–140 ([Step 1.7](lab/tasks/optional/task-1.md#17-finish-the-task)) — The step is titled "Finish the task" but contains only "Close the issue." Per convention 4.11, "Finish the task" is reserved for the PR + review ending (create PR, get review, merge). The current body matches the no-code ending pattern (close issue with evidence) but uses the wrong heading. Suggested fix: either (a) add `Git workflow` step 1.1, PR creation, and review steps, or (b) rename the step and restructure to match the close-issue-with-evidence pattern.
2. **[Medium]** Lines 34–43 — The task modifies `docker-compose.yml` (a tracked file) in step 1.2 but does not include a "Follow the `Git workflow`" step and does not ask students to commit or push. This leaves a modified file uncommitted on the VM. Suggested fix: either add the `Git workflow` step and a PR ending, or add a note explaining that this change is local-only and intentionally not committed.

### D10. Conceptual gaps and misconceptions

1. **[Low]** Line 41 — Asks students to uncomment the `Grafana` service block without explaining why it was commented out. A brief note (e.g., "The `Grafana` service is commented out by default because it is used only in this optional task") would help students understand the design pattern. Suggested fix: add a `> 🟦 **Note**` block after step 1.2 item 3.

### D11. Controlled AI steps

Not applicable — no AI-assisted steps in this task.

### D12. Autochecker verifiability

1. **[High]** Line 152 — "The dashboard has at least 2 panels with data from `PostgreSQL`." `Grafana` dashboards are stored in its internal database; verifying panel count and data source requires `Grafana` API access, which is not part of the standard autochecker channels (repository checks + VM `SSH`). Suggested fix: either provision the dashboard via a `JSON` file at a known path (checkable via `SSH`), or expose the `Grafana` API and document the check, or replace with a criterion the autochecker can verify (e.g., a screenshot posted in the issue).
2. **[Medium]** Line 153 — "The issue contains a reflection comment comparing the two dashboard approaches" is open-ended free text. The autochecker can check for comment existence via the `GitHub` API but cannot verify whether the content adequately compares the approaches. Suggested fix: require a structured format (e.g., "The reflection comment addresses all three questions from step 1.6") or constrain to a verifiable proxy (e.g., "The issue contains a comment with at least 3 lines").

---

## Convention findings

### Section 1. Task document template

1. ~~**[Medium]** Between lines 13 and 15 — Missing `<h4>Diagram</h4>` section. The task involves actions across multiple environments (editor for `docker-compose.yml`, terminal/VM for `Docker` commands, browser for `Grafana` UI, `Grafana` connecting to `PostgreSQL` via `Docker` network). Convention 1.1 requires a Mermaid sequence diagram when the task involves actions across multiple actors or environments. Suggested fix: add a `sequenceDiagram` showing Developer → VM (Docker) → Browser (Grafana) → PostgreSQL flow.~~
2. **[Medium]** Lines 138–140 — Step 1.7 "Finish the task" body doesn't match the template pattern. The template for "Finish the task" requires PR creation and review steps (`1. Create a PR… 2. Get a PR review…`). The current body only has "Close the issue." This is a structural mismatch between the heading and the ending type.
3. **[Medium]** The task modifies `docker-compose.yml` (step 1.2, line 41) but has no "Follow the `Git workflow`" step (expected as step 1.1 per convention 1.1). If the task is designed as a no-commit exploration, the file modification creates a design inconsistency with the template rules.

### 4.1. Instructions wording

No issues found.

### 4.2. Terminal commands

No issues found.

### 4.3. Command Palette commands

Not applicable.

### 4.4. Options vs steps

Not applicable.

### 4.5. Ordered lists

No issues found.

### 4.6. Mini-ToC

Not applicable.

### 4.7. Table of contents

No issues found.

### 4.8. Links and cross-references

1. ~~**[Low]** Line 83 — `docker-compose.yml` is mentioned in prose in section 1.4 but is not linked. Convention 4.8 requires linking a concept or file on its first mention within each section. The file was linked in section 1.2 (line 37) but this is a different `###`-level section. Suggested fix: link to `[`docker-compose.yml`](../../../docker-compose.yml)`.~~

### 4.9. Notes, tips, warnings

No issues found.

### 4.10. Images

Not applicable.

### 4.11. Collapsible hints and solutions

Not applicable.

### 4.12. Commit message format

Not applicable.

### 4.13. Diagrams

Not applicable (covered in Section 1 finding #1).

### 4.14. `<!-- TODO -->` comments

Not applicable.

### 4.15. `<!-- no toc -->` comments

Not applicable.

### 4.16. Code snippets in explanations

Not applicable.

### 4.17. Heading levels in section titles

Not applicable.

### 4.18. Inline formatting of technical terms

No issues found.

### 4.19. Steps with sub-steps

Not applicable.

### 4.20. Placeholders in docs

No issues found.

### 4.21. `docker compose up` commands

No issues found.

### 4.22. Environment variable references

1. **[Low]** Line 43 — `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` are referenced as environment variables from `.env.docker.secret` but are not individually linked to their wiki sections per the convention 4.22 pattern (`` [`VARIABLE_NAME`](../../../wiki/dotenv-docker-secret.md#variable_name) ``). The file name is linked correctly but the variable names themselves are not. Suggested fix: link each variable name to its anchor in the wiki, or create the wiki sections if they don't exist.

### 4.23. Horizontal rules

No issues found.

### 4.24. Inline paths

No issues found.

### 4.25. Branch-on-remote references

Not applicable.

### 4.26. Example IP address

Not applicable (placeholder used correctly).

---

## TODOs

No TODOs found.

---

## Empty sections

No empty sections found.

---

## Summary

| Category | Count |
|---|---|
| Conceptual [High] | 1 |
| Conceptual [Medium] | 5 |
| Conceptual [Low] | 5 |
| Convention [High] | 0 |
| Convention [Medium] | 2 |
| Convention [Low] | 1 |
| TODOs | 0 |
| Empty sections | 0 |
| **Total** | **14** |

**Overall:** The task provides a clear, well-structured walkthrough for setting up `Grafana` with good use of `SQL` examples and a useful reflection step. The most critical issue is that two acceptance criteria (dashboard panels and reflection comment) cannot be verified by the autochecker through standard channels (D12). The task also has a structural inconsistency: it modifies `docker-compose.yml` but uses a no-code ending pattern, with the "Finish the task" heading mismatched to a "Close the issue" body (D9, Section 1). Adding a troubleshooting block for the `Docker` step, checkpoints for steps 1.2 and 1.5, and linking environment variable names to their wiki sections would improve the student experience.
