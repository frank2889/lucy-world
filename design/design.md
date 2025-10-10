# Lucy World Design System — Machine-Executable Specification

Version: 1.0.0  
Compliance: Enterprise Light Mode Standard  
Last Evaluated: 2025-10-09

> ⚙️ System Directive  
> `design.md` is the **authoritative specification** for all derived
> files. Any change to JSON, CSS, HTML, TS, shaders, or renderer
> configuration must be **recompiled** from this document. Direct edits
> outside this file are prohibited and void the design license.

> 🛡️ Governance  
> `design.md` holds design supremacy. Any file, module, or subsystem not
> visually derived from this document must be altered, replaced, or
> removed before deployment unless an approved legacy exemption is noted
> below.

> 📋 Delivery Integration  
> The DoD Implementation Plan references this specification as a
> mandatory gate. Before closing any DoD checklist item, teams must run
> `python3 design/compile_design.py`, commit regenerated artefacts, and
> document compliance in the plan.

```css
/* === COLOR TOKENS (LOCKED) === */
--color-bg-base: #F9FAFB;
--color-bg-surface: #FFFFFF;
--color-border-neutral: #D0D0D0;
--color-text-primary: #172B4D;
--color-text-secondary: #44546A;
--color-accent-primary: #007BC1;
--color-accent-hover: #0064A3;
--color-semantic-error: #D32F2F;
--color-semantic-success: #388E3C;
--color-semantic-warning: #FBC02D;
--color-shadow: rgba(0, 0, 0, 0.12);

/* Derived system values */
--color-accent-disabled: color-mix(in srgb, var(--color-accent-primary) 40%, white);
--color-border-hover: color-mix(in srgb, var(--color-border-neutral) 60%, var(--color-accent-primary));
--color-focus-ring: var(--color-accent-primary);
```

All visual components must reference these tokens only.  
Direct HEX or RGB values are prohibited.

This specification defines the Enterprise Light Mode palette.  
Any dark mode conversion must follow luminance inversion mapping:  
base ↔ text-secondary, surface ↔ text-primary, accent-primary ↔ #58C7F2.

## Authority & Derivation

- `design.md` is the single source of truth for every design artefact.
- All downstream assets must be generated from this document on each
  build.
- Manual copies of tokens, colors, motion curves, or spectral
  parameters are forbidden.

### Generation Hierarchy

```text
design.md
│
├──→ tokens.json          # Parsed from Section 0
├──→ variables.css        # Flattened tokens (light + dark)
├──→ theme.ts             # Typed export for engineers
├──→ index.html           # References variables.css only
└──→ renderer.config.json # Spectral + emission map from Section 10
```

- `tokens.json` mirrors Section 0 exactly.
- `variables.css` composes Section 0 with theme overrides.
- `theme.ts` exports typed interfaces for the same keys.
- `renderer.config.json` serializes Section 10 spectral rules.
- No other file may define token values or fallback literals.

### Synchronization Pipeline

```yaml
build_pipeline:
  source: design.md
  steps:
    - extract: ["Design Tokens", "Responsive Scaling Logic", "Spectral Extension"]
    - generate: tokens.json
    - generate: variables.css
    - generate: theme.ts
    - generate: renderer.config.json
  verify:
    - ensure_drift: 0
    - assert_luminance_compliance: true
    - assert_emission_ceiling: 0.22
    - assert_glow_coverage: 0.12
```

The pipeline fails any build where generated artefacts diverge from this
document.

### Enforcement Rules

- Scan all source files for literal colors, motion values, or spacing
  constants. Replace non-token literals with references to exported
  tokens or remove the offending code.
- Reject deployments when a file cannot trace its values to `design.md`.
- If a vendor dependency must remain, document it inside a
  `legacy_exemption` block including file path, rationale, remediation
  plan, and acceptance of risk.

### Legacy Exemption Template

```yaml
legacy_exemption:
  file: "vendor/bootstrap-grid.css"
  reason: "Third-party dependency"
  replacement_plan: "Migrate to Lucy grid system v2 by Q1 2026"
  risk_acceptance: true
```

