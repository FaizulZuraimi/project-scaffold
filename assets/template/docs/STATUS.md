# Status

@@if default
A hello-world skeleton with every check in place:

- `backend/`: one route, `GET /api/health`
@@if agent
- `agent/`: the entry point `run(request, thread_id)`, with one tool that calls the health route
@@end
@@if dashboard
- `dashboard/`: one page that shows whether the backend is up
@@end
@@if e2e
- `e2e/`: one test of that page
@@end
@@end
@@if custom
Documents only. No code or checks exist yet, so the first plan must set them up.
@@end

Nothing of {{PROJECT_NAME}} itself is built yet. Update this file as you build.
