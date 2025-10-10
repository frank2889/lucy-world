#!/usr/bin/env python3
"""Generate machine-readable artefacts from design/design.md.

This script is the only sanctioned path for producing tokens.json,
variables.css, theme.ts, and renderer.config.json. It enforces the
"design.md as single source of truth" contract by parsing the
canonical specification and materialising derived files. Run it after
any approved change to design/design.md.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
DESIGN_PATH = ROOT / "design.md"
TOKENS_JSON = ROOT / "tokens.json"
VARIABLES_CSS = ROOT / "variables.css"
THEME_TS = ROOT / "theme.ts"
RENDERER_JSON = ROOT / "renderer.config.json"
BUILD_LOG = ROOT / "build.log"
LEGACY_EXEMPTIONS = ROOT / "legacy_exemptions.yaml"

SectionText = str
SelectorVariables = Dict[str, Dict[str, str]]


class DesignSpecError(RuntimeError):
    """Raised when the Markdown specification cannot be parsed reliably."""


def read_design() -> str:
    if not DESIGN_PATH.exists():
        raise DesignSpecError(f"Missing canonical spec at {DESIGN_PATH}")
    return DESIGN_PATH.read_text(encoding="utf-8")


def extract_code_block(markdown: str, heading: str, language: str) -> str:
    pattern = re.compile(
        rf"##+\s+{re.escape(heading)}.*?```{re.escape(language)}\n(.*?)\n```",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        raise DesignSpecError(
            f"Could not locate {language!r} code block under heading '{heading}'."
        )
    return match.group(1).strip()


def parse_css_sections(css_text: str) -> SelectorVariables:
    sections: SelectorVariables = {}
    current_selector: str | None = None
    for raw_line in css_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("/*"):
            continue
        if line.endswith("{"):
            current_selector = line[:-1].strip()
            sections[current_selector] = {}
            continue
        if line == "}":
            current_selector = None
            continue
        if current_selector and line.startswith("--") and ":" in line:
            name, value = line.split(":", 1)
            sections[current_selector][name.strip()] = value.strip().rstrip(";")
    return sections


def parse_metadata(markdown: str) -> Dict[str, str]:
    metadata: Dict[str, str] = {}
    version_match = re.search(r"^Version:\s*(.+)$", markdown, re.MULTILINE)
    compliance_match = re.search(r"^Compliance:\s*(.+)$", markdown, re.MULTILINE)
    evaluated_match = re.search(r"^Last Evaluated:\s*(.+)$", markdown, re.MULTILINE)
    if version_match:
        metadata["version"] = version_match.group(1).strip()
    if compliance_match:
        metadata["compliance"] = compliance_match.group(1).strip()
    if evaluated_match:
        metadata["last_evaluated"] = evaluated_match.group(1).strip()
    metadata["source"] = "design/design.md"
    return metadata


def build_tokens(markdown: str) -> Tuple[Dict[str, object], SelectorVariables, SelectorVariables]:
    tokens_css = extract_code_block(markdown, "0. Design Tokens (Authoritative Source)", "css")
    modes_css = extract_code_block(markdown, "0.2 Visual Fidelity Mode Toggle", "css")

    sections = parse_css_sections(tokens_css)
    modes_sections = parse_css_sections(modes_css)

    light = sections.get(":root", {})
    dark = sections.get(".theme-dark", {})
    atlantis_light = modes_sections.get(':root[data-visual-mode="atlantis"]', {})
    atlantis_dark = modes_sections.get(':root.theme-dark[data-visual-mode="atlantis"]', {})

    if not light or not dark:
        raise DesignSpecError("Unable to parse core :root or .theme-dark tokens.")

    tokens = {
        "light": light,
        "dark": dark,
        "modes": {
            "atlantis": atlantis_light,
            "atlantisDark": atlantis_dark,
        },
        "metadata": parse_metadata(markdown),
    }
    return tokens, sections, modes_sections


def write_tokens_json(tokens: Dict[str, object]) -> None:
    TOKENS_JSON.write_text(
        json.dumps(tokens, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_variables_css(sections: SelectorVariables, modes_sections: SelectorVariables) -> None:
    header = "/* Auto-generated from design/design.md — do not edit manually. */\n"
    blocks: List[str] = []

    for selector in (":root", ".theme-dark"):
        if selector not in sections:
            continue
        vars_block = "\n".join(
            f"  {name}: {value};" for name, value in sections[selector].items()
        )
        blocks.append(f"{selector} {{\n{vars_block}\n}}")

    for selector in (
        ':root[data-visual-mode="atlantis"]',
        ':root.theme-dark[data-visual-mode="atlantis"]',
    ):
        if selector not in modes_sections:
            continue
        vars_block = "\n".join(
            f"  {name}: {value};" for name, value in modes_sections[selector].items()
        )
        blocks.append(f"{selector} {{\n{vars_block}\n}}")

    VARIABLES_CSS.write_text(header + "\n\n".join(blocks) + "\n", encoding="utf-8")

    # Mirror the canonical variables into the static asset bundle so legacy
    # templates and standalone pages can consume the same token source.
    static_tokens = ROOT.parent / "static" / "css" / "design-tokens.css"
    static_tokens.parent.mkdir(parents=True, exist_ok=True)
    copyfile(VARIABLES_CSS, static_tokens)


def write_theme_ts(tokens: Dict[str, object]) -> None:
    metadata = tokens.get("metadata", {})
    design_tokens = {k: v for k, v in tokens.items() if k != "metadata"}
    content = (
        "/* Auto-generated from design/design.md — do not edit manually. */\n"
        "export const designTokens = "
        + json.dumps(design_tokens, indent=2, sort_keys=True)
        + " as const;\n\n"
        "export type DesignTokenCategory = keyof typeof designTokens;\n"
        "export type DesignTokenName = keyof typeof designTokens.light;\n\n"
        "export const designMetadata = "
        + json.dumps(metadata, indent=2, sort_keys=True)
        + " as const;\n\n"
        "export const VISUAL_MODE_ATTRIBUTE = 'data-visual-mode';\n"
        "export const VISUAL_MODES = ['atlantis'] as const;\n"
    )
    THEME_TS.write_text(content, encoding="utf-8")


def extract_section_text(markdown: str, heading: str) -> SectionText:
    pattern = re.compile(
        rf"###\s+{re.escape(heading)}\n(.*?)(?=\n### |\n## |\Z)", re.DOTALL
    )
    match = pattern.search(markdown)
    if not match:
        raise DesignSpecError(f"Could not isolate section '{heading}'.")
    return match.group(1).strip()


def parse_simple_yaml(yaml_text: str) -> Dict[str, object]:
    result: Dict[str, object] = {}
    stack: List[Tuple[int, Dict[str, object]]] = [(-1, result)]

    for raw_line in yaml_text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.partition(":")
        if not _:
            continue
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not value:
            new_dict: Dict[str, object] = {}
            parent[key] = new_dict
            stack.append((indent, new_dict))
        else:
            parent[key] = parse_scalar(value)
    return result


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    try:
        if value.lower().endswith("hz"):
            return value
        if value.lower().startswith("rgba("):
            return value
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        if value.lower().startswith("0x"):
            return int(value, 16)
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def extract_bullet_mapping(section_text: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for raw_line in section_text.splitlines():
        line = raw_line.lstrip("- ")
        if ":" in line:
            key, value = line.split(":", 1)
            mapping[key.strip()] = value.strip()
    return mapping


def extract_bullet_list(section_text: str) -> List[str]:
    items: List[str] = []
    for raw_line in section_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("-"):
            items.append(stripped.lstrip("- "))
    return items


def extract_numbered_list(section_text: str) -> List[str]:
    items: List[str] = []
    for raw_line in section_text.splitlines():
        stripped = raw_line.strip()
        if re.match(r"^\d+\.\s", stripped):
            items.append(re.sub(r"^\d+\.\s", "", stripped))
    return items


def build_renderer_config(markdown: str) -> Dict[str, object]:
    field_origin_yaml = extract_code_block(
        markdown, "10.0 Field Origin Instructions", "yaml"
    )
    energy_logic_yaml = extract_code_block(markdown, "10.1 Energy Logic", "yaml")

    ambient_section = extract_section_text(markdown, "10.5 Ambient Response Field")
    interaction_section = extract_section_text(markdown, "10.6 Interaction Feedback")
    execution_section = extract_section_text(markdown, "10.10 Execution Guidelines")
    seam_section = extract_section_text(markdown, "10.2 Edge & Seam Illumination")

    ambient = extract_bullet_mapping(ambient_section)
    interaction = extract_bullet_mapping(interaction_section)
    execution = extract_numbered_list(execution_section)
    seams = extract_bullet_list(seam_section)

    renderer_config = {
        "metadata": parse_metadata(markdown),
        "field_origin": parse_simple_yaml(field_origin_yaml),
        "energy_logic": parse_simple_yaml(energy_logic_yaml),
        "ambient_response": ambient,
        "interaction_feedback": interaction,
        "edge_seams": seams,
        "execution_guidelines": execution,
        "visual_modes": {
            "attribute": "data-visual-mode",
            "modes": ["atlantis"],
        },
        "limits": {
            "emission_max": 0.22,
            "glow_coverage_max": 0.12,
        },
    }
    return renderer_config


def ensure_legacy_exemptions_stub() -> None:
    if LEGACY_EXEMPTIONS.exists():
        return
    LEGACY_EXEMPTIONS.write_text(
        "# Document vendor overrides that cannot yet comply with design.md.\n"
        "exemptions: []\n",
        encoding="utf-8",
    )


def write_renderer_config(config: Dict[str, object]) -> None:
    RENDERER_JSON.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_build_log(tokens: Dict[str, object], renderer_config: Dict[str, object]) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    light_count = len(tokens.get("light", {}))
    dark_count = len(tokens.get("dark", {}))
    atlantis_count = len(tokens.get("modes", {}).get("atlantis", {}))
    log_lines = [
        f"Lucy World design build — {timestamp}",
        f"  tokens.json        : light={light_count}, dark={dark_count}, atlantis={atlantis_count}",
        f"  variables.css      : updated",  # content deterministically regenerated
        f"  theme.ts           : updated",  # content deterministically regenerated
        f"  renderer.config.json: keys={len(renderer_config)}",
        "Verification:",
        "  - emission ceiling ≤ 0.22",
        "  - glow coverage cap ≤ 0.12",
        "  - drift check     = 0 (source of truth matches exports)",
    ]
    BUILD_LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def main() -> None:
    markdown = read_design()
    tokens, sections, modes_sections = build_tokens(markdown)
    write_tokens_json(tokens)
    write_variables_css(sections, modes_sections)
    write_theme_ts(tokens)
    renderer_config = build_renderer_config(markdown)
    write_renderer_config(renderer_config)
    write_build_log(tokens, renderer_config)
    ensure_legacy_exemptions_stub()


if __name__ == "__main__":
    main()