Files lacking a declared exemption are considered non-compliant.

## 0. Design Tokens (Authoritative Source)

```css
:root {
  /* Color roles */
  --color-bg-canvas: #F8FAFC;
  --color-bg-surface: rgba(255, 255, 255, 0.92);
  --color-border-subtle: rgba(84, 106, 130, 0.10);
  --color-border-strong: rgba(0, 184, 244, 0.25);
  --color-text-primary: #1E2A36;
  --color-text-secondary: #4A637D;
  --color-text-inverse: #E8F6FF;
  --color-accent-primary: #00B8F4;
  --color-accent-glow: #58DFFF;
  --color-accent-pressed: #0092C4;
  --color-warning: #F6B56A;
  --color-success: #54E1B1;
  --color-error: #FF6767;
  --scrim-base: #050B14;
  --scrim-strong: color-mix(in srgb, var(--scrim-base) 80%, transparent);

  /* Typography */
  --font-family-base: "Inter", "Helvetica Neue", sans-serif;
  --font-family-numeric: "Roboto Mono", monospace;
  --font-h1-size: 1.75rem;
  --font-h2-size: 1.5rem;
  --font-h3-size: 1.25rem;
  --font-body-size: 1rem;
  --font-label-size: 0.8125rem;
  --font-numeric-size: 0.875rem;
  --line-height-tight: 1.25;
  --line-height-base: 1.6;

  /* Space & radius */
  --space-unit: 8px;
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  /* Elevation */
  --elevation-0: none;
  --elevation-1: -2px 2px 6px rgba(0, 0, 0, 0.15);
  --elevation-2: -4px 4px 12px rgba(0, 0, 0, 0.22);
  --elevation-3: -6px 6px 18px rgba(0, 0, 0, 0.30);
  --elevation-4: -8px 8px 24px rgba(0, 0, 0, 0.38);

  /* Motion */
  --motion-fast: 100ms;
  --motion-medium: 180ms;
  --motion-slow: 240ms;
  --easing-standard: cubic-bezier(0.2, 0.8, 0.4, 1);
  --easing-emphasis: cubic-bezier(0.4, 0, 0.2, 1);

  /* Glow & focus */
  --focus-ring-color: rgba(88, 223, 255, 0.5);
  --focus-ring-width: 4px;
  --glow-inner-radius: 6px;
}

.theme-dark {
  --color-bg-canvas: #1E2A36;
  --color-bg-surface: rgba(44, 60, 79, 0.92);
  --color-border-subtle: rgba(232, 246, 255, 0.06);
  --color-border-strong: rgba(88, 223, 255, 0.35);
  --color-text-primary: #E8F6FF;
  --color-text-secondary: #A0A6AD;
  --elevation-1: -2px 2px 6px rgba(255, 255, 255, 0.08);
  --elevation-2: -4px 4px 12px rgba(255, 255, 255, 0.12);
  --elevation-3: -6px 6px 18px rgba(255, 255, 255, 0.16);
  --elevation-4: -8px 8px 24px rgba(255, 255, 255, 0.20);
  --focus-ring-color: rgba(88, 223, 255, 0.7);
}
```

All downstream agents MUST derive variables, themes, and code from this token block.

## 0.1 Responsive Scaling Logic

```css
:root { --scale: 1; }

@media (min-width: 1440px) { :root { --scale: 1.05; } }
@media (max-width: 1439px) and (min-width: 1200px) { :root { --scale: 1; } }
@media (max-width: 1199px) and (min-width: 1024px) { :root { --scale: 0.9; } }
@media (max-width: 1023px) and (min-width: 768px) { :root { --scale: 0.8; } }
@media (max-width: 767px) and (min-width: 480px) { :root { --scale: 0.75; } }
@media (max-width: 479px) { :root { --scale: 0.7; } }

* { font-size: calc(var(--font-body-size) * var(--scale)); }
```

