#!/usr/bin/env python3
"""Lesson headings in a flat JOURNEY.md. Same shape as scripts/lesson-order."""
import re
from pathlib import Path

HEADING = re.compile(r"^# ([a-z0-9-]+):")


def order_text(text):
    return [match.group(1) for line in text.splitlines() if (match := HEADING.match(line))]


def order_path(path):
    return order_text(Path(path).read_text())


def section(text, lesson):
    lines = text.splitlines()
    prefix = f"# {lesson}:"
    start = next((index for index, line in enumerate(lines) if line.startswith(prefix)), None)
    if start is None:
        return None
    end = next(
        (index for index in range(start + 1, len(lines)) if HEADING.match(lines[index])),
        len(lines),
    )
    return "\n".join(lines[start:end])


def journey_beside_results(results):
    root = Path(results).resolve()
    sibling = root.parent / "JOURNEY.md"
    if sibling.is_file():
        return sibling
    inside = root / "JOURNEY.md"
    if inside.is_file():
        return inside
    return sibling


def journey_beside_material(material):
    return Path(material).resolve().parent / "JOURNEY.md"
