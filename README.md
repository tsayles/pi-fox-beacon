# pi-fox-beacon

**PiTower Radio** — a Raspberry Pi Zero–controlled amateur radio fox hunting beacon.

A modular, stacked-HAT system that turns a Baofeng UV-5RX3 handheld transceiver into an automated, remotely-controllable fox hunt beacon with programmable RF power stepping — built for regional mobile hunts (initial design target: greater Seattle area).

---

## Overview

pi-fox-beacon controls a Baofeng UV-5RX3 (up to 10W output) via PTT keying and I²S-generated audio, and steps its effective transmit power down over the course of a hunt using a custom RF attenuator module — drawing hunters in from a distance, then making the final approach progressively harder as they close in.

The system is built as a vertical stack of Raspberry Pi HATs ("PiTower"), each board handling one concern:

- **Raspberry Pi Zero** — runs the beacon logic, generates I²S audio, drives GPIO control lines
- **Motherboard HAT** — I²S audio codec, PTT control, attenuator relay control, status LCD, power distribution
- **Power Management HAT** — USB-C PD charging input, main battery pack management, USB-A charge-through to the Baofeng's own battery
- **Attenuator module** — switched resistive T-pad network providing 6–8 stages of RF attenuation between the Baofeng and the antenna

---

## Key Design Facts

| Item | Value |
|---|---|
| Radio | Baofeng UV-5RX3, tri-band, up to 10W |
| Radio battery | BL-5, 1800mAh @ 7.4V |
| Control computer | Raspberry Pi Zero |
| Audio interface | I²S → audio codec → Baofeng mic input |
| RF attenuator | 6–8 stage switched T-pad network, board-edge SMA in/out |
| Attenuator control | GPIO → relay driver → RF relays (mechanical/coaxial, rated for 10W) |
| Target runtime | 24 hours per charge |
| Target charge time | 2–4 hours (USB-C, Power Delivery) |
| Main battery | 18650 Li-ion pack, external holder, 2S configuration (parallel count TBD pending bench-measured current draw) |
| PCB fab target | OSH Park, 4-layer, 1oz copper |
| Assumed RF TX duty cycle | 40% |

---

## Repository Structure

```
pi-fox-beacon/
├── hardware/
│   ├── motherboard/        # Main control HAT: audio, PTT, attenuator control, LCD
│   ├── power-board/        # Charging, battery management, voltage regulation
│   └── attenuator/         # RF attenuator module (T-pad network + relays)
├── firmware/                # Pi Zero control software (Python)
├── docs/
│   ├── specs/                # Board-level specifications
│   └── schematics/           # Schematic references / block diagrams
└── test/                     # Automated test scripts (Phase 2)
```

*(Adjust to match actual repo layout as it develops — this reflects the modules specified so far.)*

---

## Project Status

**Phase: Hardware specification / schematic design**

- [x] Overall system architecture defined (Pi Zero + motherboard + power board + attenuator, stacked HAT form factor)
- [x] Motherboard functional spec drafted
- [x] Power board / battery pack requirements drafted
- [x] Attenuator T-pad topology and relay-switching schemes drafted (micro-stage vs. binary-switched)
- [x] Power dissipation analysis completed for attenuator resistor networks
- [ ] Final resistor/component selection for attenuator (custom leaded/parallel-SMD vs. commercial attenuator pad — cost tradeoff still open)
- [ ] Full manufacturable schematics (KiCad) for all three boards
- [ ] PCB layout
- [ ] Firmware (v1: PTT + audio + attenuator stepping; v2: DTMF control; v3: interactive voice)
- [ ] Automated test infrastructure (second Pi + scripted validation)

---

## Version Roadmap

- **v1 (MVP):** I²S audio generation, PTT control, attenuator relay control, status LCD
- **v2:** DTMF remote control
- **v3:** Interactive voice control

---

## Design Notes

- All boards designed with test points for future automated testing (planned: a second Raspberry Pi running scripted validation against each module).
- Attenuator resistor networks require power ratings well beyond standard SMD chip resistors at the higher attenuation stages — see `docs/specs/` for the full power dissipation analysis and component tradeoffs (custom resistor networks vs. commercial fixed attenuator pads).
- The Baofeng's own BL-5 battery cannot sustain a 24-hour hunt alone — the power board continuously charges it via USB-A pass-through during operation.

---

## Related Projects

- [PiTowerRadio-Concept](https://github.com/tsayles/PiTowerRadio-Concept) —
  The original concept repository that preceded this project, containing
  early design notes and exploratory work for the PiTower Radio system.

---

## License

*(TBD)*

## Contributing

*(TBD)*