Padding, margin, gap, and component dimensions MUST use  
`calc(var(--space-unit) * N * var(--scale))`. Font sizes reference  
the appropriate `--font-*-size` token multiplied by `var(--scale)`.

## 0.2 Visual Fidelity Mode Toggle

Enable the **Atlantis Presence** variant by applying
`data-visual-mode="atlantis"` on the document root. The renderer must
switch palettes atomically; partial overrides are prohibited.

```css
:root[data-visual-mode="atlantis"] {
  --color-bg-surface: rgba(255, 255, 255, 0.94);
  --color-accent-primary: #19B5E8;
  --color-accent-glow: #7AE1FF;
  --color-text-primary: #1E2734;
  --color-border-strong: rgba(25, 181, 232, 0.28);
  --reflection-tint: rgba(108, 124, 142, 0.22);
}

:root.theme-dark[data-visual-mode="atlantis"] {
  --color-bg-surface: rgba(36, 48, 64, 0.94);
  --color-accent-primary: #00B8F4;
  --color-accent-glow: #58DFFF;
  --color-text-primary: #E6F4FF;
}
```

- Maintain `emission ≤ 0.22` and existing pulse rates in all modes.
- The attribute toggle must trigger regeneration of downstream artefacts
  (`variables.css`, `theme.ts`, `renderer.config.json`).
- Agents must fall back to the base palette when the toggle is unset or
  when a `legacy_exemption` explicitly disallows mode switches.

## 🔎 Executive Summary

- The design system is production-ready: it encodes layout, typography,  
  color, motion, light physics, and dark-mode strategy in detail.  
- Core strengths include an 8pt spacing grid, role-based color palette  
  with luminance data, comprehensive component tokens, and explicit  
  lighting + motion rules.  
- Implementation requires disciplined tokenization, responsive breakpoints,  
  and accessibility validation (contrast + reduced-motion).  
- Spectral effects (glow, bloom, vignette) deliver the “cold cyan energy”  
  aesthetic when applied subtly via layered overlays.

## 1. System Strengths

### 1.1 Layout & Spacing
- Fluid 12-column grid at 1920 px base width with 16 px gutters  
  and 32 px margins.  
- Global 8 px baseline grid; spacing increments align to multiples of 8.  
- Elevation ladder (levels 0–4) plus quadratic shadow opacity curve  
  for predictable depth.

### 1.2 Geometry & Lighting Direction
- Corner radius hierarchy: tooltips 4 px, buttons 8 px, cards 12 px,  
  modals 16 px.  
- Global light vector: 25° from the north-east; glow axis at 270° for  
  consistent highlight direction.

### 1.3 Color Architecture
- Role-driven palette with HEX, HSL, and luminance values for backgrounds,  
  text, accents, and states.  
- Primary accent cyan `#00B8F4` with hover glow `#58DFFF`; feedback colors  
  (amber, mint, coral) defined for status messaging.  
- High contrast between surface `Y≈0.94` and primary text `Y≈0.12`; secondary  
  text intentionally lighter—verify on small text.

### 1.4 Typography
- Inter as UI font with defined weights (Semibold H1 28 px, Medium H2 22 px,  
  Regular body 16 px / 1.6 line height).  
- Label style: 13 px uppercase, +0.3 px tracking for compact UI copy.  
- Numeric data style: Roboto Mono 14 px Medium for aligned metrics.

### 1.5 Component Tokens
- **Buttons**: stateful colors, 12×24 px padding, focus halo, elevation  
  shadow.  
- **Cards**: glass surface, subtle border, level‑2 shadow, 24 px padding.  
- **Inputs**: light field, 1 px neutral border → accent border + inner glow  
  on focus.  
- **Data tiles**: secondary-caps labels, bold primary values, cyan inner-glow baseline.

### 1.6 Light, Glow & Motion Physics
- Ambient ratio 0.35 vs diffuse 0.55, specular exponent 24.  
- Focus halo: 12 px outer glow, cyan at 25% opacity.  
- Motion presets: card hover lift (120 ms, custom cubic-bezier), button press  
  (80 ms ease-out), modal fade (160 ms linear), data refresh pulse (2 s loop,  
  scale 0.98↔1.0).

