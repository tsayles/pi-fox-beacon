# PyTower Radio Fox Hunt Beacon — Motherboard Specification

**Version:** 1.0 (Draft)
**Subsystem:** Main Control Board ("Motherboard" HAT)
**Project:** PyTower Radio — Amateur Radio Fox Hunting Beacon

---

## 1. Overview

The motherboard is the central control HAT in the PyTower stack. It sits between the Raspberry Pi Zero and the Power Management board, and interfaces directly with the Baofeng tri-band handheld transceiver (10W) and the step-attenuator module. It is responsible for audio generation, PTT keying, attenuator relay control, status display, and distribution of regulated power to onboard logic.

### 1.1 Stack Position
- **Above:** Raspberry Pi Zero (plugs in via GPIO/HAT header)
- **Below:** Power Management board (separate HAT)
- **External interfaces:** Baofeng radio (audio + PTT), step-attenuator module (relay control), status LCD

---

## 2. Functional Blocks (v1 / MVP)

1. **Digital audio generation** — I²S audio stream from Pi Zero → analog audio out to Baofeng mic input
2. **PTT control** — GPIO-driven, opto-isolated keying of Baofeng PTT line
3. **Attenuator relay control** — 6 independent relay drive lines (one per attenuation stage, switched in/out of RF path)
4. **Power interface** — Receives regulated rails from Power Management board below; distributes to onboard components
5. **Status display** — Small LCD/OLED for real-time status and error reporting
6. **Test infrastructure** — Test points on all key signals for future automated test rig (Phase 2)

## 3. Functional Blocks (v2+, Not in MVP — Reserve Space/Headers For)

- DTMF decode input (remote command/control via tone)
- Interactive voice control module interface
- Additional GPIO/expansion headers for future sensors (e.g., GPS)

---

## 4. Key Components

| Function | Component (candidate) | Notes |
|---|---|---|
| Audio codec | Wolfson/Cirrus **WM8731** (or equiv.) | I²S digital audio in, analog out to mic level; 2.7V–3.6V supply, runs at 3.3V |
| Relay drivers | ULN2003-type driver IC or logic-level SOT-23 MOSFETs | One channel per attenuator stage (6 total) |
| PTT isolation | Opto-isolator + small relay/MOSFET | Keeps Pi GPIO electrically isolated from radio PTT line |
| Status display | Small character LCD (I²C) or small OLED (I²C/SPI) | Shows TX state, attenuation level, battery voltage, faults |
| Voltage regulation | 3.3V and 5V rail regulators (fed from Power Mgmt board) | See Section 5 |
| Protection | TVS diodes on Baofeng audio input line | Guards against transients from radio side |
| Connectors | GPIO/HAT header (Pi Zero), stacking header (Power Mgmt board), board-edge SMA pass-through awareness (attenuator lives on its own module) | |
| Test points | Populated test pads on audio, PTT, relay control, and power rails | For future automated test fixture (2nd Pi + scripted test agent) |

---

## 5. Power Architecture

- **Input to motherboard:** Regulated rails supplied by the separate Power Management board (below in stack)
- **Primary rails needed on motherboard:**
  - **5V** — Raspberry Pi Zero input (Pi draws ~5V @ up to ~1.2A; onboard Pi regulator drops to 3.3V for its own processor)
  - **3.3V** — Audio codec (WM8731 operates 2.7V–3.6V) and most onboard logic/relay driver logic level
- Additional rail(s) may be needed depending on final relay driver selection (e.g., relay coil voltage if using mechanical/coax relays for the attenuator) — **TBD pending attenuator relay part selection**

---

## 6. Interfaces

| Interface | Direction | Purpose |
|---|---|---|
| I²S | In (from Pi Zero) | Digital audio stream for beacon tone/ID generation |
| GPIO — PTT | Out (to Baofeng, via isolation) | Key/unkey transmitter |
| GPIO — Relay control x6 | Out (to attenuator module) | Independent switch-in/out control per attenuation stage |
| I²C or SPI | Out (to LCD/OLED) | Status and error display |
| Stacking connector | To Power Management board | Regulated power in |
| Stacking connector | To Pi Zero | Power, I²S, GPIO |
| Test points | N/A | Bench/automated test access |

---

## 7. Design & Fabrication Notes

- **Implementation:** Custom PCBA, surface-mount components
- **Layout discipline:**
  - Separate analog audio path from digital/switching noise sources
  - Decoupling capacitors close to all IC power pins
  - Ground plane considerations for audio integrity (RF integrity is primarily an attenuator-module concern given board-edge SMA there, but keep noisy relay switching away from audio traces)
- **Testability:** Every functional block should expose test points/pads sufficient for bench probing and later automated test (candidate: second Pi Zero running scripted validation, phase 2)

---

## 8. Open Items / To-Do

- [ ] Finalize relay driver part selection for 6-stage attenuator control (drive voltage/current TBD)
- [ ] Confirm LCD/OLED part number and interface (I²C vs SPI)
- [ ] Schematic diagrams comparing micro-stage vs. binary-switched attenuator RF path (needed to finalize relay control line count/logic)
- [ ] Determine if additional voltage rail is required for relay coils
- [ ] Define GPIO/header pinout reserved for v2 DTMF and voice control expansion
- [ ] Define physical test point layout per module for Phase 2 automated test rig

---

## 9. Related Modules (Reference Only — Specified Separately)

- **Power Management board:** Single USB-C input; charges onboard Li-ion (18650) pack for Pi/motherboard side; passes through charging to Baofeng's own USB-C battery pack; power management ICs for dual charge-path safety
- **Attenuator module:** 6-stage, board-edge SMA in/out, mechanical RF relays (solid-state RF switches ruled out above ~1W; ten-watt handling requires mechanical/coax relays), targeting full 10W down to low-milliwatt output
