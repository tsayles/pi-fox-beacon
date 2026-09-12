# PyTower Radio Fox Hunt Beacon — Power Management Board & Battery Pack Specification

**Version:** 1.0 (Draft)
**Subsystem:** Power Management HAT + External Battery Pack
**Project:** PyTower Radio — Amateur Radio Fox Hunting Beacon

---

## 1. Overview

The power management board is the lowest HAT in the PyTower stack (or otherwise wired to it). It accepts external USB-C charging input, manages charging of the main external Li-ion battery pack, regulates and distributes 5V/3.3V rails to the motherboard above, and provides a separate USB-A charging output to continuously top up the Baofeng UV-5RX3's own BL-5 battery pack during operation.

## 2. Operating Assumptions (Design Basis)

| Parameter | Value | Notes |
|---|---|---|
| Target beacon runtime | 24 hours | Single charge, no swap |
| Target main-pack charge time | 2–4 hours | Via USB-C, PD-negotiated |
| Radio TX duty cycle | 40% | Assumption for fox hunt operation |
| Radio | Baofeng UV-5RX3 | Up to 10W RF output |
| Radio battery | BL-5, 1800mAh @ 7.4V (13.3Wh) | **Not** the extended BL-5L (3800mAh) |
| Radio TX current draw (est.) | ~2.0–2.5A @ 7.4V | Typical handheld PA efficiency; needs bench verification |
| Radio standby/RX current draw (est.) | ~0.3A @ 7.4V | Estimate, needs verification |
| Radio average current draw | ~1.1A @ 7.4V (≈8.1W) | At 40% duty cycle |
| BL-5 standalone runtime | ~1.6 hours | Confirms BL-5 alone cannot support a 24h hunt — continuous charge-through required |

**Key finding:** The Baofeng's own BL-5 pack cannot sustain 24-hour operation — the power board must continuously feed charging current to the BL-5 (via its USB-C port) throughout the hunt, sized to roughly match or exceed its ~1.1A average draw.

---

## 3. Power Budget (Main Battery Pack)

| Load | Estimated avg. power |
|---|---|
| Beacon electronics (Pi Zero, audio codec, relay drivers, LCD) | ~2 W |
| Baofeng BL-5 charge-through (sustaining ~1.1A/7.4V avg draw, incl. charge inefficiency) | ~9–10 W |
| **Total average draw** | **~11–12 W** |

**Energy required for 24h runtime:** ~11.5W × 24h ≈ **~275 Wh**

---

## 4. Main Battery Pack Requirements

- **Chemistry/form factor:** 18650 Li-ion cells, external plastic holder (not mounted on PCB)
- **Configuration:** 2S (series) for ~7.2V nominal bus
- **Parallel count:** Sized for ~275Wh target
  - Using ~3.4–3.5Ah per 18650 cell: **2S12P** (24 cells total) yields ≈ 40.8Ah ≈ **~294 Wh** — recommended for headroom
  - *(Earlier working assumption of 2S10P was based on a since-corrected, oversized Baofeng draw estimate — 2S12P reflects the corrected BL-5-based numbers plus margin)*
- **Nominal voltage:** 7.2–7.4V (2S)
- **Total capacity:** ~40–41 Ah
- **Physical packaging:** External to power board; separate plastic cell holder
- **Note:** Final cell count should be revisited once actual bench-measured current draw (TX/RX/standby) on the UV-5RX3 is available — figures above are estimates

---

## 5. Charging Requirements — Main Pack (USB-C Input)

- **Target charge time:** 2–4 hours for ~40Ah pack
- **Implication:** Requires high charge power — USB Power Delivery (PD) negotiation is mandatory; basic 5V/2A USB will not meet this target
- **Estimated charge power needed:** Roughly 70–170W depending on final capacity and acceptable charge time (higher end of PD profiles, e.g., 20V/5A or Extended Power Range profiles up to ~28V, may be required)
- **Components:**
  - USB-C PD controller/negotiator IC (e.g., STUSB4500-class part) to request appropriate voltage/current profile from the source charger
  - High-current buck charging IC/charge controller capable of multi-string parallel pack charging and cell balancing across the parallel groups
  - Overvoltage, overcurrent, overtemperature protection
  - Cell/string balancing monitoring across the 12 parallel strings

---

## 6. Charging Requirements — Baofeng BL-5 Pack (USB-A Output)

- **Connector:** Dedicated USB-A output (separate/independent from the USB-C main input)
- **Source:** Tapped from the regulated 5V rail on the power board (not raw pack voltage)
- **Rationale:** BL-5 pack charges via standard 5V USB-C charging internally (confirmed — Baofeng BL-5/BL-5L packs use basic 5V USB charging, not PD negotiation) — a simple regulated 5V feed is sufficient, no PD negotiation needed on this leg
- **Sizing:** Must sustain ~1.1A average continuously during operation to keep pace with the radio's own average draw at 40% duty cycle; peak charge current should be sized with margin above this average
- **Electrical independence:** This charge path is electrically separate from the main pack's USB-C charging input/circuit — no direct interaction between the two charging systems

---

## 7. Voltage Regulation & Distribution

| Rail | Consumer(s) | Source |
|---|---|---|
| 5V | Pi Zero (via motherboard), Baofeng USB-A charge output | Regulated down from 7.2–7.4V main pack |
| 3.3V | Audio codec, logic-level components on motherboard | Regulated down from main pack or from 5V rail |

- Regulators must be sized for combined worst-case load (beacon electronics + BL-5 charge-through + any margin)
- Rails distribute upward through the stacking connector to the motherboard

---

## 8. Component Candidates

| Function | Component (candidate) |
|---|---|
| USB-C PD negotiation | STUSB4500 or equivalent PD sink controller |
| Main pack charge management | BQ257xx-class multi-cell/multi-string Li-ion charge controller (or equivalent) |
| Cell/string balancing & protection | Dedicated BMS IC appropriate for 2S/12P configuration |
| 5V regulation | Buck converter sized for combined beacon + BL-5 charge-through load |
| 3.3V regulation | Buck/LDO off 5V rail or direct from pack, per final load calc |
| USB-A output (BL-5 charging) | Simple regulated 5V feed, standard USB-A connector, no PD IC required |

---

## 9. Open Items / To-Do

- [ ] Bench-measure actual UV-5RX3 current draw: TX (at 10W and at lower attenuator-stepped power levels), RX, and standby
- [ ] Confirm real-world PA efficiency for the UV-5RX3 to refine average draw calculations
- [ ] Finalize exact parallel cell count (2S12P working figure) once measured data is available
- [ ] Select and validate PD controller + charge IC combination capable of the required 70–170W charge power within 2–4 hour target
- [ ] Define balancing/monitoring strategy across 12 parallel strings
- [ ] Confirm regulated 5V rail sizing accounts for simultaneous beacon load + BL-5 charge-through under worst-case (continuous TX) conditions
- [ ] Physical design of external 2S12P 18650 holder/pack enclosure
- [ ] Test point placement for automated test rig (Phase 2), per general test infrastructure requirement

---

## 10. Related Modules (Reference Only — Specified Separately)

- **Motherboard:** Consumes regulated 5V/3.3V rails from this board; hosts I²S audio, PTT, attenuator relay control, LCD status display
- **Attenuator module:** Reduces Baofeng TX power at range-dependent steps during hunt — does not affect power board design directly, but reduced TX power at closer range may somewhat lower average Baofeng draw during those phases (not yet factored into budget above; treat current budget as worst-case/high-power-phase estimate)
