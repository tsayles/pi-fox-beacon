# Session State: pi-fox-beacon / PiTower Radio

Purpose: compact handoff record for another agent picking up this project. Read top-down; each section is self-contained — stop once you have what you need.

## 1. Project Identity

- **Project:** PiTower Radio — Pi Zero–controlled amateur radio fox hunting beacon
- **Repo:** `pi-fox-beacon`
- **Goal:** automate a Baofeng UV-5RX3 handheld as a fox-hunt beacon with programmable RF power stepping, for regional mobile hunts (greater Seattle area)
- **Form factor:** stack of Raspberry Pi HATs ("PiTower") — Pi Zero + Motherboard HAT + Power Management HAT + Attenuator module
- **Phase:** hardware specification / schematic design (pre-PCB-layout)

## 2. Module Status Table

| Module | Status | Spec doc |
|---|---|---|
| Motherboard (audio/PTT/attenuator ctrl/LCD) | Spec drafted, components selected at concept level | `pytower-motherboard-spec.md` |
| Power Management board | Spec drafted, battery sizing revised once (see §5) | `pytower-power-board-spec.md` |
| Attenuator module | Topology + schematics + power analysis done; component sourcing unresolved | `attenuator-power-analysis-trace-spec.md` + schematic SVGs |
| Firmware | Not started | — |
| Test infrastructure | Deferred to Phase 2 (design-for-test only, in this phase) | — |
| PCB layout | Not started | — |

## 3. Key Specs (Current/Final Values)

| Parameter | Value |
|---|---|
| Radio | Baofeng UV-5RX3, tri-band, ≤10W |
| Radio battery | BL-5, 1800mAh @ 7.4V (NOT the 3800mAh BL-5L) |
| Radio TX current (est., unverified) | ~2.0–2.5A during TX, ~0.3A standby |
| Assumed TX duty cycle | 40% |
| Target runtime | 24h/charge |
| Target charge time | 2–4h |
| Main battery | 18650 Li-ion, 2S config, ~2S12P (24 cells, ~294Wh) — working figure, pending real current measurement |
| Main pack charging | USB-C w/ Power Delivery (needed: ~70–170W to hit charge-time target) |
| Baofeng charge path | USB-A off regulated 5V rail (Baofeng BL-5 uses plain 5V USB charging, no PD) |
| Control audio | I²S (Pi Zero) → audio codec (candidate: WM8731) → Baofeng mic in |
| Attenuator stages | 6 (micro-stage design) or 3 (binary-weighted design) — **electrically identical building block**: SPDT relay bypasses a T-pad |
| Attenuator connectors | Board-edge SMA in/out |
| PCB fab target | OSH Park 4-layer, 1oz Cu; ~13 mil trace for 50Ω microstrip (impedance-limited, not current-limited) |

## 4. Attenuator — Critical Findings

1. **Micro-stage vs binary-switched are NOT different architectures** — same T-pad+bypass-relay block; only stage count and value-weighting differ (6 arbitrary stages/64 combos vs 3 binary-weighted stages/8 combos).
2. **Worst case: any stage may see full 10W** (its relay could be the first one engaged) → every stage's resistors must be rated for full-power dissipation, not just the physically-first stage.
3. **Computed power dissipation per stage at 10W in** (T-pad, Z0=50Ω): 1dB stage max 1.0W (R2), ..., **16dB stage R1 = 7.26W, 32dB stage R1 = 9.51W** — full table in `attenuator-power-analysis-trace-spec.md`.
4. **Standard SMD chip resistors are inadequate** at any stage (even best 2512 SMD power resistors cap ~6W). High-atten stages likely need through-hole/leaded power resistors, paralleled SMD resistors, or commercial attenuator pads.
5. **Through-hole introduces lead-inductance/impedance-matching risk** at VHF/UHF — mitigate with short leads, direct ground-plane vias; expect to verify match empirically (VNA) post-assembly.
6. **Commercial fixed attenuator pads are expensive for this use case**: e.g. Pasternack PE7016-10 (10dB/10W/SMA) = **$667 (qty1) / $595 (qty10)**, 15-week lead time. Buying 3–6 of these for the high-power stages would run **~$750–4,000+**, in tension with the project's stated cost/availability priority. DIY resistor approach (paralleled/leaded, ~$1–5/resistor) likely still preferred despite added engineering effort — **this tradeoff is unresolved**.
7. Mechanical/coaxial RF relays required for 10W switching (SMD RF switch ICs top out ~1W) — roughly golf-ball to matchbox sized, ~inch-scale.

## 5. Power Board — Correction History (important — don't re-derive from stale numbers)

- Initial sizing assumed continuous Baofeng charging at "1–1.5A" → led to oversized 2S20-25P (40-50 cell) estimate.
- **Corrected** once actual radio/battery model (UV-5RX3 / BL-5, 1800mAh) was confirmed: BL-5 alone only lasts ~1.6h at 40% duty cycle — confirms continuous charge-through is required, but at the **corrected** lower average draw (~1.1A @ 7.4V ≈ 8.1W), not the earlier inflated figure.
- Current working total power budget: ~11–12W average → ~275Wh/24h → **2S12P 18650** pack recommended (see §3). Revisit once bench data exists.

## 6. Open Items (Unresolved, Cross-Session)

- [ ] Bench-measure actual UV-5RX3 current draw (TX/RX/standby) — everything in §3/§5 downstream of this is an estimate
- [ ] Decide attenuator resistor sourcing: DIY (leaded/parallel-SMD) vs. commercial pad, per §4.6 cost tension
- [ ] Finalize attenuator relay part (10W-rated coaxial/mechanical)
- [ ] Full manufacturable schematics (KiCad) — current schematics are block/reference-level only, not fabrication-ready
- [ ] PCB layout (all 3 boards)
- [ ] Confirm OSH Park stackup dims at time of order before finalizing 50Ω trace width
- [ ] USB-C PD controller + charge IC selection for main pack
- [ ] Physical footprint re-check: power-resistor packages may force board larger than early 2×3"–3×4" estimate
- [ ] Firmware not started (v1: PTT/audio/attenuator/LCD; v2: DTMF; v3: voice control)
- [ ] Test point layout details (Phase 2 automated test, 2nd-Pi-based)

## 7. Artifact Index (files produced this session)

| File | Content |
|---|---|
| `pytower-motherboard-spec.md` | Full motherboard functional spec, components, power rails, I/O |
| `pytower-power-board-spec.md` | Power board + battery pack requirements (pre-BL-5-correction numbers — see §5 for corrected figures) |
| `micro-stage-attenuator.svg`, `binary-switched-attenuator.svg` | Early block-diagram schematics (superseded by full versions below) |
| `micro-stage-attenuator-full-schematic.svg` | Full electrical schematic, 6-stage T-pad design, component-level |
| `binary-switched-attenuator-full-schematic.svg` | Full electrical schematic, 3-stage binary-weighted T-pad design |
| `attenuator-power-analysis-trace-spec.md` | Per-resistor power dissipation table, PCB trace width analysis, component implications |
| `README.md` | Repo README for `pi-fox-beacon` |
| `session-summary.md` (this file) | Progressive-discovery handoff summary |

## 8. Terminology Corrections (don't reintroduce)

- It's **PiTower**, not PyTower.
- Radio is confirmed **UV-5RX3** with **BL-5** battery (not BL-5L).
- Control audio is **I²S**, not I²C (this was corrected once mid-session).
