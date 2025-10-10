# Design Specification Relocated

The canonical Lucy World design system specification now lives at
`design/design.md`.

- Treat the `design/design.md` file as the **single source of truth** for
  all design tokens, variables, spectral rules, and governance directives.
- Regenerate derived artefacts by running
  `python3 design/compile_design.py` from the repo root. This rebuilds
  `tokens.json`, `variables.css`, `theme.ts`, and `renderer.config.json`
  alongside supporting logs.
- Avoid editing generated artefacts directly; update `design/design.md`
  and recompile instead.

This pointer remains to honor historical links. Update any remaining
references to use the `design/` location directly.
