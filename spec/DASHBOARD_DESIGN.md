# Dimplex WPM — Dashboard Design

> **Status: DESIGN.** Companion to `DESIGN.md` (architecture, device tree §5/§5.0,
> source matrix §6, capabilities §4.1) and `spec/REGISTERS.md` (canonical
> registers/entities). This document specifies the Home Assistant front-end:
> importable Lovelace dashboards now, an optional custom card later.
>
> Scope: integration domain `dimplex_wpm`. Entity-id convention (derived from
> `has_entity_name = True`, `unique_id = {entry_id}_{module}_{key}`) used
> throughout this doc:
>
> ```
> sensor.dimplex_wpm_<module>_<key>            # e.g. sensor.dimplex_wpm_hc1_flow_temperature
> binary_sensor.dimplex_wpm_<module>_<key>
> number.dimplex_wpm_<module>_<key>
> select.dimplex_wpm_<module>_<key>
> climate.dimplex_wpm_<module>_<key>
> ```
>
> Modules: `controller`, `hc1`, `hc2_3`, `dhw`, `pool`, `vent`, `solar`,
> `source`, `sg` (smart grid / EMS), `analytics`. These are placeholders — the
> implementation team owns the final slugs, but the patterns below are
> entity-id-agnostic and degrade cleanly if a slug changes.

---

## 1. Overall approach

### Recommendation: **ship importable YAML dashboards first (v1); defer the custom Lovelace card to v2 (and only if a concrete gap survives).**

**Order:**
1. **v1 — four-to-five importable YAML dashboards** built almost entirely on
   **built-in cards** plus a thin, *optional* dependency on `mushroom` (chips
   for compact status) and `apexcharts-card` (the energy/COP plots that
   built-in `history-graph` cannot do well). These are by far the two most
   widely installed HACS frontend cards in 2025/2026, so the "optional
   dependency" cost to users is low. We also provide a **built-in-only
   fallback** for every view so the dashboards render even with zero HACS
   frontend installs.
2. **v2 — *only if needed* — a custom Lovelace card** in a **separate HACS
   "frontend" repo** (the backend integration must not register cards; this is
   HA convention and a hard requirement for HACS/core acceptance). This is the
   `M4` milestone in `DESIGN.md §12` and stays optional.

### Why YAML-first, against 2025/2026 HA practice

- **Sections view is the modern default.** Since the 2024.x → 2025.x cycle,
  the **sections** view type (drag-resizable grid, `grid_options`,
  `column_span`, conditional visibility per card) is the standard layout
  engine. It gives responsive, masonry-free layouts that previously *required*
  a custom layout card (`layout-card`). We build every multi-card view as
  `type: sections`. This removes the historical reason to reach for custom
  layout cards.
- **Built-in cards got good.** `tile` (with features: `target-temperature`,
  `toggle`, state-content lines), `gauge` (with severity bands),
  `history-graph`, `statistics-graph` (long-term stats, hourly/daily/monthly),
  `entities`, `conditional`, `markdown`, `entity` badges, and the native
  `energy-*` cards cover ~90% of what a heat-pump dashboard needs without any
  HACS dependency.
- **The two genuine gaps** that built-ins still don't cover well:
  1. **Multi-series power/heat plots with mixed units and a secondary axis**
     (e.g. COP on a right axis against thermal kW on the left, stacked
     compressor/heater/defrost areas). `history-graph` cannot do dual axes,
     stacking, or per-series styling. **`custom:apexcharts-card`** is the
     de-facto standard here and is the single most valuable optional card.
  2. **Dense, glanceable status at the top of Overview.** `custom:mushroom-*`
     (chips, template cards, climate card) gives a noticeably nicer compact
     status row than `entities`/`tile`, but built-in `tile` + badges are an
     acceptable fallback.

### What a *custom card* would add vs built-ins — and the v1 verdict

A bespoke `dimplex-wpm-card` could deliver, in one widget:

