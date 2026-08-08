# MVP: USB Sound Interface + VOX Mode

## Overview

This MVP simplifies the original PiTower Radio design by eliminating custom hardware and using readily-available components:

- **Raspberry Pi 3 Model B+** (quad-core 1.4GHz, built-in WiFi)
- **UGREEN USB Audio Adapter** (24bit/96kHz DAC, TRRS)
- **BTECH APRS-K1 Cable** (Kenwood K1 to 3.5mm TRRS audio interface)
- **Baofeng UV-5RX3** in VOX mode (voice-activated transmission)

No custom HATs, no PTT control circuit, no RF attenuator — just software-generated audio triggering the radio's built-in VOX.

**📖 For complete hardware setup instructions, see [mvp-hardware-setup.md](mvp-hardware-setup.md)**

---

## Hardware Requirements

### Components (Actual Setup)

| Component | Part Number / Model | Price | Status |
|-----------|-------------------|-------|--------|
| Raspberry Pi | Raspberry Pi 3 Model B+ | ~$40 | Ordered (SparkFun #430326) |
| USB Audio Dongle | UGREEN USB to 3.5mm Jack Audio Adapter (24bit/96kHz, TRRS, 9.8") | ~$15 | Ordered (Amazon) |
| Audio Cable | BTECH APRS-K1 Multi-Function Universal Audio Interface Cable | ~$25 | On hand |
| Baofeng Radio | UV-5RX3 (10W tri-band) | — | On hand |
| Power Supply | 5V/2.5A USB power supply or power bank | ~$10 | TBD |

**Total Hardware Cost:** ~$90 (excluding radio and power supply already on hand)

### Alternative Cable Option

Also available: [Digirig Baofeng Cables Set](https://digirig.net/product/baofeng-cables/) (~$35)
- Higher quality shielded cables with ferrite chokes
- Dual 3.5mm plugs (separate mic/speaker)
- Can be used instead of APRS-K1 if preferred

### Wiring Diagram

```
Raspberry Pi 3 B+
    ↓ USB-A port
UGREEN USB Audio Adapter (24bit/96kHz)
    ↓ 3.5mm TRRS jack
BTECH APRS-K1 Cable (3.5mm TRRS plug → Kenwood K1 connector)
    ↓ Kenwood K1 plug (2-pin)
Baofeng UV-5RX3 K-port
```

**Signal Path:**
- Pi generates audio in software (numpy sine waves)
- Audio output via ALSA to USB audio device
- UGREEN adapter converts USB digital audio to analog 3.5mm
- APRS-K1 cable routes audio to Baofeng microphone input
- Baofeng VOX detects audio and keys PTT automatically
- No GPIO or hardware PTT control needed!

### Kenwood K1 Connector Pinout

The Baofeng K-port uses standard Kenwood K1 (2-pin):
- **3.5mm jack:** Speaker output (from radio)
- **2.5mm jack:** Microphone input + PTT
  - Tip: Microphone (audio from Pi goes here)
  - Sleeve: PTT (grounded to transmit, floating for receive)
  - Ring: Ground

**For VOX mode:** Only the microphone input is used. PTT pin is left floating.

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

### Phase 1: Basic Beacon ✅ (Implemented in this PR)
- [x] USB audio device detection and configuration
- [x] Simple tone generator (1kHz test tone)
- [x] VOX trigger testing via test_audio.py
- [x] Basic beacon loop (transmit every N minutes)
- [x] Morse code generator (callsign identification)
- [x] CW tone generation (600-800 Hz)
- [x] WPM configuration
- [ ] Hardware testing with actual Pi 3 B+ + UGREEN + BTECH APRS-K1
- [ ] VOX calibration and tuning

### Phase 2: Field Testing (Next)
- [ ] Bench test complete hardware stack
- [ ] Verify VOX triggering reliability
- [ ] Measure VOX latency and PTT hold time
- [ ] Range testing (High vs Low power)
- [ ] Signal quality reports from receivers
- [ ] 24-hour continuous beacon test
- [ ] Power consumption measurement

### Phase 3: Voice Messages
- [ ] Text-to-speech integration (pyttsx3 or festival)
- [ ] Voice message queue
- [ ] Callsign announcement in voice
- [ ] Mixed morse + voice announcements

### Phase 4: Remote Control
- [ ] Web interface for configuration
- [ ] SSH-based remote control
- [ ] Status monitoring/logging
- [ ] Remote shutdown/restart
- [ ] (Future: DTMF control if we add audio input)

---

## Testing Plan

### 1. Bench Testing (With Hardware)
- [ ] Verify UGREEN adapter detected by Pi (lsusb, aplay -l)
- [ ] Run test_audio.py and verify tone output
- [ ] Confirm Baofeng VOX triggers (PTT LED lights)
- [ ] Test different VOX levels (1-10 on radio)
- [ ] Test different vox_trigger_level values (0.3-0.8 in config)
- [ ] Measure VOX latency (time from audio start to PTT)
- [ ] Measure VOX hold time (time from audio stop to PTT release)
- [ ] Verify morse code is readable (listen on second radio)

### 2. Field Testing
- [ ] Transmit range testing at HIGH power (10W)
- [ ] Transmit range testing at LOW power (5W)
- [ ] Signal quality reports from receivers
- [ ] Battery runtime testing (Pi + Baofeng on power bank)
- [ ] Outdoor deployment test (weatherproofing, mounting)

### 3. Integration Testing
- [ ] 24-hour continuous beacon operation
- [ ] Configuration change testing (live reload)
- [ ] Error recovery (USB disconnect, audio device reset)
- [ ] Error recovery (power loss/restore)
- [ ] Log analysis (missed beacons, timing accuracy)

### 4. Fox Hunt Validation
- [ ] Deploy as actual fox in practice hunt
- [ ] Gather feedback from hunters on signal clarity
- [ ] Validate beacon timing meets hunt requirements
- [ ] Test portability (setup/teardown time)

---

## Hardware Documentation

See detailed hardware setup instructions:
- **docs/mvp-hardware-setup.md** - Complete assembly and configuration guide
- **docs/orders/** - Purchase receipts and part numbers

## Reference Links

- [Baofeng UV-5R VOX Mode Guide](https://www.miklor.com/uv5r/)
- [Raspberry Pi Audio Configuration](https://www.raspberrypi.org/documentation/usage/audio/)
- [BTECH APRS-K1 Cable Documentation](https://baofengtech.com/product/aprs-k1/)
- [UGREEN USB Audio Adapter](https://www.amazon.com/UGREEN-Adapter-Support-Headphone-Compatible/dp/B08Y8CZB2S)

---

## License

*(Same as main project)*
