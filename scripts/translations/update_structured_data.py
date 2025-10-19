from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_ROOT = ROOT / "languages"
SPLIT_PATTERN = re.compile(r"[,\uFF0C;\uFF1B]+")
INCLUDE_SEARCH_ACTION = False


@dataclass
class UpdateResult:
    language: str
    changed: bool
    reason: List[str]


def iter_language_dirs(base: Path) -> Iterable[Path]:
    if not base.exists():
        return []
    for item in sorted(base.iterdir()):
        if item.is_dir():
            yield item


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def unique_preserve_order(values: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for raw in values:
        item = raw.strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def update_structured_for_language(lang_dir: Path) -> UpdateResult:
    code = lang_dir.name
    locale_path = lang_dir / "locale.json"
    structured_path = lang_dir / "structured.json"

    messages: List[str] = []
    if not locale_path.exists() or not structured_path.exists():
        return UpdateResult(code, False, ["missing locale or structured json"])

    locale_doc = load_json(locale_path)
    structured_doc = load_json(structured_path)

    strings = locale_doc.get("strings", {})
    title = strings.get("meta.title")
    description = strings.get("meta.description")
    keywords = strings.get("meta.keywords")

    if not title or not description or not keywords:
        missing_keys = [key for key, value in (
            ("meta.title", title),
            ("meta.description", description),
            ("meta.keywords", keywords),
        ) if not value]
        messages.append(f"missing metadata: {', '.join(missing_keys)}")
        return UpdateResult(code, False, messages)

    graph = structured_doc.get("@graph")
    if not isinstance(graph, list) or len(graph) < 3:
        messages.append("structured graph missing expected entries")
        return UpdateResult(code, False, messages)

    organisation = graph[0]
    website = graph[1]
    webpage = graph[2]

    changed = False

    for entry in (website, webpage):
        if entry.get("name") != title:
            entry["name"] = title
            changed = True
        if entry.get("description") != description:
            entry["description"] = description
            changed = True
        if entry.get("keywords") != keywords:
            entry["keywords"] = keywords
            changed = True

    keyword_tokens = unique_preserve_order(
        SPLIT_PATTERN.split(keywords)
    )
    if keyword_tokens and webpage.get("aiSemantic") != keyword_tokens:
        webpage["aiSemantic"] = keyword_tokens
        changed = True

    if INCLUDE_SEARCH_ACTION:
        expected_action = {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"https://lucy.world/{code}/?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
        if website.get("potentialAction") != expected_action:
            website["potentialAction"] = expected_action
            changed = True
    elif "potentialAction" in website:
        del website["potentialAction"]
        changed = True

    if changed:
        write_json(structured_path, structured_doc)
        messages.append("updated structured metadata")

    return UpdateResult(code, changed, messages)


def main() -> int:
    results: List[UpdateResult] = []
    for directory in iter_language_dirs(LANGUAGE_ROOT):
        results.append(update_structured_for_language(directory))

    updated = [r.language for r in results if r.changed]
    skipped = [r for r in results if not r.changed]

    for result in results:
        if result.changed or result.reason:
            status = "changed" if result.changed else "skipped"
            detail = f" ({'; '.join(result.reason)})" if result.reason else ""
            print(f"{result.language}: {status}{detail}")

    print(f"Total languages processed: {len(results)}")
    print(f"Languages updated: {len(updated)}")
    print(f"Languages skipped: {len(skipped)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