- A **hydraulic schematic** (animated flow arrows source → compressor →
  buffer → HC/DHW, live ΔT, live estimated flow) — genuinely impossible with
  built-ins.
- **First-class measured-vs-estimated rendering** — a badge baked into every
  value that reads the entity's `source` attribute, instead of us hand-wiring
  conditional cards (see §3).
- **Auto-discovery of present modules** from the device tree, so the card
  configures itself instead of the user hand-editing YAML when DHW/Pool/Solar
  appear.

**Verdict for v1: not worth it.** The schematic is delightful but cosmetic;
everything functional (status, control, energy, calibration, measured-vs-
estimated signalling) is achievable today with sections + built-ins +
apexcharts. A custom card is a *frontend repo to maintain, version against HA
breaking changes, and submit to HACS separately* — real ongoing cost for a
solo/small project whose differentiator (per `DESIGN.md §1`) is the
**estimation engine**, not pixels. Build the card in v2 if and only if user
feedback shows the schematic / auto-config gap is real. Until then, the
auto-config win is better spent on **generating** the YAML dashboards from the
active capability set at setup time (a small backend nicety) than on a
runtime card.

---

## 2. Dashboard set

Five views. All are `type: sections` unless noted. Each view degrades by
**capability** and **module presence** via `conditional`/per-card visibility
(§3). Names map to `DESIGN.md §9 Etap 1` (Overview/Status, Energy & Heat,
History, Calibration/Parameters) plus a dedicated **Control** view because
control entities only exist behind the `enable_control` gate and deserve
isolation from read-only daily use.

| # | View | Path | Audience | Built-in-only? |
|---|------|------|----------|----------------|
| 1 | Overview / Status | `overview` | daily glance | yes (mushroom optional) |
| 2 | Heat & Energy | `energy` | the differentiator | apexcharts recommended |
| 3 | Temperatures / History | `history` | trends | yes (statistics-graph) |
| 4 | Control | `control` | gated, expert | yes |
| 5 | Calibration / Diagnostics | `diagnostics` | setup & tuning | yes |

---

### View 1 — Overview / Status

Goal: "is the pump OK, what is it doing right now, key temps." This is the
modern replacement for existing **dashboard 1**, reorganised around the device
tree and with measured-vs-estimated made explicit.

**Top: heading + status chips (mushroom optional, badges fallback).**

- **Card: heading** — `type: heading`, `heading: Dimplex WPM`, icon
  `mdi:heat-pump`. Optional `badges:` row bound to
  `sensor.dimplex_wpm_controller_status_text`,
  `binary_sensor.dimplex_wpm_controller_fault_active`,
  `binary_sensor.dimplex_wpm_controller_lock_active`.
- **Card: chips** — `custom:mushroom-chips-card` with one chip per:
  current status (`controller_status_text`), outdoor temp, active power
  (`analytics_total_power` — shows estimated badge per §3), DHW temp, SG Ready
  mode. *Fallback:* a `glance` card with the same entities. Why: glanceable
  "everything fine" read without scrolling.

**Section: Heat pump now.** (`type: grid`)

- **Card: tile × N** — one `tile` per primary live value:
  `controller_outdoor_temperature`, `hc1_flow_temperature`,
  `hc1_return_temperature`, `dhw_temperature`,
  `analytics_cop_en14511` (with source badge), `analytics_total_power`.
  Why `tile`: large, tap-to-more-info, state-coloured, plays well in the
  sections grid; replaces the cramped `entities` list from dashboard 1.
- **Card: gauge** — `analytics_cop_en14511`, `min: 0 max: 6`, severity green
  ≥3.5 / amber 2–3.5 / red <2. COP is the headline KPI of this integration;
  a gauge sells it.

**Section: Operating state.** (`type: grid`)

