# project-scaffold

A [Claude Code](https://claude.com/claude-code) skill that sets up a new coding project so it starts from a **verified, agent-ready base** instead of a blank folder.

It asks a few questions, then generates a written project contract, a hello-world app that runs end to end, and strict quality checks that are on from the first commit. A coding agent can then plan and build against it. The skill **stops after setup and builds no features**.

## What you get

| Piece | What it is |
| --- | --- |
| `AGENTS.md` | Tells coding agents what to read first, how the owner and agent work together, and to stop and ask while any placeholder is unresolved. |
| `docs/` contract | `SPEC.md`, `TECH_STACK.md`, `CODE_STANDARDS.md`, `PROCESS.md`, `STATUS.md`, and `BRAND.md` (dashboard only). |
| Hello-world app | A FastAPI backend with one route, `GET /api/health`. Optional LangChain agent, React dashboard and Playwright end-to-end test. |
| Quality gates | ruff, pyright, ESLint, Prettier, `tsc`, pytest and vitest with 80% coverage, plus a pre-commit hook (lefthook). |

## Two rules it follows

1. **Never invent a requirement.** Anything you don't answer becomes a visible `[PLACEHOLDER: ...]` instead of a plausible guess. Wrong guesses at setup turn into a wrong plan and a wrong build.
2. **Stop when setup is done.** It doesn't write a plan or build features. That is a separate request, after you've reviewed the base.

## Install

A skill is just a folder. Clone this repo into your Claude Code skills directory:

```bash
git clone https://github.com/FaizulZuraimi/project-scaffold.git ~/.claude/skills/project-scaffold
```

On Windows Command Prompt, use `"%USERPROFILE%\.claude\skills\project-scaffold"` as the destination.

### Requirements

- [`uv`](https://docs.astral.sh/uv/) (runs the script and manages Python 3.12)
- Node.js `^22.22.2 || ^24.15.0 || >=26.0.0` (`engine-strict` is on, so older versions make `npm install` fail)
- `git` (the pre-commit hook install needs a repo)

## Use

Ask Claude Code for a new project in plain words. The skill triggers on requests to start, bootstrap, set up or scaffold a project or repo:

> Set up a new project for me in `C:\projects\harbor`. It's called Harbor Service Desk, for a marina. Staff track boat maintenance on paper today and jobs get lost. I want an AI agent and a dashboard.

Claude then works through four steps:

1. **Ask.** Target folder, stack, which components you want, and free-text answers for the documents. Skipped answers become placeholders.
2. **Generate.** Writes your answers to a temporary JSON file and runs `scripts/scaffold.py`, which refuses to overwrite anything that already exists.
3. **Verify.** Installs dependencies and runs `npm run check`, so the skeleton is proven to work. Failures are reported, never hidden by loosening a rule.
4. **Hand over.** Reports where the project is, what passed or failed, and the list of open placeholders, then stops. It doesn't commit or push.

After that, fill in the placeholders, read `docs/SPEC.md` and `docs/TECH_STACK.md`, and tell your coding agent: *"Please plan the first release."*

### Components

| Component | Adds | Needs |
| --- | --- | --- |
| *(always, default stack)* | FastAPI backend, `pyproject.toml`, `package.json`, lefthook pre-commit hook | |
| `agent` | LangChain agent using OpenRouter, with `.env.example` | |
| `dashboard` | React 19 + Vite page, vitest, ESLint, Prettier, `tsc`, `docs/BRAND.md` | |
| `e2e` | Playwright test of the dashboard | `dashboard` |

### Default vs custom stack

The default stack is **FastAPI, uv, npm and Python 3.12**. For any other language or framework (a Go CLI, a frontend with no backend), choose **custom**. A custom stack gets only the documents, `.gitignore` and `.gitattributes`. The skill does not improvise an app, and `docs/STATUS.md` tells the first plan to set up the code and checks.

### Answers the documents use

| Field | Meaning |
| --- | --- |
| `project_name`, `pitch`, `owner` | What it's called, one sentence on what it is, who asked for it |
| `problem`, `goal`, `success` | How it works today, what release one must do, how you'll know it worked |
| `users`, `rules`, `data`, `out_of_scope` | Who uses it, rules that must hold, starting data, what's not for now |
| `storage`, `deploy` | Database or storage, where it runs |
| `model` | Default OpenRouter model id (with `agent`) |
| `fonts`, `colors`, `tone` | Look and voice (with `dashboard`) |
| `stack`, `install_command`, `run_command`, `check_command` | Details for a custom stack |

### Running the script directly

```bash
# answers.json: {"project_name": "Tidewater", "agent": true, "dashboard": true, "e2e": true}
uv run --no-project python scripts/scaffold.py create <target-dir> --answers answers.json
uv run --no-project python scripts/scaffold.py report <target-dir>   # list unresolved placeholders
```

It uses the standard library only. Omit any field you haven't been given; it becomes a placeholder.

## What the generated project runs

```bash
uv sync && npm install    # install everything, including the git pre-commit hook
npm run dev               # start the app
npm run check             # run every check
```

`npm run check` runs ruff (lint + format), pyright and pytest with 80% coverage. With `dashboard` it adds ESLint, Prettier, `tsc` and vitest with 80% coverage, and with `e2e` it adds Playwright. The ruff rule set is strict (complexity limit 10, security and bugbear rules on). The pre-commit hook formats staged files and runs the matching checks on every commit.

## Repo layout

```
SKILL.md                  # the skill: when it triggers and the four steps
scripts/
  scaffold.py             # create / report commands (standard library only)
  test_scaffold.py        # self-check for scaffold.py
assets/template/          # files copied into a new project (default stack)
evals/                    # three end-to-end test cases for the skill
  full-brief-full-stack/  # complete brief, every component
  vague-request-no-questions/  # "don't ask me anything" request
  custom-go-stack/        # non-default stack
```

## Developing the skill

After changing `scripts/scaffold.py` or the template, run the self-check (needs nothing installed):

```bash
python scripts/test_scaffold.py
```

It renders every component combination, checks that the right files appear, that unanswered fields become placeholders and answered ones don't, and that bad input is refused and nothing is ever overwritten.

Each folder in `evals/` holds a `prompt.md` (the request), a `case.yaml` (the expected outcome) and `graders/` (checks to score a run).

## Windows note

Some Python dependencies exceed the 260-character path limit when the project sits in a deeply nested folder. If you see a `ModuleNotFoundError` for a package listed in `uv.lock`, or pytest crashes on a long module name, move the project to a shorter path.

## License

[MIT](LICENSE)