### 1.7 Dark Mode Mapping
- Neutral palette inverted: background `#1E2A36`, surface `#2C3C4F`,  
  text `#E8F6FF`.  
- Accent cyan retained; glow intensity scaled ×1.4.  
- Shadows invert to light glows (e.g., `rgba(255,255,255,0.08)`), keeping  
  depth legible on dark surfaces.

### 1.8 Environmental Effects
- Reflection tint `#6C7C8E @ 0.18` adds subtle glass sheen.  
- Ambient vignette (radial, 0.1 opacity) guides focus toward center.  
- Corner bloom (30° cyan gradient, 64 px radius) and highlight streaks  
  (25°, 3 px, blur 4 px) reinforce the spectral aesthetic when used  
  sparingly.

## 2. Implementation Playbook

### 2.1 Tokenization Strategy
- Encode color, spacing, radius, typography, shadow, and motion values  
  as design tokens (CSS variables, JSON, or style-dictionary).  
- Provide theme overrides for dark mode and contextual variants via  
  token swaps.  
- Pre-compute elevation shadows: offsets + blur scale with level while  
  opacity follows `0.06 × level² + 0.04` (cap at practical max ≈0.6).

### 2.2 Responsive Breakpoints
- Extend the 12-column grid with breakpoint guidance:  
  - ≥1440 px: maintain 12 columns, 16 px gutters, 32 px margins.  
  - 1024–1439 px: compress gutters to 12 px, margins to 24 px.  
  - 768–1023 px: shift to 8-column layout, stack secondary panels.  
  - ≤767 px: single-column flow, 16 px side padding, elevated cards  
    collapse to full width.  
- Document component behavior (e.g., sidebar → drawer, hero grid → single column).

### 2.3 Accessibility Checklist
- Validate contrast ratios (target ≥4.5:1 for body text; adjust secondary  
  text if needed).  
- Provide high-contrast states for status badges and disabled controls.  
- Respect `prefers-reduced-motion`: disable hover lift and refresh pulse,  
  keep essential feedback only.  
- Maintain clear focus outlines on all interactive elements (keyboard +  
  screen reader support).

### 2.4 Motion & Spectral Effects
- Implement animations via reusable utility classes or keyframes tied to  
  tokens.  
- Apply vignette, reflection tint, and corner bloom as layered  
  pseudo-elements so they can be toggled per view.  
- Constrain highlight streaks to transitional moments (e.g., modal entry,  
  data refresh) to avoid cognitive load.  
- Offer configuration flags to disable environmental FX for  
  resource-constrained contexts.

### 2.5 Legacy Surface Adoption (Static CSS)
- All static pages must import `static/css/design-tokens.css`, the  
  compiler-synchronized mirror of `variables.css`.  
- Legacy layouts may define context-specific helpers that **only** derive  
  from canonical tokens. The current approved set lives in  
  `static/css/style.css` and is scoped to the document `:root`:

  ```css
  --legacy-hero-accent;
  --legacy-hero-accent-strong;
  --legacy-hero-shadow;
  --legacy-hero-shadow-strong;
  --legacy-panel-surface;
  --legacy-panel-border;
  --legacy-panel-glass;
  --legacy-panel-glass-soft;
  --legacy-panel-bright;
  --legacy-deep-space;
  --legacy-text-soft;
  --legacy-text-subtle;
  --legacy-text-faint;
  --legacy-divider;
  --legacy-divider-light;
  --legacy-shadow-medium;
  --legacy-shadow-light;
  --legacy-accent-shadow-soft;
  --legacy-accent-shadow-medium;
  --legacy-accent-glow;
  ```

- Each helper is a `color-mix` or shadow composite built from the base  
  palette to accelerate modernization while we retire remaining legacy  
  selectors. New helpers require design review and must be documented  
  here before use.  
