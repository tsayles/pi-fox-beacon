# MVP: AIOC Hardware PTT Interface

## Overview

This MVP uses the **NA6D AIOC (All-In-One Cable)** to combine USB audio and hardware PTT control into a single plug-and-play adapter. This replaces the separate USB audio dongle + BTECH cable used in the original VOX-only approach.

**Hardware:**
- Raspberry Pi (any model with USB)
- [NA6D AIOC adapter](https://na6d.com/products/aioc-ham-radio-all-in-one-cable) (~$40)
- Baofeng UV-5R series radio (Kenwood K1 / K-port compatible)

**No VOX required** — the AIOC provides hardware PTT via serial port DTR, giving precise control over transmit timing.

**📖 For complete hardware setup instructions, see [mvp-hardware-setup.md](mvp-hardware-setup.md)**

---

## Hardware Requirements

### Components

| Component | Part Number / Model | Price | Status |
|-----------|-------------------|-------|--------|
| Raspberry Pi | Raspberry Pi 3 Model B+ | ~$40 | Ordered (SparkFun #430326) |
| AIOC Adapter | NA6D AIOC Ham Radio All-In-One Cable | ~$40 | Purchase at na6d.com |
| Baofeng Radio | K5PLUS (10W tri-band, ASIN B0GTDDRGY7) | ~$40 | On hand |
| Power Supply | 5V/2.5A USB power supply or power bank | ~$10 | TBD |

**Total Hardware Cost:** ~$90 (excluding radio already on hand)

### What the AIOC Provides

The AIOC is a single USB-C device that replaces multiple adapters:

| Function | How |
|----------|-----|
| USB sound card (TX audio) | Built-in STM32 DAC |
| Hardware PTT | Serial port DTR line |
| Radio programming | Virtual COM port (CHIRP compatible) |

**Radio Compatibility:** Kenwood K1 (2-pin) connector — Baofeng UV-5R, UV-5RX3, K5PLUS, Quansheng UV-K5, BTech, and others. *Not compatible with Icom, Yaesu, or waterproof Baofeng models (e.g. UV-9R).*

### Wiring Diagram

```
Raspberry Pi
    ↓ USB-A port
NA6D AIOC adapter (USB-C)
    ↓ Kenwood K1 plug (2-pin, built into AIOC cable)
Baofeng K-port (side of radio)
```

**Signal Path:**
- Pi generates audio in software (numpy sine waves)
- Audio output via ALSA to AIOC USB sound device
- PTT asserted via AIOC serial port DTR before audio starts
- AIOC keys radio PTT directly (no VOX needed)
- PTT released after audio completes

### Kenwood K1 Connector Pinout

The AIOC terminates in a standard Kenwood K1 (2-pin) connector:
- **3.5mm jack:** Speaker output (from radio)
- **2.5mm jack:** Microphone input + PTT
  - Tip: Microphone (TX audio from AIOC DAC)
  - Sleeve: PTT (AIOC asserts this to transmit)
  - Ring: Ground

---

## Software Architecture

### Core Components

1. **Beacon Controller** (`beacon.py`)
   - Asserts PTT via serial DTR before each transmission
   - Releases PTT after audio playback completes
   - Falls back to VOX mode if `ptt.enabled: false` in config

2. **Audio Generator** (`audio_generator.py`)
   - Generates beacon tones (morse code, CW ID)
   - Routes audio to AIOC USB sound device via sounddevice/ALSA

3. **Morse Code Generator** (`morse.py`)
   - Encodes text to CW audio at configurable WPM

4. **Configuration** (`config.yaml`)
   - Callsign, beacon interval, morse settings
   - AIOC serial port and PTT timing

### Key Software Dependencies

- Python 3.x
- `sounddevice` (audio output via ALSA)
- `numpy` (waveform generation)
- `pyserial` (PTT via AIOC serial DTR)
- `pyyaml` (configuration)

---

## PTT Configuration

The AIOC appears as two devices on Linux:
- **USB sound card** — detected automatically by ALSA
- **Serial port** — typically `/dev/ttyACM0`

### Find the AIOC Serial Port

```bash
ls /dev/ttyACM*
# or
ls /dev/serial/by-id/ | grep -i aioc
```

### Grant Serial Port Access

```bash
sudo usermod -aG dialout $USER
# Log out and back in for group change to take effect
```

### config.yaml PTT Settings

```yaml
ptt:
  enabled: true
  port: "/dev/ttyACM0"   # Adjust if needed
  ptt_on_delay: 0.05     # Seconds after PTT before audio
  ptt_off_delay: 0.05    # Seconds after audio before PTT release
```

---

## Advantages Over VOX-Only Approach

✅ **No VOX required** — precise PTT timing, no preamble tone needed  
✅ **Single cable** — AIOC replaces USB audio dongle + BTECH APRS-K1 cable  
✅ **Instant PTT** — no 100-500ms VOX latency  
✅ **Clean transmissions** — first morse element is never clipped  
✅ **Open source hardware** — AIOC firmware and schematics on GitHub  
✅ **Plug-and-play** — no drivers needed on Linux/Windows/macOS  

---

## Limitations vs. Full PiTower Design

❌ **No RF power stepping** — radio transmits at fixed selected power  
❌ **No hardware integration** — separate Pi + radio + cable  

**Note:** Audio amplitude affects FM audio deviation, not carrier power. The radio transmits at full selected power (10W/7W/4W) regardless of audio level.

---

## Fallback: VOX Mode

If the AIOC is unavailable, set `ptt.enabled: false` in config.yaml and configure the radio for VOX mode:

1. Press MENU → VOX → Set level 5 (adjust as needed)
2. Increase `pre_audio_silence` to ~0.3s in config to compensate for VOX latency

---

## Migration Path to Full Design

This MVP validates:
- Audio generation and morse code encoding
- Beacon timing and scheduling
- Hardware PTT control via serial

Once proven, the full PiTower design adds:
- GPIO-based PTT (no USB serial dependency)
- RF attenuator (programmable power stepping)
- Custom audio codec
- Integrated power management (24+ hour runtime)

---

## Development Roadmap

### Phase 1: Basic Beacon ✅ (Implemented in this PR)
- [x] USB audio device detection and configuration
- [x] Simple tone generator (700 Hz CW tone)
- [x] Hardware PTT via AIOC serial DTR
- [x] Basic beacon loop (transmit every N minutes)
- [x] Morse code generator (callsign identification)
- [x] WPM configuration
- [ ] Hardware testing with actual Pi + AIOC + radio
- [ ] PTT timing calibration

### Phase 2: Field Testing (Next)
- [ ] Bench test complete hardware stack
- [ ] Verify PTT timing (ptt_on_delay / ptt_off_delay)
- [ ] Range testing (High vs Low power)
- [ ] Signal quality reports from receivers
- [ ] 24-hour continuous beacon test
- [ ] Power consumption measurement

### Phase 3: Voice Messages
- [ ] Text-to-speech integration (pyttsx3 or festival)
- [ ] Mixed morse + voice announcements

### Phase 4: Remote Control
- [ ] Web interface for configuration
- [ ] SSH-based remote control
- [ ] Status monitoring/logging

---

## Testing Plan

### 1. Bench Testing (With Hardware)
- [ ] Verify AIOC detected by Pi (`lsusb`, `aplay -l`, `ls /dev/ttyACM*`)
- [ ] Run `test_audio.py` and verify tone output
- [ ] Test hardware PTT via `test_audio.py` PTT section
- [ ] Confirm radio TX LED lights during PTT test
- [ ] Verify morse code is readable (listen on second radio)
- [ ] Measure PTT-to-audio latency

### 2. Field Testing
- [ ] Transmit range testing at HIGH power (10W)
- [ ] Transmit range testing at LOW power (4W)
- [ ] Signal quality reports from receivers
- [ ] Battery runtime testing (Pi + radio on power bank)
- [ ] Outdoor deployment test

### 3. Integration Testing
- [ ] 24-hour continuous beacon operation
- [ ] Error recovery (USB disconnect, audio device reset)
- [ ] Log analysis (missed beacons, timing accuracy)

### 4. Fox Hunt Validation
- [ ] Deploy as actual fox in practice hunt
- [ ] Gather feedback from hunters on signal clarity
- [ ] Validate beacon timing meets hunt requirements

---

## Hardware Documentation

See detailed hardware setup instructions:
- **docs/mvp-hardware-setup.md** - Complete assembly and configuration guide
- **docs/orders/** - Purchase receipts and part numbers

## Reference Links

- [NA6D AIOC Product Page](https://na6d.com/products/aioc-ham-radio-all-in-one-cable)
- [AIOC Open Source Project (GitHub)](https://github.com/skuep/AIOC)
- [AIOC Documentation](https://skuep.github.io/AIOC/)
- [Raspberry Pi Audio Configuration](https://www.raspberrypi.org/documentation/usage/audio/)

---

## License

*(Same as main project)*
