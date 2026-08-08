# MVP Firmware - USB Audio + VOX

This directory contains the MVP firmware for the USB sound interface + VOX mode beacon.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test audio output
python test_audio.py

# Run beacon (once audio is confirmed working)
python beacon.py
```

## Files

- `beacon.py` - Main beacon control script
- `audio_generator.py` - Audio tone and waveform generation
- `morse.py` - Morse code generator
- `config.yaml` - Beacon configuration (callsign, timing, etc.)
- `requirements.txt` - Python dependencies
- `test_audio.py` - Audio device test utility

## Configuration

Edit `config.yaml` to set:
- Your callsign
- Beacon interval (seconds between transmissions)
- Audio device selection
- VOX trigger level (audio amplitude)
- Message patterns

## Hardware Setup

1. Connect USB audio dongle to Raspberry Pi
2. Connect 3.5mm cable from dongle to Baofeng K-port
3. Configure Baofeng for VOX mode (level 3-5)
4. Set Baofeng to desired frequency and power level

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
