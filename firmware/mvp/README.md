# MVP Firmware - USB Audio + VOX

This directory contains the MVP firmware for the USB sound interface + VOX mode beacon.

## Hardware Requirements

- **Raspberry Pi 3 Model B+** (or compatible)
- **UGREEN USB Audio Adapter** (24bit/96kHz, TRRS)
- **BTECH APRS-K1 Cable** (Kenwood K1 to 3.5mm TRRS)
- **Baofeng UV-5RX3** (or UV-5R)

See `docs/mvp-hardware-setup.md` for complete assembly instructions.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test audio output (lists all audio devices and plays test tone)
python test_audio.py

# Edit configuration with your callsign
cp config.yaml my-config.yaml
nano my-config.yaml

# Run beacon (once audio is confirmed working)
python beacon.py
```

## Files

- `beacon.py` - Main beacon control script
- `audio_generator.py` - Audio tone and waveform generation
- `morse.py` - Morse code generator
- `config.yaml` - Beacon configuration template
- `requirements.txt` - Python dependencies
- `test_audio.py` - Audio device test utility

## Configuration

Edit `config.yaml` to set:
- Your callsign (required for legal operation)
- Beacon interval (seconds between transmissions)
- Audio device selection (typically auto-detected)
- VOX trigger level (audio amplitude 0.0-1.0)
- Morse code speed (WPM) and frequency
- Message patterns

**Important:** Set your amateur radio callsign before transmitting!

## Hardware Setup

1. **Connect UGREEN USB adapter to Raspberry Pi USB port**
   - Any of the 4 USB-A ports
   - Pi will auto-detect as USB audio device

2. **Connect BTECH APRS-K1 cable:**
   - 3.5mm TRRS plug → UGREEN adapter jack
   - Kenwood K1 connector → Baofeng K-port (side of radio)

3. **Configure Baofeng for VOX mode:**
   - Press MENU, navigate to VOX setting
   - Set VOX level: 5 (range 1-10, start mid-range)
   - Set VOX delay: 1.0s
   - Set frequency and power (HIGH=10W or LOW=5W)

4. **Test with test_audio.py:**
   - Radio should key up when test tone plays
   - Adjust VOX level or `vox_trigger_level` in config if needed

## Troubleshooting

**VOX not triggering:**
- Increase audio volume in config.yaml
- Verify cable connection (tip and ring must make contact)
- Check Baofeng VOX level setting

**Audio device not found:**
- Run `python test_audio.py` to list available devices
- Update device index in config.yaml

**Background PTT triggering:**
- Lower VOX sensitivity on radio
- Reduce beacon audio volume
- Add squelch delay in beacon timing
