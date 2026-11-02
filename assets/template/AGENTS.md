# {{PROJECT_NAME}}

{{PITCH}}

## Unresolved placeholders

IMPORTANT: this project came from a scaffold. Square-bracketed text that starts with the word PLACEHOLDER is a question nobody has answered yet. Before you plan or build anything, search the repo for `PLACEHOLDER:`, leaving out this file's note. If you find any, list them and ask for the answers. Do not guess them, and do not plan or build until they are resolved or the owner tells you to go ahead without them.

## Start here

IMPORTANT: before you plan, build or change anything in the product, or answer questions about it, read each of these files in full:

- `docs/SPEC.md`: what the business needs
- `docs/TECH_STACK.md`: the tech choices
- `docs/CODE_STANDARDS.md`: how to write the code
- `docs/PROCESS.md`: how to plan, build and check the work
@@if dashboard
- `docs/BRAND.md`: the look
@@end
- `docs/STATUS.md`: what's built so far and how to run it
- `docs/PLAN.md`: the plan for the first release, once it exists. Later plans go in their own documents, such as `docs/PLAN_<NAME>.md`

## Your role in the build

The documents in `docs/` are the customer's requirements. The owner directs the work and reviews your plans and builds. You plan, build and check the work as `docs/PROCESS.md` describes.

Write plans the owner can review: say what each phase builds and why you chose that approach.

## The builds

Each build goes in two steps, with the owner's review in between. First a request like "Please plan <the work> in docs/<NAME>.md", which writes the plan to `docs/PLAN_<NAME>.md`, then "Please implement the plan for <the work>". The first build works from `docs/SPEC.md` itself: "Please plan the first release" writes `docs/PLAN.md`, then "Please implement the plan for the first release".

Build only what the documents in `docs/` ask for. Don't build ahead.

## Folders

- `docs/`: the main documentation for the product
@@if default
- `backend/`: the API
@@end
@@if agent
- `agent/`: the AI agent
@@end
@@if default
@@if dashboard
- `dashboard/`: the web front end
@@end
@@end
@@if e2e
- `e2e/`: end-to-end tests
@@end
- `data/`: the business data
