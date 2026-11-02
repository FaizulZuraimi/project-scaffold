---
name: project-scaffold
description: Scaffolds a new coding project with a full agent-ready setup, so a project starts from a verified base rather than a blank folder. It asks clarifying questions, then generates AGENTS.md, a docs/ contract (spec, tech stack, code standards, process, brand, status), a running hello-world app (FastAPI backend, optional LangChain agent, React dashboard, Playwright tests), and quality gates (ruff, pyright, ESLint, 80% coverage, pre-commit hook). Anything unanswered becomes a clear [PLACEHOLDER]. Use this whenever the user wants to start, bootstrap, set up, kick off, or scaffold a new project, app, product, or repo, wants a good starting point or a project template, or asks for a setup like the UnderCover course project, even if they don't say "scaffold". It stops after setup and builds no features.
---

# Project scaffold

Sets up a new project the way the UnderCover course project is set up: a written contract in `docs/`, a hello-world app that runs end to end, and checks that are strict from the first commit. A coding agent can then plan and build against it.

The point is a base the owner has checked before any real work begins. Wrong guesses at this stage turn into a wrong plan and a wrong build, so this skill would rather leave a visible gap than a plausible invention. Two rules follow from that:

- **Never invent a requirement.** If the owner did not say it, it stays a `[PLACEHOLDER]`. The script does this for any field you leave out, so leave fields out rather than filling them with your own ideas. Reword what the owner said, but add nothing to it.
- **Stop when the setup is done.** Building features here skips the review this skill exists for.

## Step 1: Ask

Take what the user has already said, then ask for the rest in one sitting. Don't re-ask what they've answered, and don't skip the round because the request looks complete: confirm the target folder and the components at the least.

Ask with `AskUserQuestion`, up to four questions at a time, for choices. Ask for the free-text items in one plain message, and tell the user that anything they skip becomes a placeholder, so skipping is fine.

**Setup choices**
- Target folder, which is usually new. Never use the current repo unless the user says so.
- Stack: the default stack, or something else (custom). The default is FastAPI, uv, npm and Python 3.12. Choose custom for any other language or framework; see Step 2.
- Components on top of the backend: `agent`, `dashboard`, `e2e`. The backend is always there on the default stack, and `e2e` needs `dashboard`.
- A project that doesn't fit, such as a frontend with no backend or an agent with no API, is custom.

**Answers for the documents** (the field name in brackets)
- Product name (`project_name`) and one sentence on what it is (`pitch`)
- Who is asking for it (`owner`)
- How it works today (`problem`)
- What the first release must do (`goal`)
- How you'll know it worked (`success`)
- Who uses it and what they need (`users`)
- Rules that must always hold (`rules`)
- The data it starts from (`data`)
- What's not for now (`out_of_scope`)
- Storage (`storage`) and where it will run (`deploy`)
- With `agent`: default OpenRouter model id (`model`)
- With `dashboard`: `fonts`, `colors`, `tone`
- With custom: `stack`, `install_command`, `run_command`, `check_command`

If there's no way to ask, for example in an unattended run or when the user says to go ahead without questions, carry on with what you have. Say in your final message that you could not ask.

## Step 2: Generate

Write the answers to a JSON file in a temporary location, not in the target folder. Use the field names above, with `true` for each component and `"custom": true` for a custom stack. Omit whatever is unanswered.

```json
{"project_name": "Tidewater", "goal": "- Show each boat's next service date", "agent": true, "dashboard": true, "e2e": true}
```

Then run the script, using this skill's real path:

```
uv run --no-project python "<skill-path>/scripts/scaffold.py" create "<target>" --answers "<answers.json>"
```

It writes the files and lists the placeholders. It refuses to overwrite anything: if it names collisions, show them to the user and let them decide. Don't delete anything to get past it.

**Custom stack:** the script writes only the documents, `.gitignore` and `.gitattributes`, because the templates are for the default stack. Don't improvise an app for another language. Step 3 is skipped, and `docs/STATUS.md` tells the first plan to set up the code and checks.

## Step 3: Verify the skeleton runs

Skip this for a custom stack. Otherwise, run these from the target folder.

1. Check the Node version first: `node -v` must satisfy `engines` in `package.json` (`^22.22.2 || ^24.15.0 || >=26.0.0`). `.npmrc` sets `engine-strict`, so a lower version makes `npm install` fail. If it's too low, don't remove `engine-strict` or loosen `engines`. Run `git init`, `uv sync`, `uv run ruff format`, `uv run ruff check` and `uv run pytest -q` instead, report the npm steps as not run, and tell the user to upgrade Node and run them.
2. `git init` if it isn't a repo yet. The hook install needs one.
3. `uv sync`, then `npm install`.
4. `npm run format`. A long product name can change how a line wraps.
5. `npm run check`. This can take several minutes on Windows, so give it a long timeout and don't pipe it through `tail`, which hides where it is.

On Windows, a `ModuleNotFoundError` for a package you can see in `uv.lock`, or a pytest crash on a long module name, usually means the folder path is too long: some dependencies pass the 260-character limit under a deep folder. Tell the user to move the project to a shorter path.

If a check fails, fix the cause. Don't lower a threshold, disable a rule or exclude a file to get a green run. A failure you can't fix goes in the handover as a failure. Leave `.env` to the user; with `agent`, `.env.example` lists what it needs. Don't commit or push: the owner reviews first.

## Step 4: Hand over and stop

End with this, in order:

1. **Where it is**, and which components it has.
2. **Check results:** what you ran and what passed, failed or was skipped, with the real output for anything that failed.
3. **Open placeholders:** the list from `scaffold.py report "<target>"`, grouped by file. Run it again if you changed anything. Placeholders in code files show up on screen, such as the product name in the page title.
4. **The next steps:** fill the placeholders, read `docs/SPEC.md` and `docs/TECH_STACK.md`, then ask the coding agent to "Please plan the first release". The generated `AGENTS.md` tells agents to stop and ask while placeholders remain.

Then stop. Don't write `docs/PLAN.md` and don't build features, even if the spec looks ready. If the user wants to go on, that's a new request.
