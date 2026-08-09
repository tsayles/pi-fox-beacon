# MVP Quick Reference Card

Quick reference for operating the Pi Fox Beacon MVP.

---

## Hardware Stack

```
┌─────────────────────────────────┐
│   Baofeng UV-5RX3 (5W HT)       │  ← Radio in VOX mode
│   ASIN: B01J2W4JUI              │     Tri-band VHF/1.25m/UHF
└────────────┬────────────────────┘
             │ K1 connector (2-pin Kenwood)
┌────────────┴────────────────────┐
│   BTECH APRS-K1 Cable           │  ← Audio interface cable
└────────────┬────────────────────┘
             │ 3.5mm TRRS plug
┌────────────┴────────────────────┐
│   UGREEN USB Audio Adapter      │  ← 24bit/96kHz DAC
│   (9.8" cable, nylon braided)   │
└────────────┬────────────────────┘
             │ USB-A connector
┌────────────┴────────────────────┐
│   Raspberry Pi 3 Model B+       │  ← Control computer
│   (1.4GHz quad-core, WiFi)      │
└─────────────────────────────────┘
```

---

## Quick Start Checklist

### Hardware Setup
- [ ] UGREEN adapter plugged into Pi USB port
- [ ] BTECH APRS-K1 cable: TRRS → UGREEN, K1 → Baofeng
- [ ] Baofeng battery charged
- [ ] Pi powered via 5V/2.5A supply

### Baofeng Configuration
- [ ] Frequency set (e.g., 146.565 MHz for fox hunting)
- [ ] Power level: HIGH (5W) or LOW (1W)
- [ ] VOX enabled: Level 5 (Menu → VOX)
- [ ] VOX delay: 1.0 seconds
- [ ] CTCSS/DCS: OFF (unless required)

### Software Setup
- [ ] Pi OS updated: `sudo apt update && sudo apt upgrade`
- [ ] Repository cloned: `git clone https://github.com/tsayles/pi-fox-beacon.git`
- [ ] Branch checked out: `git checkout mvp-usb-sound-vox`
- [ ] Dependencies installed: `pip install -r firmware/mvp/requirements.txt`
- [ ] Audio tested: `python firmware/mvp/test_audio.py`
- [ ] Config edited: Set callsign in `firmware/mvp/config.yaml`

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

audio:
  device_index: null  # Auto-detect UGREEN adapter
  sample_rate: 48000  # Standard for UGREEN (supports up to 96kHz)
  vox_trigger_level: 0.6  # 0.0-1.0, tune with radio VOX level
  
morse:
  wpm: 20  # Words per minute (15-25 recommended)
  frequency: 700  # CW tone in Hz (600-800 standard)

message:
  type: "morse"  # or "tone"
  text: "FOX DE {callsign}"  # {callsign} auto-substituted
```

---

## Tuning VOX Sensitivity

VOX too sensitive (false triggers):
- **Radio:** Decrease VOX level (try 3-4)
- **Config:** Decrease `vox_trigger_level` (try 0.4-0.5)

VOX not sensitive enough (doesn't key):
- **Radio:** Increase VOX level (try 6-7)
- **Config:** Increase `vox_trigger_level` (try 0.7-0.8)

**Goal:** Clean trigger on beacon, no false triggers on silence.

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
1. Check BTECH cable seated in both UGREEN and Baofeng K-port
2. Verify Baofeng VOX is ON (Menu → VOX → Level 5)
3. Check Baofeng battery charge
4. Increase vox_trigger_level in config.yaml
5. Increase VOX level on radio

### "Morse code sounds garbled"
1. Reduce WPM (try 15)
2. Check tone frequency (700 Hz standard)
3. Reduce vox_trigger_level if clipping

### "Permission denied" on audio device
```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Log out and back in for group change to take effect
```

---

## Common Commands

### Audio Device Info
```bash
# List USB devices (verify UGREEN present)
lsusb

# List ALSA audio devices
aplay -l

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
git pull origin mvp-usb-sound-vox

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
- Baofeng UV-5RX3: 5W maximum output (HIGH), 1W (LOW)
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
| Radio output power | 5W (HIGH) / 1W (LOW) |
| Beacon TX latency | ~100-500ms (VOX dependent) |
| VOX preamble | 300ms (configurable) |
| Audio sample rate | 48 kHz (24bit DAC) |
| Morse code WPM | 15-25 (configurable) |
| CW tone frequency | 600-800 Hz (configurable) |
| Station ID interval | 10 minutes (FCC compliant) |
| Power consumption | ~3-4W (Pi + radio idle) |
| Estimated runtime | 8-12 hours on 20,000mAh power bank |

---

## Support Resources

- **Hardware Setup:** `docs/mvp-hardware-setup.md`
- **Full Documentation:** `docs/mvp-usb-sound-vox.md`
- **Source Code:** `firmware/mvp/`
- **GitHub Issues:** https://github.com/tsayles/pi-fox-beacon/issues
- **Pull Request:** https://github.com/tsayles/pi-fox-beacon/pull/3

---

**Version:** MVP v0.1  
**Last Updated:** 2026-08-08