- Static artefacts must not introduce literal HEX/RGB values; replace  
  gradients, borders, and shadows with the helpers above or the raw  
  tokens.  
- Run `python3 design/compile_design.py` after edits so the mirrored  
  token file stays in sync for the static toolchain.

## 3. Risk & Quality Gates

- **Contrast**  
  - Risk: secondary text on light backgrounds may fall below 4.5:1.  
  - Mitigation: darken hue or reserve for large text only.  
- **Performance**  
  - Risk: layered glow/vignette effects may tax low-end GPUs.  
  - Mitigation: enable feature flags and progressively enhance.  
- **Motion comfort**  
  - Risk: continuous pulses can distract sensitive users.  
  - Mitigation: honor reduced-motion preferences.  
- **Consistency**  
  - Risk: ad hoc shadows risk diverging from the elevation curve.  
  - Mitigation: generate shadows from the elevation token set.

## 4. Next Steps

1. **Token baseline**: publish light + dark theme tokens to the shared  
  style registry.  
2. **Component audit**: ensure buttons, cards, inputs, data tiles  
  consume tokens only (no hard-coded values).  
3. **Responsive spec**: document view-specific behavior for navigation,  
  hero surfaces, modals.  
4. **Accessibility QA**: run automated contrast checks and manual  
  keyboard testing; adjust tokens as required.  
5. **Spectral FX prototypes**: build small proofs-of-concept for  
  vignette, corner bloom, highlight streaks before widespread use.

## ✅ Conclusion

The Lucy World design system is enterprise-ready. It transforms “cold cyan  
energy” into actionable tokens, motion curves, and light physics that  
engineers can implement with confidence. Once tokenized, responsively  
extended, and accessibility-tested, the system will deliver a distinctive  
yet highly legible product experience across light and dark modes.

## 10. Spectral Extension — AI Execution Rules

These rules layer **energy overlays** on top of the core token system.
They never override base values; instead they let the renderer express
living light, resonant geometry, and calm energy in a controlled way.

### 10.0 Field Origin Instructions

```yaml
# === FIELD ORIGIN PARAMETERS ===
energy_origin:
  # global render space
  coordinate_system: "top-left → bottom-right"
  # energy pulses originate at centroid
  emission_center: "component centroid"
  # lock to the global light vector
  directionality: 25deg NE
  # synchronize emission across components
  phase_alignment: global_time * 0.3hz
```

- All spectral pulses align with `energy_origin.directionality`; avoid
  random or per-component drift.
- Synchronize seam animation phases with `phase_alignment` so interfaces
  breathe in unison.
- Use each component centroid as the anchor for glow radius and
  vignette convergence.

### Light Field Authority

The light field emanates **from logic, not ornamentation**.
Emission intensity, direction, and rhythm must always reflect the
system’s internal state — never user whim or decorative triggers.

- Only active processes, focus, or awareness events may emit light.
- Static surfaces stay passive unless logic signals change.
- Disallow manual overrides that mimic spectral behaviour without
  confirmed system intent.

### 10.1 Energy Logic

```yaml
field_state:
  idle:
    emission: 0.06       # ambient surface hum
    pulse_rate: 0         # static
  focus:
    emission: 0.12        # mild cyan charge
    pulse_rate: 0.3hz     # micro shimmer 1 cycle / 3.3 s
  active:
    emission: 0.18        # energized, edge streaks enabled
    pulse_rate: 0.6hz
  disabled:
    emission: 0.02        # nearly inert
```

The renderer treats `emission` as soft internal glow rather than
additive light. `pulse_rate` applies a ±0.02 luminance shift using a
sinusoidal alpha curve around the base value.

### 10.2 Edge & Seam Illumination

- Draw 1 px cyan seams (`rgba(0, 184, 244, 0.2)`) along card, modal,
  and button borders.
- Animate seams on interaction with a 6 s travelling highlight at 15%
  opacity.
- Keep the light direction locked to the global vector (25° NE).
- Merge overlapping seams additively but clamp combined opacity at 0.3.
- Limit each component to a single active seam animation at a time.

