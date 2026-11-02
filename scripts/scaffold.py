"""Scaffold a project from assets/template, or list the placeholders left in one.

    scaffold.py create <target-dir> --answers answers.json
    scaffold.py report <target-dir>

Standard library only. Run test_scaffold.py beside this file after changing it.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).parent.parent / "assets" / "template"

# Every answerable field, with the question its placeholder shows when unanswered.
FIELDS = {
    "project_name": "product name",
    "pitch": "one sentence on what this product is",
    "owner": "who is asking for this, by name or role",
    "problem": "how this works today and what is wrong with it",
    "goal": "what the first release must do, as a short list",
    "success": "how we will know the first release worked",
    "users": "who uses it and what they need to see or do",
    "rules": "business rules that must always hold",
    "data": "what data the product starts from and where it lives",
    "out_of_scope": "what is deliberately not in the first release",
    "storage": "database or storage, such as SQLite",
    "deploy": "where this will run",
    "model": "default model id on OpenRouter, such as openai/gpt-6-luna",
    "fonts": "fonts for headings, body and code",
    "colors": "primary, secondary and alert colors, as hex",
    "tone": "tone of voice for on-screen text",
    "stack": "language, framework and package manager",
    "install_command": "command that installs everything",
    "run_command": "command that starts the app",
    "check_command": "command that runs every check",
}
# These land inside code strings, so they must not be able to break the syntax.
CODE_FIELDS = ("project_name", "model")
SWITCHES = ("agent", "dashboard", "e2e", "custom")

# Paths that exist only when all the named flags are on. Everything else is always written.
PATH_RULES = {
    "backend/": ["default"],
    "pyproject.toml": ["default"],
    "lefthook.yml": ["default"],
    ".python-version": ["default"],
    ".nvmrc": ["default"],
    ".npmrc": ["default"],
    "agent/": ["default", "agent"],
    ".env.example": ["default", "agent"],
    "dashboard/": ["default", "dashboard"],
    "eslint.config.js": ["default", "dashboard"],
    "tsconfig.json": ["default", "dashboard"],
    "docs/BRAND.md": ["dashboard"],
    "e2e/": ["default", "e2e"],
    "playwright.config.ts": ["default", "e2e"],
}

DASHBOARD_DEPS = {
    "@eslint/js": "^10.0.1",
    "@testing-library/dom": "^10.4.2",
    "@testing-library/react": "^16.3.3",
    "@types/node": "^26.6.3",
    "@types/react": "^19.3.0",
    "@types/react-dom": "^19.3.0",
    "@vitejs/plugin-react": "^6.1.1",
    "@vitest/coverage-v8": "^5.0.2",
    "@vitest/eslint-plugin": "^1.6.27",
    "concurrently": "^10.0.5",
    "eslint": "^10.11.0",
    "eslint-config-prettier": "^10.1.8",
    "eslint-plugin-jsx-a11y-x": "^0.2.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.7",
    "eslint-plugin-sonarjs": "^4.2.1",
    "globals": "^17.12.0",
    "jsdom": "^30.1.1",
    "prettier": "^3.9.9",
    "typescript": "6.0.3",
    "typescript-eslint": "^8.70.1",
    "vite": "^8.3.1",
    "vitest": "^5.0.2",
}
E2E_DEPS = {"@playwright/test": "^1.63.0", "eslint-plugin-playwright": "^2.12.0"}


def fail(message: str) -> None:
    sys.exit(f"scaffold: {message}")


def placeholder(field: str) -> str:
    return f"[PLACEHOLDER: {FIELDS[field]}]"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"


def load_answers(answers: dict, target: Path) -> tuple[dict, dict]:
    """Split the answers into flags and template values, with placeholders for gaps."""
    unknown = set(answers) - set(FIELDS) - set(SWITCHES)
    if unknown:
        fail(f"unknown answers: {sorted(unknown)}. Known: {[*FIELDS, *SWITCHES]}")

    flags = {name: bool(answers.get(name)) for name in SWITCHES}
    flags["default"] = not flags["custom"]
    if flags["e2e"] and not flags["dashboard"]:
        fail("e2e tests drive the dashboard, so e2e needs dashboard")
    if flags["custom"] and (flags["agent"] or flags["e2e"]):
        fail("agent and e2e are templates for the default stack; drop them with custom")

    values = {}
    for field in FIELDS:
        answer = answers.get(field)
        answer = answer.strip() if isinstance(answer, str) else answer
        values[field.upper()] = answer or placeholder(field)
    for field in CODE_FIELDS:
        if field in answers and re.search(r'["\\<>{}\n]', str(answers[field] or "")):
            fail(f'{field} cannot contain " \\ < > {{ }} or a line break')

    py_dirs = ["backend", "agent"] if flags["agent"] else ["backend"]
    ts_dirs = ["dashboard", "e2e"] if flags["e2e"] else ["dashboard"]
    values |= {
        "SLUG": slugify(str(answers.get("project_name") or target.resolve().name)),
        "PY_DIRS": json.dumps(py_dirs),
        "PY_GLOBS": json.dumps([f"{d}/**/*.py" for d in py_dirs]),
        "PY_GLOB_HOOK": "{" + ",".join(py_dirs) + "}/**/*.py",
        "TS_GLOB_HOOK": "{" + ",".join(ts_dirs) + "}/**",
    }
    return flags, values


def resolve_conditionals(text: str, flags: dict) -> str:
    """Keep the lines inside @@if <flag> / @@if !<flag> ... @@end blocks whose test holds."""
    kept, tests = [], []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("@@if "):
            name = stripped.removeprefix("@@if ")
            tests.append(flags[name.lstrip("!")] != name.startswith("!"))
        elif stripped == "@@end":
            tests.pop()
        elif all(tests):
            kept.append(line)
    return "".join(kept)


def render(text: str, flags: dict, values: dict) -> str:
    text = resolve_conditionals(text, flags)
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: str(values[m[1]]), text)


def wanted(relative: str, flags: dict) -> bool:
    for prefix, needed in PATH_RULES.items():
        if relative == prefix or (prefix.endswith("/") and relative.startswith(prefix)):
            return all(flags[name] for name in needed)
    return True


def package_json(flags: dict, slug: str) -> str:
    """Build package.json for the chosen parts of the stack."""
    dashboard, e2e = flags["dashboard"], flags["e2e"]
    backend = "uv run -m uvicorn backend.main:app --reload --reload-dir backend"
    ts_paths = "dashboard e2e *.config.*" if e2e else "dashboard *.config.*"
    python = (
        "uv run ruff format --check && uv run ruff check && pyright && uv run pytest -q"
    )
    checks = ["npm run check:python"]
    scripts = {"prepare": "lefthook install"}
    format_command = "uv run ruff format"
    if e2e:
        scripts["prepare"] += " && playwright install chromium"
    if dashboard:
        checks.append("npm run check:ts")
        format_command += f" && prettier --write -u {ts_paths}"
        scripts |= {
            "dev": "concurrently -k -n backend,dashboard npm:dev:backend npm:dev:dashboard",
            "dev:backend": backend,
            "dev:dashboard": "vite dashboard",
        }
    else:
        scripts["dev"] = backend
    if e2e:
        checks.append("npm run e2e")
    scripts |= {
        "format": format_command,
        "check": " && ".join(checks),
        "check:python": python,
    }
    if dashboard:
        scripts["check:ts"] = (
            f"prettier --check -u {ts_paths} && eslint {ts_paths} && tsc"
            " && vitest run --root dashboard --coverage"
        )
    if e2e:
        scripts["e2e"] = "playwright test"

    dev = {"lefthook": "^2.1.14", "pyright": "^1.1.414"}
    if dashboard:
        dev |= DASHBOARD_DEPS
    if e2e:
        dev |= E2E_DEPS
    package = {
        "name": slug,
        "private": True,
        "type": "module",
        "engines": {"node": "^22.22.2 || ^24.15.0 || >=26.0.0"},
        "scripts": scripts,
    }
    if dashboard:
        package["dependencies"] = {"react": "^19.3.0", "react-dom": "^19.3.0"}
    package["devDependencies"] = dict(sorted(dev.items()))
    package["allowScripts"] = {"lefthook": False, "fsevents": False}
    return json.dumps(package, indent=2) + "\n"


def planned_files(flags: dict, values: dict) -> dict[str, str]:
    files = {}
    for path in sorted(TEMPLATE.rglob("*")):
        relative = path.relative_to(TEMPLATE).as_posix()
        if path.is_dir() or "__pycache__" in relative or not wanted(relative, flags):
            continue
        files[relative] = render(path.read_text(encoding="utf-8"), flags, values)
    if flags["default"]:
        files["package.json"] = package_json(flags, values["SLUG"])
    return files


def create(target: Path, answers: dict) -> list[str]:
    flags, values = load_answers(answers, target)
    files = planned_files(flags, values)
    collisions = [name for name in files if (target / name).exists()]
    if collisions:
        fail(f"these already exist in {target}, nothing was written: {collisions}")
    for name, content in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        # .gitattributes sets eol=lf, so write LF on Windows too.
        with path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(content)
    return sorted(files)


def report(target: Path) -> list[str]:
    """Return every unresolved placeholder as path:line: text."""
    skipped = {".git", ".venv", "node_modules", "__pycache__", "coverage"}
    lockfiles = {"uv.lock", "package-lock.json"}
    found = []
    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target)
        if (
            path.is_dir()
            or skipped & set(relative.parts)
            or path.name in lockfiles
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for number, line in enumerate(text.splitlines(), start=1):
            for match in re.findall(r"\[PLACEHOLDER[^\]]*\]", line):
                found.append(f"{relative.as_posix()}:{number}: {match}")
    return found


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("create")
    create_parser.add_argument("target", type=Path)
    create_parser.add_argument("--answers", type=Path, required=True)
    report_parser = commands.add_parser("report")
    report_parser.add_argument("target", type=Path)
    args = parser.parse_args()

    if args.command == "create":
        answers = json.loads(args.answers.read_text(encoding="utf-8"))
        written = create(args.target, answers)
        print(f"Wrote {len(written)} files to {args.target}:")
        print("\n".join(f"  {name}" for name in written))
    found = report(args.target)
    print(f"\n{len(found)} unresolved placeholders:")
    print("\n".join(f"  {line}" for line in found))


if __name__ == "__main__":
    main()
