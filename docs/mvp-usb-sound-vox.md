# MVP: USB Sound Interface + VOX Mode

## Overview

This MVP simplifies the original PiTower Radio design by eliminating custom hardware and using readily-available components:

- **Raspberry Pi** (any model with USB)
- **USB Audio Dongle** (3.5mm stereo output)
- **Baofeng UV-5RX3** in VOX mode (voice-activated transmission)
- **3.5mm audio cable** (Pi USB dongle → Baofeng mic/speaker jack)

No custom HATs, no PTT control circuit, no RF attenuator — just software-generated audio triggering the radio's built-in VOX.

---

## Hardware Requirements

### Components

| Component | Specification | Notes |
|-----------|--------------|-------|
| Raspberry Pi | Any model with USB port | Pi Zero W, Pi 3, Pi 4, etc. |
| USB Audio Dongle | USB sound card with 3.5mm output | Generic USB audio adapter (~$5-10) |
| Audio Cable | 3.5mm TRRS or TRS | Connects dongle to Baofeng K-port |
| Baofeng Radio | UV-5RX3 or UV-5R | Must support VOX mode |
| Power Supply | 5V USB power bank or wall adapter | For Raspberry Pi |

### Wiring

```
Raspberry Pi USB Port
    └── USB Audio Dongle
            └── 3.5mm plug
                    └── Baofeng K-port (mic/speaker connector)
```

The Baofeng K-port pinout (2.5mm/3.5mm TRRS):
- **Tip:** Speaker output
- **Ring 1:** Microphone input (audio from Pi goes here)
- **Ring 2:** Ground
- **Sleeve:** PTT (not used in VOX mode)

---

## Software Architecture

### Core Components

1. **Audio Generator**
   - Python script using `pyaudio` or similar
   - Generates beacon tones (morse code, CW ID, voice messages)
   - Routes audio to USB sound device

2. **Beacon Controller**
   - Schedule-based transmission
   - Power level simulation (adjust audio volume to trigger VOX at different ranges)
   - Configurable beacon patterns

3. **Configuration**
   - YAML or JSON config file
   - Callsign, beacon interval, message patterns
   - VOX sensitivity compensation (audio level adjustment)

### Key Software Dependencies

- Python 3.x
- `pyaudio` or `sounddevice` (audio output)
- `numpy` (waveform generation)
- `pyyaml` (configuration)

---

## VOX Mode Configuration

The Baofeng must be configured for VOX operation:

1. **Radio Settings:**
   - VOX level: Start with level 3-5 (adjust based on testing)
   - VOX delay: 0.5-1.0 seconds (delay after audio stops before PTT release)
   - Frequency: Set to desired beacon frequency
   - Power: High (10W) or Low (5W) as needed

2. **Audio Level Calibration:**
   - Too loud: VOX triggers on background noise
   - Too quiet: VOX doesn't trigger reliably
   - Target: Clean activation on beacon tones, no false triggers

---

## Advantages of MVP Approach

✅ **No custom PCB required** — use off-the-shelf components  
✅ **Rapid prototyping** — test beacon logic immediately  
✅ **Low cost** — under $50 in parts (excluding radio)  
✅ **Easy debugging** — all components are standard and well-documented  
✅ **Portable** — entire system fits in a small case  

---

## Limitations vs. Full PiTower Design

❌ **No RF power stepping** — can't attenuate the signal programmatically  
❌ **VOX latency** — ~100-500ms delay before transmission starts  
❌ **Less precise PTT control** — VOX may hold PTT longer than needed  
❌ **Audio quality dependent** — VOX sensitivity varies with tone/voice characteristics  
❌ **No hardware PTT** — can't do instant-on transmissions  

---

## Migration Path to Full Design

This MVP validates:
- Audio generation logic
- Beacon timing and scheduling
- Message encoding (morse code, voice synthesis)
- Field deployment workflows

Once proven, the full PiTower design adds:
- Hardware PTT control (precise timing)
- RF attenuator (programmable power stepping)
- Custom audio codec (better audio quality)
- Integrated power management (24+ hour runtime)

---

## Development Roadmap

### Phase 1: Basic Beacon (This PR)
- [ ] USB audio device detection and configuration
- [ ] Simple tone generator (1kHz test tone)
- [ ] VOX trigger testing
- [ ] Basic beacon loop (transmit every N minutes)

### Phase 2: Morse Code
- [ ] Morse code generator (callsign identification)
- [ ] CW tone generation (600-800 Hz)
- [ ] WPM configuration

### Phase 3: Voice Messages
- [ ] Text-to-speech integration (pyttsx3 or festival)
- [ ] Voice message queue
- [ ] Callsign announcement

### Phase 4: Remote Control
- [ ] DTMF tone detection (if Pi has audio input)
- [ ] Web interface for configuration
- [ ] SSH-based remote control

---

## Testing Plan

1. **Bench Testing:**
   - Verify audio output from USB dongle
   - Confirm VOX triggering at various audio levels
   - Measure VOX latency and PTT hold time

2. **Field Testing:**
   - Transmit range testing (High vs Low power)
   - Battery runtime testing
   - Signal quality reports from receivers

3. **Integration Testing:**
   - 24-hour continuous beacon operation
   - Configuration change testing
   - Error recovery (USB disconnect, power loss)

---

## Reference Links

- [Baofeng UV-5R VOX Mode Guide](https://www.miklor.com/uv5r/)
- [Raspberry Pi Audio Configuration](https://www.raspberrypi.org/documentation/usage/audio/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/)

---

## License

*(Same as main project)*