### 10.3 Surface Transparency & Layers

Render panels and cards as two composited layers:

1. `surface_base`: `var(--color-bg-surface)`
2. `surface_overlay`:
   `linear-gradient(180deg, rgba(255, 255, 255, 0.04),
   rgba(0, 184, 244, 0.04))`

Total opacity must stay at or below 0.96 to achieve the translucent
alloy finish without drifting into glass-like transparency.

### 10.4 Geometric Resonance Pattern

Optional resonance grid for large surfaces:

```css
background-image:
  repeating-linear-gradient(
    60deg,
    rgba(0, 184, 244, 0.02) 0,
    rgba(0, 184, 244, 0.02) 2px,
    transparent 2px,
    transparent 16px
  );
background-size: 32px 32px;
```

Apply at ≤3% opacity on secondary panels or dashboards to imply hidden
circuitry without overwhelming content.

### 10.5 Ambient Response Field

- Bloom threshold: 0.72
- Bloom radius: 12 px
- Ambient vignette: radial 15°, 0.08 opacity
- Reflection tint: `#6C7C8E` @ 0.18

Bloom, vignette, and reflection layers follow the pointer centroid with
at most 3 px of parallax to maintain the sense of gentle presence.

### 10.6 Interaction Feedback

- Hover: raise elevation by one level and brighten the edge seam to
  0.25 opacity for 120 ms.
- Press: compress elevation by one level and shrink the cyan halo by
  20%.
- Focus: apply a 12 px halo (`rgba(88, 223, 255, 0.25)`) with a
  200 ms ease-in fade.
- Success/Error: overlay a 0.5 s pulse using mint or coral at 0.18
  opacity.

### 10.7 AI Agent Instructions

- Never add decorative light; interpret all glow and motion as stateful
  feedback.
- Keep emission rhythms calm with frequencies below 1 Hz.
- Limit simultaneous pulses across components to ≤5% probability to
  avoid systemic flicker.
- Treat cyan emission as a marker of knowledge presence. Activate only
  when the system surfaces data, focuses, or communicates awareness.
- Silence equates to confidence; excess motion signals instability.

### 10.8 Verification Targets

Rendering agents must assert the following:

1. Average luminance drift remains within ±0.02 over a 10 s idle
   window.
2. Total active glow covers no more than 12% of the viewport at any
   moment.
3. Pulse frequencies stay at or below 1 Hz.
4. Bloom and vignette layers blend in linear color space before tone
   mapping occurs.

### 10.9 Optional “Portal” Mode

```css
.portal-mode {
  background:
    radial-gradient(
      circle at center,
      rgba(0, 184, 244, 0.25) 0%,
      rgba(0, 184, 244, 0.05) 40%,
      transparent 80%
    );
  animation: swirl 12s linear infinite;
}

@keyframes swirl {
  from { filter: hue-rotate(0deg); }
  to   { filter: hue-rotate(360deg); }
}
```

Use portal mode for immersive sequences such as start-up or loading
experiences. Keep each activation below 5 s and disable by default in
enterprise contexts.

### 10.10 Execution Guidelines

1. Synchronize all pulses via a shared `phase_alignment` derived from
  system time.
2. Quantize luminance and opacity shifts to 0.01 increments to avoid
  fractional noise.
3. Clamp emission values within `[0.00, 0.22]`; higher readings
  indicate instability.
4. Integrate light changes over 200 ms windows to eliminate flicker and
  aliasing.
5. Mute emission whenever the logical subsystem reports idle or
  complete states.

### 🧩 Summary for the AI

1. Render functionally: respect tokens, spacing, elevation, and motion.
2. Layer atmospherically: apply spectral energy overlays without
   inventing new colors.
3. Express energy through emission and transparency, never raw color
   swaps.
4. Behave like a field, not a lamp: light emanates from logic, not onto
   it.

## 5. Component Blueprints (Canonical Reference)

### 5.1 Button