- **Card: entities** — the status block: `controller_status_text` (with
  `secondary_info: last-changed`), `controller_lock_text`,
  `controller_fault_text`, `controller_sensor_error_text`,
  `binary_sensor.dimplex_wpm_controller_lock_active`,
  `binary_sensor.dimplex_wpm_controller_fault_active`,
  `binary_sensor.dimplex_wpm_source_2nd_heat_generator` (E10 output, the
  "expensive backup heat is running" signal users care about — carried over
  from dashboard 1), `controller_runtime_2nd_heat_generator`.
- **Card: conditional → entities (Smart Grid)** — visible only when the `sg`
  module exists. `sg_ready_mode_text`,
  `binary_sensor.dimplex_wpm_sg_smartgrid_input_1`,
  `binary_sensor.dimplex_wpm_sg_smartgrid_input_2`,
  `binary_sensor.dimplex_wpm_sg_utility_lockout`. Replaces dashboard 1's SG
  block; the legacy `input_select.sg_ready_mode` helper is gone — control
  moves to View 4.

**Section: Module tiles (each conditional on its module).** (`type: grid`)
One small `conditional` → `entities`/`tile` group per present module:

- **HC2/3** (cond. module `hc2_3`): `hc2_3_hc2_temperature`,
  `hc2_3_hc3_temperature`, setpoints.
- **Pool** (cond. module `pool`): `pool_setpoint`, pool pump output.
- **Ventilation** (cond. module `vent`): supply/extract/exhaust temps, fan
  speeds, level.
- **Solar** (cond. module `solar`): `solar_collector_temperature`,
  `solar_tank_temperature`.
- **Source** (cond. module `source`): `source_inlet_temperature`,
  `source_outlet_temperature`.

---

### View 2 — Heat & Energy  *(the differentiator — measured-vs-estimated front and centre)*

Goal: show power, heat, COP, flow, and energy — and **never let the user
confuse an estimate for a meter reading.** Modernises **dashboard 2**.

This view is where `custom:apexcharts-card` earns its keep. We provide an
apexcharts layout and a `history-graph` fallback section.

**Section: Live power & heat balance.** (`type: grid`)

- **Card: apexcharts (stacked area)** — instantaneous **thermal** balance:
  `analytics_thermal_power_compressor`,
  `analytics_thermal_power_heater`,
  `analytics_thermal_power_defrost_loss` (negative),
  with `analytics_thermal_power_loop` as a line overlay. Stacked area shows
  the heat decomposition the estimation engine produces — impossible in
  `history-graph`. *Fallback:* `history-graph` of the same five series (the
  exact set in dashboard 2).
- **Card: apexcharts (dual axis)** — left axis kW
  (`analytics_total_power`, `analytics_thermal_power_loop`), right axis COP
  (`analytics_cop_en14511`). The COP-vs-power relationship is the core story
  and needs two axes.

**Section: House / installation split.** (cond. capability; `type: grid`)

- **Card: apexcharts (stacked)** — `analytics_thermal_power_to_house` vs
  `analytics_thermal_power_to_installation`. The α-split heuristic
  (`DESIGN.md §6.1 step 6`) is a headline estimation feature; give it a home.

**Section: Flow.** (`type: grid`)

- **Card: apexcharts / history-graph** — `analytics_estimated_flow`,
  `analytics_estimated_flow_smoothed`, `analytics_delta_t`, and — *only when
  `has_flow_sensor`* — the external measured flow entity
  (`capabilities.flow_sensor_entity`). When the real sensor is present, it is
  plotted as a **bold solid** line and the estimate as **dashed**, with a note
  card: "Solid = measured flow sensor; dashed = hydraulic estimate." This is
  the cross-check dashboard 2 hinted at with the `aquaro_*` entity.

**Section: Energy (today / total).** (`type: grid`)

- **Card: statistics-graph** — `period: day`, `stat_types: [change]`,
  bar chart of `analytics_energy_total_kwh` (electric) and
  `analytics_energy_to_house_kwh` (thermal). Long-term-stats native card; no
  HACS needed.
