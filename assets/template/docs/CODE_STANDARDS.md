# Code standards

1. Keep it simple, do not overcomplicate.
2. Comments only when necessary.
3. Be concise: a short README and no emojis.
4. IMPORTANT: avoid overly defensive code. Handle exceptions only when necessary.
@@if default
5. Use uv: ALWAYS `uv run`, NEVER `python3`.
@@if dashboard
6. TypeScript: strict mode, never `any`.
@@end
@@end
