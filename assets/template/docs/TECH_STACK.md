# Tech stack

@@if default
- `backend/`: FastAPI. Every API operation has an `operation_id`, a one-line docstring and no optional inputs.
@@if agent
- `agent/`: LangChain's `create_agent` on OpenRouter, with one entry point. It reaches the product only through the backend's API. It uses `{{MODEL}}` by default, or the model in the environment variable `MODEL_NAME` if set, such as `openrouter/free`.
@@end
@@if dashboard
- `dashboard/`: React, Vite and TypeScript.
@@end
@@if e2e
- `e2e/`: Playwright tests.
@@end
- `data/`: the business data the backend starts from.
@@if agent
- `data/evals/`: if we hold back examples to check the agent's work, they go here. The agent never sees them.
@@end
- Storage: {{STORAGE}}
- Deployment: {{DEPLOY}}

Python 3.12 with uv, all in the root `pyproject.toml`. Node 26.
@@if agent
The OpenRouter key is `OPENROUTER_API_KEY` in `.env`; `.env.example` lists what's needed.
@@end
@@end
@@if custom
- Language and framework: {{STACK}}
- Storage: {{STORAGE}}
- Deployment: {{DEPLOY}}
@@end
