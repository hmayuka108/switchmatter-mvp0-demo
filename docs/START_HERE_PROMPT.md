# Prompt to Give an AI Coding Agent

Use the following as the first implementation instruction after placing this starter pack in the repository.

---

You are implementing SwitchMatter MVP0.

Before writing or editing code, read these files in full:

1. `AGENTS.md`
2. `docs/SPEC.md`
3. `docs/DATA_SCHEMA.md`
4. `docs/SCORING_LOGIC.md`
5. `docs/TASKS.md`
6. `tests/expected_behaviour.json`

Treat those documents as the implementation contract.

Important constraints:

- Do not use an LLM, AI API, OCR, embeddings, or external material search.
- Do not guess missing information.
- The current product/component data must actually be extracted from uploaded PDF text, not hard-coded from the filename.
- Keep `null` when the deterministic parser cannot find an explicit value.
- Regulation FAIL excludes a candidate before scoring.
- Regulation UNKNOWN creates a Potential Candidate and does not automatically enter scoring.
- Score only Eligible Candidates.
- MVP0 scoring dimensions are Cost and Properties only.
- Use the exact formulas in `docs/SCORING_LOGIC.md`.
- Do not add Recyclability Score.
- Do not add user-adjustable scoring weights.
- Preserve intermediate calculations and rule explanations.

First, inspect the existing codebase and tell me:

1. the current frontend/backend stack,
2. which existing files should be reused,
3. the minimal files/modules you propose to add,
4. any conflict between the current codebase and the MVP0 specification.

Do not implement anything until after this short implementation plan is produced.

After the plan is accepted, implement `docs/TASKS.md` one task at a time and run the relevant acceptance test after each task.

---