- **Card: entities** — totals row: electric `energy_*_kwh`, thermal
  `energy_*_kwh`, each carrying its `source` badge (§3). Where a heat meter
  exists, the **measured** energy entity is shown; where not, the **estimated**
  one — they are *different entities*, never the same entity flipping source.
- **Card: markdown (link)** — "Configure these in Settings → Energy
  Dashboard" with the entity list (§4).

> **Measured-vs-estimated discipline on this view:** every estimated series
> uses a consistent visual language — name suffix " (est.)", a
> `mdi:calculator-variant` badge, and (apexcharts) a dashed/lighter stroke.
> Measured series get `mdi:gauge` and a solid stroke. See §3 for the
> mechanics.

---

### View 3 — Temperatures / History

Goal: trends over hours/days/weeks. Modernises **dashboard 3** but splits the
one giant 26-entity `history-graph` into purposeful, readable graphs and adds
**long-term** statistics (the old view only had 24h live history).

**Section: Temperatures (24 h live).** (`type: grid`)

- **Card: history-graph** `hours_to_show: 24` — temperature cluster only:
  `controller_outdoor_temperature`, `hc1_flow_temperature`,
  `hc1_return_temperature`, `hc1_return_setpoint`, `dhw_temperature`,
  `dhw_setpoint`. (Plus conditional HC2/3, Source temps when present.)

**Section: Activity (24 h live).** (`type: grid`)

- **Card: history-graph** `hours_to_show: 24` — the binary/state cluster:
  `controller_status_text`, `controller_inverter_frequency`,
  `binary_sensor.dimplex_wpm_source_compressor_1`,
  `binary_sensor.dimplex_wpm_hc1_heating_pump_m13`,
  `binary_sensor.dimplex_wpm_dhw_pump`,
  `binary_sensor.dimplex_wpm_source_2nd_heat_generator`. Separating temps from
  on/off states fixes dashboard 3's unreadable mixed graph.

**Section: Long-term trends.** (`type: grid`)

- **Card: statistics-graph** `period: day`, `days_to_show: 30` — daily mean
  COP, daily energy, daily mean outdoor temp. Uses HA long-term statistics —
  the genuinely new capability this redesign should expose.

---

### View 4 — Control  *(gated: only render behind `enable_control`)*

Goal: isolate every *write* in one clearly-labelled place, with a prominent
warning, so daily users never fat-finger a setpoint. The entire view is
wrapped so it shows nothing useful unless control entities exist.

Because control entities are simply **absent** when `enable_control` is off,
the cleanest gate is: each control card is a `conditional` keyed on the
existence/availability of a representative control entity (e.g.
`number.dimplex_wpm_dhw_setpoint`). When absent, an `entity_filter`/conditional
shows instead a `markdown` notice: "Control is disabled. Enable *Advanced
control* in the integration's options to expose setpoints."

**Section: Warning.** (`type: grid`)

- **Card: markdown** — "These controls write directly to the heat-pump
  controller. Values are range-validated, but changes affect a live system."

**Section: Climate (cond. `enable_climate`).** (`type: grid`)

- **Card: thermostat** (built-in) — `climate.dimplex_wpm_hc1` and
  `climate.dimplex_wpm_dhw`. Built-in thermostat card; no HACS dependency.
  *Optional:* `custom:mushroom-climate-card` for a denser look.

**Section: Heating circuit 1 setpoints (cond.).** (`type: grid`)

- **Card: entities** — `number.dimplex_wpm_hc1_curve_offset` (enum-decoded
  −19..+19 K), `number.dimplex_wpm_hc1_fixed_flow`,
  `number.dimplex_wpm_hc1_curve_end`, `number.dimplex_wpm_hc1_hysteresis`.

**Section: DHW & Pool setpoints (each cond. on module).** (`type: grid`)

- **Card: tile (with target-temperature feature)** —
  `number.dimplex_wpm_dhw_setpoint`, `number.dimplex_wpm_pool_setpoint`.
  `tile` + a number feature gives a clean slider.

**Section: Smart Grid (cond. `enable_sg_ready` + `sg` module).** (`type: grid`)