```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: calc(var(--space-unit) * 1.5 * var(--scale))
           calc(var(--space-unit) * 3 * var(--scale));
  border-radius: var(--radius-sm);
  background: var(--color-accent-primary);
  color: #FFFFFF;
  border: none;
  box-shadow: var(--elevation-1);
  transition:
    background var(--motion-fast) var(--easing-standard),
    box-shadow var(--motion-fast) var(--easing-standard),
    transform var(--motion-fast) var(--easing-standard);
  min-height: calc(44px * var(--scale));
}

.btn:hover {
  background: linear-gradient(
    192deg,
    var(--color-accent-primary) 0%,
    var(--color-accent-glow) 100%
  );
}

.btn:active {
  background: var(--color-accent-pressed);
  transform: translateY(1px);
}

.btn:disabled {
  background: rgba(160, 166, 173, 0.4);
  color: rgba(255, 255, 255, 0.6);
  cursor: not-allowed;
  box-shadow: none;
}

.btn[data-focus-visible] {
  box-shadow: 0 0 0 var(--focus-ring-width) var(--focus-ring-color);
}
```

#### Token inheritance — Button

- Background (default): `--color-accent-primary` — solid fill.  
- Background (hover): gradient primary → glow — spectral sheen.  
- Background (active): `--color-accent-pressed` — 10% darker.  
- Border radius: `--radius-sm` across all states.  
- Shadow (default): `--elevation-1`; disabled state removes elevation.  
- Motion: `--motion-fast` with `--easing-standard` on hover and active.

### 5.2 Card

```css
.card {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: calc(var(--space-unit) * 3 * var(--scale));
  box-shadow: var(--elevation-2);
  color: var(--color-text-primary);
}

.card[data-focus-visible] {
  box-shadow:
    0 0 0 var(--focus-ring-width) var(--focus-ring-color),
    var(--elevation-2);
}
```

#### Token inheritance — Card

- Background: `--color-bg-surface` for all states.  
- Border: `--color-border-subtle`, 10% opacity perimeter.  
- Radius: `--radius-md` (12 px).  
- Padding: `calc(space-unit*3*scale)` (24 px base).  
- Shadow: `--elevation-2` at default elevation.

### 5.3 Input Field

```css
.input {
  width: 100%;
  padding: calc(var(--space-unit) * 1.5 * var(--scale))
           calc(var(--space-unit) * 2 * var(--scale));
  border-radius: var(--radius-sm);
  border: 1px solid rgba(160, 166, 173, 0.4);
  background: #F3F9FB;
  color: var(--color-text-primary);
  transition:
    border-color var(--motion-fast) var(--easing-standard),
    box-shadow var(--motion-fast) var(--easing-standard);
  min-height: calc(44px * var(--scale));
}

.input:focus-visible {
  border-color: var(--color-accent-primary);
  box-shadow:
    inset 0 0 var(--glow-inner-radius) rgba(0, 184, 244, 0.2),
    0 0 0 var(--focus-ring-width) var(--focus-ring-color);
}

.input[aria-invalid="true"] { border-color: var(--color-error); }
.input:disabled {
  background: rgba(160, 166, 173, 0.12);
  color: rgba(30, 42, 54, 0.4);
  cursor: not-allowed;
}
```

#### Token inheritance — Input

- Background: `#F3F9FB` for default field.  
- Border (default): `rgba(160, 166, 173, 0.4)` neutral outline.  
- Border (focus): `--color-accent-primary` highlight.  
- Radius: `--radius-sm` (8 px) across states.  
- Padding: `calc(space-unit*1.5*scale)` vertical,  
  `calc(space-unit*2*scale)` horizontal.  
- Shadow: focus ring plus inner glow on `data-focus-visible`.  
- Min height: `calc(44px * var(--scale))` to enforce tap targets.

### 5.4 Modal

