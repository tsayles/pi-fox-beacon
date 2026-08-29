# MVP Quick Reference Card

Quick reference for operating the Pi Fox Beacon MVP with the NA6D AIOC adapter.

---

## Hardware Stack

```
┌─────────────────────────────────┐
│   Baofeng K5PLUS (10W HT)       │  ← Radio (no VOX needed)
│   ASIN: B0GTDDRGY7              │     Tri-band VHF/1.25m/UHF
│   Tri-power: 10W/7W/4W          │     2500mAh, 999 channels
└────────────┬────────────────────┘
             │ K1 connector (2-pin Kenwood, built into AIOC cable)
┌────────────┴────────────────────┐
│   NA6D AIOC Adapter             │  ← USB sound card + hardware PTT
│   (USB-C, open source, STM32)   │     Single cable, no drivers needed
└────────────┬────────────────────┘
             │ USB-C → USB-A cable
┌────────────┴────────────────────┐
│   Raspberry Pi 3 Model B+       │  ← Control computer
│   (1.4GHz quad-core, WiFi)      │
└─────────────────────────────────┘
```

---

## Quick Start Checklist

### Hardware Setup
- [ ] AIOC plugged into Pi USB port (use data cable, not charge-only)
- [ ] AIOC Kenwood K1 connector plugged into radio K-port
- [ ] Radio battery charged
- [ ] Pi powered via 5V/2.5A supply

### Radio Configuration
- [ ] Frequency set (e.g., 146.565 MHz for fox hunting)
- [ ] Power level: HIGH (10W), MID (7W), or LOW (4W)
- [ ] CTCSS/DCS: OFF (unless required)
- [ ] VOX: OFF (hardware PTT used instead)

### Software Setup
- [ ] Pi OS updated: `sudo apt update && sudo apt upgrade`
- [ ] Repository cloned: `git clone https://github.com/tsayles/pi-fox-beacon.git`
- [ ] Dependencies installed: `pip install -r firmware/mvp/requirements.txt`
- [ ] Dialout group: `sudo usermod -aG dialout $USER` (then log out/in)
- [ ] AIOC serial port confirmed: `ls /dev/ttyACM*`
- [ ] Audio and PTT tested: `python firmware/mvp/test_audio.py`
- [ ] Config edited: Set callsign and `ptt.port` in `firmware/mvp/config.yaml`

### Run Beacon
```bash
cd ~/pi-fox-beacon/firmware/mvp
python beacon.py
```

Press **Ctrl+C** to stop.

---

## Configuration Quick Reference

### config.yaml Key Settings

```yaml
callsign: "K7LED"  # ← CHANGE THIS to your callsign (K7LED is M&K Club Call)

beacon_interval_seconds: 60  # Time between transmissions
identification_interval_seconds: 600  # CW ID every 10 min (FCC)

ptt:
  enabled: true
  port: "/dev/ttyACM0"   # ← AIOC serial port (check: ls /dev/ttyACM*)
  ptt_on_delay: 0.05     # Seconds after PTT before audio
  ptt_off_delay: 0.05    # Seconds after audio before PTT release

audio:
  device_index: null  # Auto-detect AIOC sound card
  sample_rate: 48000
  amplitude: 0.7      # Audio level (affects deviation, not TX power)

morse:
  wpm: 20        # Words per minute (15-25 recommended)
  frequency: 700 # CW tone in Hz (600-800 standard)

message:
  type: "morse"  # or "tone"
  text: "FOX DE {callsign}"  # {callsign} auto-substituted
```

---

## PTT Timing Tuning

First morse element clipped:
- Increase `ptt_on_delay` (try 0.1s)

PTT held too long after audio:
- Decrease `ptt_off_delay` (try 0.02s)

---

## Troubleshooting

### "Audio device not found"
```bash
# List all audio devices
python firmware/mvp/test_audio.py

# Or use ALSA tools
aplay -l
```

