"""Self-check for scaffold.py. Run it directly; it needs nothing installed."""

import json
import tempfile
import tomllib
from pathlib import Path

import scaffold

FULL = {"agent": True, "dashboard": True, "e2e": True}


def build(answers: dict) -> tuple[Path, dict[str, str]]:
    target = Path(tempfile.mkdtemp()) / "my-app"
    written = scaffold.create(target, answers)
    return target, {n: (target / n).read_text(encoding="utf-8") for n in written}


def test_every_combination_renders_cleanly():
    for answers in (
        {},
        {"agent": True},
        {"dashboard": True},
        {"dashboard": True, "e2e": True},
        FULL,
        {"custom": True},
        {"custom": True, "dashboard": True},
    ):
        _, files = build(answers)
        for name, text in files.items():
            assert "@@" not in text, (answers, name)
            assert "{{" not in text.replace("{{ ", ""), (answers, name)
        if not answers.get("custom"):
            package = json.loads(files["package.json"])
            tomllib.loads(files["pyproject.toml"])
            assert package["name"] == "my-app"
            assert "backend/main.py" in files


def test_components_control_files():
    _, backend_only = build({})
    assert not {"agent/main.py", "docs/BRAND.md", "eslint.config.js"} & set(backend_only)
    assert "check:ts" not in backend_only["package.json"]
    assert "typescript" not in backend_only["lefthook.yml"]
    assert "agent" not in backend_only["pyproject.toml"]

    _, no_e2e = build({"dashboard": True})
    assert "playwright" not in no_e2e["eslint.config.js"]
    assert "e2e" not in no_e2e["package.json"]
    assert "e2e" not in no_e2e["tsconfig.json"]

    _, custom = build({"custom": True})
    assert not {"package.json", "backend/main.py", "pyproject.toml"} & set(custom)
    assert "[PLACEHOLDER: command that runs every check]" in custom["docs/PROCESS.md"]


def test_unanswered_fields_become_placeholders_and_answers_do_not():
    target, files = build(FULL)
    assert "[PLACEHOLDER: product name]" in files["backend/main.py"]
    assert all("[PLACEHOLDER" in files[f"docs/{n}.md"] for n in ("SPEC", "BRAND"))
    found = scaffold.report(target)
    assert any(line.startswith("docs/SPEC.md:") for line in found)

    target, files = build(FULL | {"project_name": "Tide Water", "goal": "@@end {{X}}"})
    assert 'title="Tide Water"' in files["backend/main.py"]
    assert "@@end {{X}}" in files["docs/SPEC.md"]  # answers are not re-expanded
    assert json.loads(files["package.json"])["name"] == "tide-water"
    assert not [line for line in scaffold.report(target) if "product name" in line]


def expect_exit(call) -> None:
    try:
        call()
    except SystemExit:
        return
    raise AssertionError("expected the scaffold to refuse")


def test_refuses_bad_input_and_never_overwrites():
    expect_exit(lambda: build({"nmae": "typo"}))
    expect_exit(lambda: build({"e2e": True}))
    expect_exit(lambda: build({"custom": True, "agent": True}))
    expect_exit(lambda: build({"project_name": 'say "hi"'}))

    target, _ = build({})
    (target / "docs/SPEC.md").write_text("mine", encoding="utf-8")
    expect_exit(lambda: scaffold.create(target, {}))
    assert (target / "docs/SPEC.md").read_text(encoding="utf-8") == "mine"


if __name__ == "__main__":
    for name, check in list(globals().items()):
        if name.startswith("test_"):
            check()
            print("ok", name)