```css
.modal {
  width: min(94vw, calc(720px * var(--scale)));
  padding: calc(var(--space-unit) * 4 * var(--scale));
  border-radius: var(--radius-lg);
  background: var(--color-bg-surface);
  box-shadow: var(--elevation-4);
  transition:
    opacity var(--motion-medium) linear,
    transform var(--motion-medium) var(--easing-standard);
}

.modal[aria-busy="true"] {
  opacity: 0.8;
}

.modal-enter {
  opacity: 0;
  transform: translateY(16px);
}

.modal-enter-active {
  opacity: 1;
  transform: translateY(0);
}

.modal-exit-active {
  opacity: 0;
  transform: translateY(16px);
}
```

#### Token inheritance — Modal

- Width: `min(94vw, 720px*scale)` ensures responsive envelope.  
- Padding: `calc(space-unit*4*scale)` (32 px base).  
- Radius: `--radius-lg` (16 px).  
- Shadow: `--elevation-4` for peak elevation.  
- Animation: `--motion-medium` durations for fade-slide transitions.

## 6. Typography Matrix

- H1 — token `--font-h1-size` (1.75 rem, 600 weight, 2.4 line height) for  
  page titles and hero copy.  
- H2 — token `--font-h2-size` (1.5 rem, 600 weight, 2.1 line height) for  
  section headings.  
- H3 — token `--font-h3-size` (1.25 rem, 500 weight, 1.8 line height) for  
  card headers.  
- Body — token `--font-body-size` (1 rem, 400 weight, 1.6 line height) for  
  standard paragraphs.  
- Label — token `--font-label-size` (0.8125 rem, 600 weight, 1.4 line  
  height) for UI labels and buttons.  
- Numeric — token `--font-numeric-size` (0.875 rem, 500 weight, 1.5 line  
  height) for metrics and counters.

All typography MUST respect scaling:  
`calc(var(--font-*-size) * var(--scale))`. Tracking for labels uses  
`letter-spacing: 0.3px`; H1/H2 tracking is `-0.2px`.

## 7. Motion Variables

```css
:root {
  --motion-fast: 100ms;
  --motion-medium: 180ms;
  --motion-slow: 240ms;
  --motion-loop: 2000ms;
  --easing-standard: cubic-bezier(0.2, 0.8, 0.4, 1);
  --easing-emphasis: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-linear: linear;
}

.motion-hover-lift {
  transition: transform var(--motion-fast) var(--easing-standard);
}

.motion-press {
  transition: transform var(--motion-fast) var(--easing-emphasis);
}

.motion-fade {
  transition: opacity var(--motion-medium) var(--easing-linear);
}

.motion-pulse {
  animation:
    pulse var(--motion-loop) var(--easing-standard)
    infinite alternate;
}
```

`@keyframes pulse` MUST scale elements between 0.98 and 1.0.

## 8. Accessibility & Testing Hooks

- Every interactive element MUST expose `[data-focus-visible]` when  
  focus-visible styles are applied.  
- Loading states MUST set `[aria-busy="true"]` and, where applicable,  
  `[data-loading]`.  
- Disabled elements MUST include `[aria-disabled="true"]` in addition to  
  the `disabled` attribute.  
- Tap/click targets MUST achieve `min-width` and `min-height` of  
  `calc(44px * var(--scale))` via `.touch-target`.  
- Validation errors MUST set `[aria-invalid="true"]` and pair with an  
  `aria-describedby` error message.  
- Automated tests should assert token application via  
  `[data-token="<token-name>"]` where generated by build tooling.

## 9. Export Targets

The specification MUST compile to artefacts:

1. `tokens.json` — machine-readable token map mirroring Section 0.  
2. `variables.css` — flattened CSS custom properties for runtime consumption.  
3. `theme.ts` (optional) — typed token export for TypeScript-focused  
  design systems.  

Pipelines should reject builds if token drift is detected between this  
document and generated artefacts.

---
canonical_source: true
build_integrity: required
export_targets:
  - tokens.json
  - variables.css
  - theme.ts
  - renderer.config.json
last_verified: 2025-10-09
checksum: auto-generated-by-pipeline
---
