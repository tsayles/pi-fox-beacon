# MVP Firmware - AIOC Hardware PTT

This directory contains the MVP firmware for the NA6D AIOC (All-In-One Cable) hardware PTT beacon.

## Hardware Requirements

- **Raspberry Pi** (any model with USB)
- **NA6D AIOC adapter** (USB-C, Kenwood K1 cable, provides USB audio + serial PTT)
- **Baofeng UV-5R series radio** (Kenwood K1 / K-port compatible)

See `docs/mvp-hardware-setup.md` for complete assembly instructions.

## Quick Start

```bash
# Install dependencies (includes pyserial for AIOC PTT)
pip install -r requirements.txt

# Grant serial port access (Linux)
sudo usermod -aG dialout $USER   # Log out and back in after this

# Test AIOC audio output and hardware PTT
python test_audio.py

# Edit configuration with your callsign and AIOC serial port
cp config.yaml my-config.yaml
nano my-config.yaml

# Run beacon
python beacon.py
```

## Files

- `beacon.py` - Main beacon control script (hardware PTT via AIOC)
- `audio_generator.py` - Audio tone and waveform generation
- `morse.py` - Morse code generator
- `config.yaml` - Beacon configuration template
- `requirements.txt` - Python dependencies
- `test_audio.py` - AIOC audio and PTT test utility

## Configuration

Edit `config.yaml` to set:
- Your callsign (required for legal operation)
- `ptt.port` — AIOC serial port (e.g. `/dev/ttyACM0`)
- Beacon interval (seconds between transmissions)
- Audio device selection (typically auto-detected)
- Morse code speed (WPM) and frequency
- Message patterns

**Important:** Set your amateur radio callsign before transmitting!

## Hardware Setup

1. **Plug AIOC into Raspberry Pi USB port**
   - Use a USB-C data cable (not charge-only)
   - Pi detects two devices: USB sound card + serial port

2. **Connect AIOC Kenwood K1 connector to radio K-port**

3. **Find the AIOC serial port:**
   ```bash
   ls /dev/ttyACM*
   ```

4. **Set radio frequency and power** (VOX does NOT need to be enabled)

5. **Test with test_audio.py:**
   - Select AIOC audio device and verify tone plays
   - Enter serial port to test hardware PTT (radio TX LED should light)

## Troubleshooting

**PTT not working:**
- Check serial port: `ls /dev/ttyACM*`
- Verify dialout group: `groups $USER`
- Update `ptt.port` in config.yaml

**Audio device not found:**
- Run `python test_audio.py` to list available devices
- Check `lsusb` to confirm AIOC is detected
- Update `audio.device_index` in config.yaml if needed

**First morse element clipped:**
- Increase `ptt.ptt_on_delay` in config.yaml (try 0.1s)
