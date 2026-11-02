# Process

@@if default
`uv sync` and `npm install` at the repo root install everything, including a git pre-commit hook. `npm run dev` starts the app.

`npm run check` runs every check:

- Python: ruff (lint and format), pyright, and pytest with 80% coverage
@@if dashboard
- TypeScript: ESLint, Prettier, tsc, and vitest with 80% coverage
@@end
@@if e2e
- Playwright end-to-end tests
@@end

The pre-commit hook runs the format, lint, type and unit test checks on every commit.
@@end
@@if custom
Install everything with: {{INSTALL_COMMAND}}

Run the app with: {{RUN_COMMAND}}

Run every check (format, lint, types, tests with 80% coverage) with: {{CHECK_COMMAND}}

A pre-commit hook runs the same checks on every commit.
@@end

## Planning

When asked to plan, as in "Please plan the first release", write the plan to `docs/PLAN.md` and write no code.

- Split the work into phases, usually 5 or 6, each building on the last.
- Give each phase detailed success criteria that you can verify yourself: tests that pass, commands and their output, API calls and their responses, and pages you check in the browser. Write each one as a checkbox.
- Then stop and wait until you are asked to implement the plan.

## Implementing

When asked to implement the plan, build every phase in order without stopping. For each phase:

1. Build it, with tests.
2. Check every success criterion and fix whatever fails.
3. Tick off its criteria in the plan and update `docs/STATUS.md`.
4. Commit. The pre-commit hook runs the checks; if it fails, fix the problem and commit again.

When the last phase is done, run every check and report the results.

## Rules

- Add tests with each change.
@@if agent
- Tests never call a model; use a stub model.
@@end
- Outside a plan, commit each change once you have checked it.
- Run every check before you hand work over.
- Never use `git commit --no-verify`.
- Never lower a threshold, turn off a rule or exclude a file to get a green run. If a rule looks wrong, stop and ask.
- Keep `docs/STATUS.md` up to date.
- Never push.
@@if agent
- Don't open `data/evals/` unless you're asked to.
@@end
@@if default
- Everything must work on Windows and macOS: write `package.json` scripts as `uv run` commands or `.mjs` files.
@@end