### "Radio doesn't key up"
1. Check AIOC serial port: `ls /dev/ttyACM*`
2. Verify dialout group: `groups $USER`
3. Update `ptt.port` in config.yaml

### "Permission denied on /dev/ttyACM0"
```bash
sudo usermod -aG dialout $USER
# Then log out and back in
```

### "Morse code sounds garbled"
1. Reduce WPM (try 15)
2. Check tone frequency (700 Hz standard)
3. Reduce `audio.amplitude` if clipping

### "Permission denied" on audio device
```bash
sudo usermod -a -G audio $USER
# Log out and back in
```

---

## Common Commands

### AIOC Device Info
```bash
# List USB devices (verify AIOC present)
lsusb

# List ALSA audio devices
aplay -l

# Check AIOC serial port
ls /dev/ttyACM*

# Test speaker output
speaker-test -D plughw:1,0 -c 2 -t sine -f 700

# Adjust volume
alsamixer
```

### Service Management (if running as service)
```bash
# Status
sudo systemctl status fox-beacon

# Start/Stop
sudo systemctl start fox-beacon
sudo systemctl stop fox-beacon

# View logs
sudo journalctl -u fox-beacon -f
```

### Git Commands
```bash
# Update to latest code
git pull

# View current branch
git branch

# Check for changes
git status
```

---

## Field Deployment Checklist

### Before Hunt
- [ ] Callsign configured correctly
- [ ] Beacon interval appropriate (60-120 seconds)
- [ ] Frequency coordinated with hunt organizer
- [ ] Power level chosen (HIGH for long range, LOW for close-in)
- [ ] Battery/power supply tested (8+ hour runtime)
- [ ] Beacon tested and audible on second radio
- [ ] Weatherproofing if deploying outdoors
- [ ] Mount/positioning decided (high ground preferred)

### During Hunt
- [ ] Monitor beacon operation periodically
- [ ] Check battery/power level
- [ ] Log start time and any issues
- [ ] Be available for emergencies

### After Hunt
- [ ] Stop beacon: Ctrl+C or `systemctl stop fox-beacon`
- [ ] Collect equipment
- [ ] Review logs for reliability: `cat firmware/mvp/beacon.log`
- [ ] Document any issues for future improvement

---

## Important Safety Notes

⚠️ **FCC Compliance:**
- Must identify every 10 minutes (automatic in beacon.py)
- Must hold valid amateur radio license
- Transmit only on authorized frequencies
- Follow power limits for license class

⚠️ **RF Safety:**
- Baofeng K5PLUS: 10W maximum output (HIGH), 7W (MID), 4W (LOW)
- Maintain safe distance from antenna during transmission
- Do not transmit with antenna touching body
- Follow FCC RF exposure guidelines

⚠️ **Battery Safety:**
- Monitor Pi and radio battery levels
- Use appropriate power supply (5V/2.5A for Pi)
- Baofeng: Use genuine BL-5 battery or equivalent
- Don't leave unattended with low battery

---

## Performance Specifications

| Metric | Value |
|--------|-------|
| Radio output power | 10W (HIGH) / 7W (MID) / 4W (LOW) |
| PTT latency | ~50ms (hardware DTR) |
| Audio sample rate | 48 kHz |
| Morse code WPM | 15-25 (configurable) |
| CW tone frequency | 600-800 Hz (configurable) |
| Station ID interval | 10 minutes (FCC compliant) |
| Power consumption | ~3-5W (Pi + radio idle) |
| Estimated runtime | 8-12 hours on 20,000mAh power bank |

---

## Support Resources

- **Hardware Setup:** `docs/mvp-hardware-setup.md`
- **Full Documentation:** `docs/mvp-usb-sound-vox.md`
- **Source Code:** `firmware/mvp/`
- **AIOC Project:** https://github.com/skuep/AIOC
- **GitHub Issues:** https://github.com/tsayles/pi-fox-beacon/issues

---

**Version:** MVP v0.2 (AIOC)  
**Last Updated:** 2026-08-29
