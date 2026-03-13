# Review — `instructors/lab-plan.md`

**Date:** 2026-03-11
**Convention files used:** [`contributing/conventions/writing/lab-plan.md`](../../../contributing/conventions/writing/lab-plan.md)

---

## Lab plan findings

### D1. Learning outcome quality

No issues found.

### D2. Bloom's taxonomy coverage

No issues found.

### D3. Lab story coherence

No issues found.

### D4. Task sequencing and dependencies

No issues found.

### D5. Acceptance criteria quality

1. **[Low]** Lines 57–58, 75–76, 94, 101, 117 — Acceptance criteria across multiple tasks include specific CLI invocations with exact flags and query strings (e.g., `uv run poe cli metrics --query 'rate(http_requests_total[1m])'`), as well as specific expected answers (`victorialogs`, `rate()`). Convention 8.5 says "Do not invent specific technology choices, file paths, or implementation details beyond what is needed to illustrate the plan." **Suggested fix:** Abstract the criteria to describe expected behaviour without prescribing exact CLI syntax or specific answer values — leave those details for the task files.

### D6. Outcome-to-task alignment

No issues found.

### D7. Structural compliance

1. ~~**[High]** Lines 51, 71, 90, 112 — All four task summaries are written as single paragraphs. Convention 8.4 requires "five to ten sentences split across two to four short paragraphs." **Suggested fix:** Break each summary into two to four paragraphs on natural topic boundaries (e.g., setup and exploration in one paragraph, implementation details in the next).~~

2. **[Medium]** Line 71 — [Task 2 summary](../../lab-plan.md#task-2--the-documentation-agent) contains only 4 sentences. Convention 8.4 requires five to ten sentences. **Suggested fix:** Add one to six sentences to expand on what the student does (e.g., describe argument handling, the reference pattern, or how the two subcommands differ).

### D8. Practical feasibility

1. **[Low]** Line 33 — Task 3 depends on the Qwen API, an external free-tier service with a rate limit of 1000 requests per day. Convention D8 checks for dependencies on "external services with rate limits, approval queues, or uptime risks." The plan acknowledges the rate limit but does not address a downtime or deprecation scenario. **Suggested fix:** Mention a fallback strategy (e.g., a local model or mock LLM responses) if the API becomes unavailable.

### D9. Student experience level fit

No issues found.

### D10. Main goals clarity

1. ~~**[Low]** Line 9 — Grammatical error: "you can let an agent to debug" should be "you can let an agent debug" (bare infinitive after "let"). **Suggested fix:** Remove "to" before "debug."~~

---

## TODOs

No TODOs found.

## Empty sections

No empty sections found.

---

## Summary

| Category | Count |
|---|---|
| Lab plan [High] | 0 |
| Lab plan [Medium] | 1 |
| Lab plan [Low] | 2 |
| TODOs | 0 |
| Empty sections | 0 |
| **Total** | **3** |

**Overall:** The paragraph structure of all four task summaries has been fixed and the grammar error in Main goals has been corrected. Three findings remain: Task 2's summary is one sentence short of the five-sentence minimum (Medium), acceptance criteria across multiple tasks include overly specific CLI syntax and expected answers (Low), and no fallback strategy is mentioned for the Qwen API dependency (Low). All remaining issues require author content decisions.