- **Card: entities** — `select.dimplex_wpm_sg_ready_mode`
  (Hardware/Yellow/Green/Red/Deep-Green), with the read-back
  `sensor.dimplex_wpm_sg_ready_mode_text` beside it. This replaces the legacy
  `input_select.sg_ready_mode` helper from dashboard 1 with the integration's
  native `select`.

---

### View 5 — Calibration / Diagnostics

Goal: tuning of the estimation engine (always available — these `number`s
write to HA options, not the pump, per `DESIGN.md §5.0/§5.3a`) plus raw
diagnostics. Modernises **dashboard 4** (which mixed `input_number` helpers).

**Section: Estimation calibration.** (`type: grid`)

- **Card: entities** — the Config-category `number`s (all native now, no more
  `input_number` helpers): `number.dimplex_wpm_analytics_k_dhw`,
  `analytics_k_defrost`, `analytics_k_defrost_loss`,
  `analytics_heater_2nd_power_w`, `analytics_pump_main_power_w`,
  `analytics_pump_floor_power_w`, `analytics_alpha_base`,
  `analytics_alpha_sensitivity`, `analytics_alpha_deadband`. Group with a
  `header:` and a `markdown` explaining each knob (carries the intent of
  dashboard 4 but with proper labels).

**Section: Live estimation cross-check.** (`type: grid`)

- **Card: entities/glance** — for tuning, show the inputs and outputs
  side-by-side: `controller_inverter_frequency`,
  `analytics_compressor_power_est`, `analytics_cop_en14511`,
  `analytics_delta_t`, `analytics_estimated_flow`. Plus, when meters exist,
  the measured counterparts so the user can calibrate against ground truth.

**Section: Controller diagnostics.** (`type: grid`)

- **Card: entities** — `controller_info` (host/port/unit/firmware/profile in
  attributes), software version, raw `status_code`/`lock_code`/`fault_code`/
  `sensor_error_code` (the numeric diagnostics), all `runtime_*`.
- **Card: entities (outputs)** — collapsible list of the coil
  `binary_sensor`s (compressor 1/2, pumps M13/M14/M15/M20, mixers, DHW/pool/
  solar pumps, general fault). These are `EntityCategory.DIAGNOSTIC`, kept off
  the daily views.

---

## 3. Measured vs estimated UX

This is the dashboard's most important contract: a value the user reads must
be unmistakably tagged as **meter-measured** or **engine-estimated**. The
integration gives us two hooks (`DESIGN.md §5.0, §6`):

1. A `source: measured | estimated` **attribute** on every
   power/heat/flow/COP/energy entity.
2. **Capabilities** (`has_electric_meter`, `has_heat_meter`,
   `has_flow_sensor`, `has_inverter_freq`) that gate which entities even exist.

### Strategy: gate by capability, label by attribute

Two complementary mechanics:

**(a) Separate entities, gated by capability (preferred for energy/power).**
Where the integration creates a *different entity* for measured vs estimated
(e.g. `analytics_energy_total_kwh_measured` exists only with `has_heat_meter`,
else `analytics_energy_total_kwh_estimated` exists), the dashboard uses a
`conditional` card keyed on entity existence/availability. Result: the
Energy view shows the *measured* card on metered installs and the *estimated*
card otherwise — the user never sees both for the same quantity, and there is
no ambiguity. This is the cleanest pattern and matches `DESIGN.md §6`
("encje measured/estimated … brak sprzętu → encje estimated").

> If the implementation instead exposes **one** entity per quantity whose
> `source` attribute flips, use pattern (b) for the badge and a
> `state_attr(...,'source')`-templated note instead of conditional existence.

**(b) Per-value badge by `source` attribute (always-on labelling).**
Regardless of (a), every estimated value carries a visible marker so it reads
correctly even out of context:

- **Name suffix** " (est.)" / " (meter)" on the card config.
- **Icon badge:** estimated → `mdi:calculator-variant`; measured →
  `mdi:gauge`. On `tile`/`entities`, drive this with a `card_mod`-free,
  template-free approach where possible: set static `icon`/`name` per card
  because we already *know* the source from the capability gate. Where the
  source can change at runtime, use a `custom:template-entity-row` (from
  `lovelace-card-mod`'s sibling `template-entity-row`) or a small
  `markdown`/`template` card reading
  `{{ state_attr('sensor.dimplex_wpm_analytics_cop_en14511','source') }}`.
- **Chart stroke (apexcharts):** measured = solid, estimated = dashed +
  lighter opacity, set per-series. This makes the measured-vs-estimated split
  legible at a glance on View 2's flow cross-check.
- **A standing legend `markdown` card** at the top of View 2:
  *"`mdi:gauge` = from a physical meter · `mdi:calculator-variant` =
  estimated by the analytics engine (no meter installed)."*

### Adapting to absent modules / capabilities

Every module-specific card is wrapped in a **`conditional`** (sections view
also supports per-card `visibility:` conditions, which is preferred in
2025/2026 over the older `conditional` card type):

```yaml
visibility:
  - condition: state          # card hidden when entity is unavailable/absent
    entity: sensor.dimplex_wpm_pool_setpoint
    state_not: unavailable
```

- **No DHW/Pool/Solar/Vent/Source module** → those entities are never created;
  their cards' visibility condition fails → cards vanish. No broken "entity not
  found" tiles.
- **No electric meter (`has_electric_meter = false`)** → measured power/energy
  cards hidden; estimated cards shown; legend says "estimated".
- **No flow sensor** → the measured-flow series and its note are dropped from
  View 2's flow card; only the estimate remains.
- **No `enable_control`** → entire View 4 collapses to its "control disabled"
  notice (control entities don't exist to satisfy the gate).
- **No inverter freq (`has_inverter_freq = false`) and no electric meter** →
  power estimate degrades (per `DESIGN.md §6`); the COP gauge and power charts
  show a low-confidence note via a `markdown` conditional on
  `source == 'estimated'` *and* a `confidence` attribute if exposed.

Because all gating is condition-based, **one shipped YAML works across every
install**; nothing needs hand-editing as hardware/modules differ. (A future
backend nicety: generate the YAML pre-trimmed to the active capability set —
see §1 verdict — but the conditional approach means we don't *depend* on it.)

---

## 4. Energy Dashboard integration

The integration exposes native kWh sensors (`device_class: energy`,
`state_class: total_increasing`, `RestoreSensor`) precisely so they drop into
HA's native Energy Dashboard with zero helpers (`DESIGN.md §8`). The dashboard
docs/onboarding should direct users to **Settings → Dashboards → Energy** and
register:

**Grid / consumption (Individual devices, or "Grid consumption" if it's the
pump's whole feed):**

- `sensor.dimplex_wpm_analytics_energy_total_kwh` — total electrical energy
  (measured if `has_electric_meter`, else estimated). **Primary entity to add.**
- Optionally the breakdown as **Individual devices**:
  `analytics_energy_compressor_kwh`, `analytics_energy_heater_kwh`.

**Important guidance text (ship in README / view-2 markdown):**

> Add **one** electrical-energy entity to avoid double counting: either the
> total (`…_energy_total_kwh`) **or** the compressor + heater breakdown — not
> both. The total is the safe default.
>
> The **thermal** energy sensors (`…_energy_to_house_kwh`,
> `…_energy_to_installation_kwh`, measured `5096–5129` heat-meter sums where a
> heat meter exists) are **heat delivered, not electricity consumed** — do
> **not** add them as grid consumption. They are useful in the *Energy*
> dashboard only as context; prefer viewing them on the integration's Heat &
> Energy view (View 2). If you want a COP/SPF-style ratio in Energy, that is
> out of scope for the native Energy Dashboard — use View 2's COP chart.
>
> If you prefer custom billing cycles, the optional documented helpers
> (`utility_meter` on `…_energy_total_kwh`) give monthly/peak-offpeak buckets
> without us re-implementing calendar cycles (`DESIGN.md §8`).

When `has_electric_meter` is true the registered total is the **meter
integral** (`5170`); when false it is the **estimate integral** — but the
entity id, `device_class`, and `state_class` are identical, so the Energy
Dashboard behaves the same either way (`DESIGN.md §8`). The `source` attribute
lets View 2 still badge it.

---

## 5. Dependencies

| Card | Source | v1 status | Used for | Built-in fallback |
|------|--------|-----------|----------|-------------------|
| (core) sections, tile, gauge, entities, history-graph, statistics-graph, thermostat, conditional, markdown, energy-* | **HA built-in** | **required (already present)** | everything structural + control + LTS | — |
| `apexcharts-card` | HACS (`RomRider/apexcharts-card`) | **recommended, optional** | View 2 multi-series / dual-axis / stacked / dashed-vs-solid | `history-graph` (provided) |
| `mushroom` | HACS (`piitaya/lovelace-mushroom`) | **optional, cosmetic** | Overview chips, denser climate | `glance` / `tile` (provided) |
| `template-entity-row` *(or card-mod)* | HACS | **optional** | runtime `source`-attribute badge when source can flip | static per-card naming (provided) |

Principles:
- **Built-in first.** Every view renders with **zero HACS frontend installs**;
  we ship both an apexcharts section and a history-graph section and let users
  delete the one they don't want.
- **Only two cards are worth recommending:** `apexcharts-card` (real
  functional gap) and `mushroom` (polish). Both are top-tier-popularity, so
  the install ask is light.
- **No custom backend-registered resources** — the integration ships YAML
  files under `dashboards/` for manual/UI import (`DESIGN.md §9`), not
  auto-registered cards. The v2 custom card, if built, lives in a **separate
  HACS frontend repo**.

---

## 6. Concrete YAML sketches

Placeholder entity ids per the convention in the header. The implementation
team extends these patterns to the full entity set.

### 6.1 Overview status section (built-in only: sections + tile + gauge)

```yaml
# View 1 — Overview, "Heat pump now" section
type: grid
cards:
  - type: heading
    heading: Heat pump now
    icon: mdi:heat-pump
  - type: tile
    entity: sensor.dimplex_wpm_controller_outdoor_temperature
    name: Outdoor
  - type: tile
    entity: sensor.dimplex_wpm_hc1_flow_temperature
    name: Flow
  - type: tile
    entity: sensor.dimplex_wpm_hc1_return_temperature
    name: Return
  - type: tile
    entity: sensor.dimplex_wpm_dhw_temperature
    name: DHW
    visibility:
      - condition: state
        entity: sensor.dimplex_wpm_dhw_temperature
        state_not: unavailable
  - type: gauge
    entity: sensor.dimplex_wpm_analytics_cop_en14511
    name: COP (est.)
    min: 0
    max: 6
    needle: true
    severity:
      green: 3.5
      yellow: 2
      red: 0
```

### 6.2 Energy view — multi-series power/COP (apexcharts) with measured-vs-estimated styling, plus history-graph fallback

```yaml
# View 2 — dual-axis: thermal kW (left) vs COP (right). Estimated = dashed.
type: custom:apexcharts-card
header:
  title: Power & efficiency (6 h)
  show: true
graph_span: 6h
yaxis:
  - id: kw
    decimals: 2
    apex_config:
      title: { text: kW }
  - id: cop
    opposite: true
    min: 0
    max: 6
    apex_config:
      title: { text: COP }
series:
  - entity: sensor.dimplex_wpm_analytics_thermal_power_loop
    name: Heat output (est.)
    yaxis_id: kw
    stroke_width: 2
    # estimated -> dashed
    extend_to: now
  - entity: sensor.dimplex_wpm_analytics_total_power
    name: Electric power
    yaxis_id: kw
  - entity: sensor.dimplex_wpm_analytics_cop_en14511
    name: COP (est.)
    yaxis_id: cop
    stroke_width: 1
---
# Fallback (built-in) if apexcharts is not installed — drop one or the other.
type: history-graph
title: Power & heat (6 h)
hours_to_show: 6
entities:
  - entity: sensor.dimplex_wpm_analytics_thermal_power_loop
  - entity: sensor.dimplex_wpm_analytics_thermal_power_compressor
  - entity: sensor.dimplex_wpm_analytics_thermal_power_heater
  - entity: sensor.dimplex_wpm_analytics_thermal_power_defrost_loss
  - entity: sensor.dimplex_wpm_analytics_total_power
```

### 6.3 Measured-vs-estimated: capability-gated conditional + source badge

```yaml
# Energy totals row — show MEASURED card only when the heat meter exists,
# otherwise the ESTIMATED card. Separate entities, gated by availability.
type: grid
cards:
  - type: entities
    title: Heat delivered (meter)
    visibility:
      - condition: state
        entity: sensor.dimplex_wpm_analytics_energy_to_house_kwh_measured
        state_not: unavailable
    entities:
      - entity: sensor.dimplex_wpm_analytics_energy_to_house_kwh_measured
        name: To house (meter)
        icon: mdi:gauge
  - type: entities
    title: Heat delivered (estimated)
    visibility:
      - condition: state
        entity: sensor.dimplex_wpm_analytics_energy_to_house_kwh_estimated
        state_not: unavailable
    entities:
      - entity: sensor.dimplex_wpm_analytics_energy_to_house_kwh_estimated
        name: To house (est.)
        icon: mdi:calculator-variant

# Runtime badge when ONE entity flips its `source` attribute instead:
- type: markdown
  content: >
    COP source:
    **{{ state_attr('sensor.dimplex_wpm_analytics_cop_en14511','source') }}**
    {% if state_attr('sensor.dimplex_wpm_analytics_cop_en14511','source')
        == 'estimated' %}— no heat meter; value is engine-estimated.{% endif %}
```

### 6.4 Gated control entity (View 4)

```yaml
# Only renders when control entities exist (enable_control on); otherwise the
# notice card shows instead.
type: grid
cards:
  - type: tile
    entity: number.dimplex_wpm_dhw_setpoint
    name: DHW setpoint
    features:
      - type: numeric-input
        style: slider
    visibility:
      - condition: state
        entity: number.dimplex_wpm_dhw_setpoint
        state_not: unavailable
  - type: markdown
    content: >
      Control is disabled. Enable **Advanced control** in the Dimplex WPM
      integration options to expose setpoints, SG Ready, and climate.
    visibility:
      - condition: state
        entity: number.dimplex_wpm_dhw_setpoint
        state: unavailable
```

---

## 7. Implementation notes (for the dashboard team)

- Ship files under `dashboards/`: `overview.yaml`, `energy.yaml`,
  `history.yaml`, `control.yaml`, `diagnostics.yaml`, plus a combined
  `dimplex_wpm.yaml` (full multi-view dashboard) for one-shot import. README
  documents both raw-config-editor import and `mode: yaml` inclusion.
- Keep **two parallel sections** on View 2 (apexcharts + history-graph) and
  tell users to delete one. Don't make apexcharts a hard dependency.
- Prefer per-card `visibility:` (sections) over the legacy `conditional` card
  wrapper — cleaner and the 2025/2026 idiom.
- Lock entity ids in one place once the integration's `unique_id`/slug scheme
  is final; this doc's slugs are the contract to confirm against the first
  real install (run the integration, read `states`, sed-replace).
- Carry forward the *good instincts* from the legacy dashboards: the "2nd heat
  generator running" signal (dashboard 1), the COP/flow/estimated-flow cross-
  check including an external flow sensor (dashboards 2/3), and the dedicated
  calibration page (dashboard 4) — but with native entities, split graphs,
  long-term stats, capability gating, and explicit estimated-vs-measured
  badging.
```
