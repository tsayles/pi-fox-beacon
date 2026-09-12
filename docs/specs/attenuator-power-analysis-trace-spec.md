# PyTower Radio — Attenuator Resistor Network Power Analysis & PCB Trace Specification

**Version:** 1.0 (Draft)
**Applies to:** Both micro-stage and binary-switched attenuator designs (identical T-pad building block)
**Board assumption:** OSH Park 4-layer, 1 oz copper, ~62 mil overall thickness

---

## 1. Method

Each stage is a symmetric 50Ω T-pad (series R1 — shunt R2 to ground — series R3, with R1=R3). Standard matched-attenuator design equations were used:

- L = 10^(dB/20) (voltage attenuation ratio)
- R1 = R3 = 50 × (L−1)/(L+1)
- R2 = 50 × 2L/(L²−1)

**Worst-case assumption:** Because any stage's relay can be the first one engaged in the signal path (upstream stages bypassed), **every stage must be rated as if it alone receives the full 10W input** — not just the physically-first stage. This applies equally to both the micro-stage and binary-switched designs.

Power was calculated per-resistor at Pin = 10W, Zin = Zout = 50Ω (matched), using standard T-pad current/voltage analysis (input current Iin = √(Pin/50) = 0.447 A rms, Vin = 22.36 V rms).

---

## 2. Per-Stage Resistor Values & Power Dissipation (Pin = 10W)

| Atten. | R1 = R3 | R2 (shunt) | P(R1) | P(R2) | P(R3) | Total dissipated | Power to output |
|---|---|---|---|---|---|---|---|
| 1 dB | 2.88 Ω | 433 Ω | 0.58 W | 1.02 W | 0.46 W | 2.06 W | 7.94 W |
| 2 dB | 5.73 Ω | 215 Ω | 1.15 W | 1.82 W | 0.72 W | 3.69 W | 6.31 W |
| 4 dB | 11.3 Ω | 105 Ω | 2.26 W | 2.86 W | 0.90 W | 6.02 W | 3.98 W |
| 8 dB | 21.5 Ω | 47.3 Ω | 4.30 W | 3.43 W | 0.68 W | 8.42 W | 1.59 W |
| 16 dB | 36.3 Ω | 16.3 Ω | **7.26 W** | 2.30 W | 0.18 W | 9.75 W | 0.25 W |
| 32 dB | 47.6 Ω | 2.51 Ω | **9.51 W** | 0.47 W | 0.01 W | 9.99 W | 0.006 W |

*(Values are computed reference points; round to nearest standard 1% resistor values before BOM finalization.)*

**Key finding:** At high attenuation values (16 dB, 32 dB engaged as the first active stage), **R1 alone dissipates 7.3–9.5 W** — essentially the entire input power. This is far beyond what a standard SMD chip resistor (typically rated ¼W–1W in 0603/1206 sizes) can handle. Even the shunt resistor R2 in the low-attenuation stages (1–4 dB) sees roughly 1–3 W, which also exceeds common small SMD resistor ratings.

---

## 3. Component Selection Implications

Standard 0603/0805/1206 thin/thick-film chip resistors are **not adequate** for this application at any stage — every stage in the worst case must survive several watts to ~10W in a single resistor. Recommended approach:

- **R1/R3 (series) in high-attenuation stages (8/16/32 dB):** Use RF-rated power resistors — e.g., non-inductive thick-film power resistors in surface-mount power packages (2512 size rated 3W, or discrete leaded/surface power resistors rated 10–15W such as Vishay WSK/WSR or Ohmite series), ideally with a metal tab or thermal pad soldered to a copper pour/heatsink area rather than relying on the PCB trace alone.
- **R2 (shunt) in low/mid-attenuation stages (1/2/4 dB):** Also needs 2–3W rated parts minimum given up to ~2.9W dissipation.
- **Derating margin:** Add standard 50% derating margin for reliability — i.e., specify parts rated at least 1.5× the computed worst-case wattage (so ~15W-rated parts for the 32 dB R1, ~11W for 16 dB R1, ~3–4.5W for the R2 shunt resistors in low-attenuation stages).
- **Thermal design:** High-dissipation resistors (16/32 dB stages especially) will need a copper pour "heat spreader" on at least one PCB layer, thermal vias down to an internal/bottom copper plane, and physical spacing from adjacent components sensitive to heat (relay coils, connectors).
- **Relay power rating:** Confirm chosen coaxial RF relay contacts are rated for 10W continuous at VHF/UHF/220MHz — this was flagged in the schematic and is reinforced by this power analysis (relay contacts carry the same current as R1, so contact resistance heating is also a factor at these power levels, though typically much less significant than the resistor dissipation itself).

---

## 4. PCB Trace Specification (OSH Park 4-layer, 1 oz Cu)

### 4.1 Controlled-impedance RF trace (50Ω microstrip, top layer over layer-2 ground plane)

- OSH Park 4-layer stackup: ~6.7–7.9 mil prepreg between top layer and the layer-2 ground/reference plane, Er ≈ 3.66 (per OSH Park's published FR408 dielectric data)
- Published/measured 50Ω microstrip trace widths for this stackup cluster around **12–15 mils**, with some spread depending on calculator/measurement method and solder mask presence (community measurements range from ~12.5 mil calculated up to ~15–16 mil as-built to hit true 50Ω under soldermask)
- **Recommendation:** Start at **13 mil** trace width for the RF signal path as a design value, and verify against a controlled-impedance calculator (e.g., Saturn PCB Toolkit, KiCad's built-in calculator) using OSH Park's exact published stackup numbers at the time of layout, since dimensions have had minor revisions historically
- Keep layer 2 solid ground directly under the RF trace for its full length (no gaps/splits) to maintain consistent impedance through each stage

### 4.2 Current-carrying capacity check

- Max RF current in this design is only ~0.45 A rms (at 10W into 50Ω) — this is trivial from a pure current-carrying standpoint. Per IPC-2221 external-layer 1oz copper curves, even a 10 mil trace comfortably exceeds 1A capacity with minimal temperature rise.
- **Conclusion: trace width here is driven entirely by the 50Ω impedance requirement, not by current-carrying capacity.** No widening beyond the impedance-matched value is needed for current reasons.

### 4.3 Power/thermal-dissipation-adjacent copper (non-RF, at the resistor pads themselves)

- Separate from the controlled-impedance RF trace itself, the **copper pour/pad area directly under and around the power resistors** (R1/R2/R3 in each stage) should be sized for heat spreading, not signal integrity:
  - Recommend a solid copper pour (1 oz, ideally tied to an internal ground/thermal plane with an array of thermal vias, e.g., 0.3–0.4mm drill, 1mm pitch) under each high-power resistor footprint
  - This pour is a thermal feature, not a controlled-impedance trace — it should not run for a long distance as a "trace" but should be a localized spreading area sized to the resistor's thermal pad/footprint

---

## 5. Open Items / To-Do

- [ ] Confirm final resistor part numbers/packages for each stage based on computed worst-case wattage + 50% derating margin
- [ ] Verify actual OSH Park 4-layer stackup dimensions at time of order (values have shifted slightly across stackup revisions) and re-run 50Ω trace width calculation before final layout
- [ ] Thermal simulation or bench test of worst-case stage (32 dB, ~9.5W in R1) to confirm resistor and surrounding board temperature stay within safe margins during sustained 10W key-down
- [ ] Confirm coaxial RF relay contact power rating and thermal behavior under sustained 10W switching duty
- [ ] Reconcile resistor footprint size (power package) against the compact board dimensions discussed earlier (2×3" to 3×4" range) — high-power resistor packages may force a larger board than originally estimated
