#!/usr/bin/env python3
"""Structural validation for this exported repository.

Checks what an outside reader can check without the private engine:
  1. every knowledge record's frontmatter matches schema/knowledge-record.schema.json
  2. record id equals its filename stem
  3. every skill has SKILL.md with name/description/version, name == directory name
  4. no personal absolute paths (/Users/<name>/..., /home/<name>/...) survived export
  5. no credential-shaped strings

Exit code 1 on any failure. Run: python tools/validate_export.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "knowledge-record.schema.json").read_text())

PERSONAL_PATH = re.compile(r"/(?:Users|home)/(?!runner\b)[A-Za-z0-9._-]+/")
SECRET_SHAPES = [
    re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAIza[A-Za-z0-9_\-]{30,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[4:end + 1]) or {}


def main() -> int:
    problems: list[str] = []
    validator = Draft202012Validator(SCHEMA)

    for md in sorted((ROOT / "knowledge").glob("*.md")):
        meta = frontmatter(md.read_text(encoding="utf-8"))
        if meta is None:
            problems.append(f"{md.name}: missing or unterminated frontmatter")
            continue
        for err in validator.iter_errors(meta):
            problems.append(f"{md.name}: {'.'.join(str(p) for p in err.path) or '<root>'}: {err.message}")
        if meta.get("id") and meta["id"] != md.stem:
            problems.append(f"{md.name}: id {meta['id']!r} != filename stem {md.stem!r}")
        if meta.get("shareable") is not True:
            problems.append(f"{md.name}: exported but shareable is not true")

    for skill_md in sorted((ROOT / "skills").glob("**/SKILL.md")):
        meta = frontmatter(skill_md.read_text(encoding="utf-8"))
        rel = skill_md.parent.relative_to(ROOT / "skills")
        if meta is None:
            problems.append(f"{rel}: SKILL.md missing or unterminated frontmatter")
            continue
        for field in ("name", "description", "version"):
            if not meta.get(field):
                problems.append(f"{rel}: SKILL.md missing `{field}`")
        if meta.get("name") and meta["name"] != skill_md.parent.name:
            problems.append(f"{rel}: name {meta['name']!r} != directory name")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git/" in path.as_posix():
            continue
        if path.name == "validate_export.py":
            continue   # this file defines the patterns it looks for
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT)
        for m in PERSONAL_PATH.finditer(text):
            problems.append(f"{rel}: personal path survived export: {m.group(0)}")
        for pattern in SECRET_SHAPES:
            if pattern.search(text):
                problems.append(f"{rel}: credential-shaped string matching {pattern.pattern}")

    for line in problems:
        print(f"FAIL {line}")
    print(f"\n{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
