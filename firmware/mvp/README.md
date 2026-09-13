# MVP Firmware - AIOC Hardware PTT

This directory contains the MVP firmware for the NA6D AIOC (All-In-One
Cable) hardware PTT beacon.

## Verified Hardware Setup

Bench-tested and confirmed working as of 2026-09-13:

| Component | Details |
|-----------|---------|
| Raspberry Pi 3 Model B+ | Debian 13 (trixie), Python 3.13.5 |
| NA6D AIOC adapter **v1.0** | USB: `1209:7388`, Serial: `/dev/ttyACM0` |
| ALSA audio device | `plughw:AllInOneCable,0` (card 1 on Pi) |
| USB-C cable | Must be a **data cable** — charge-only will not work |
| Radio | Baofeng K5PLUS (Kenwood K1 / K-port) |
| Power supply | 5V/3A — undervoltage prevents USB detection |

---

## Critical Hardware Notes

### PTT method: ioctl TIOCMBIS/TIOCMBIC (not pyserial dtr)

AIOC v1.0 PTT requires **both** conditions simultaneously:
- DTR **asserted** (TIOCMBIS)
- RTS **cleared** (TIOCMBIC)

Setting `serial.dtr = True` via pyserial alone does **not** work. The
beacon uses raw `fcntl.ioctl` calls, matching the open-source
[aioc-ptt](https://github.com/0xAF/AIOC-PTT) C tool.

### Audio: aplay subprocess (not sounddevice)

sounddevice/PortAudio causes USB isochronous transfer timeouts on the
Pi 3 B+ with the AIOC. Audio is played via:

```
aplay -D plughw:AllInOneCable,0
```

### udev rule for hidraw access

A permanent udev rule is installed at:
`/etc/udev/rules.d/99-aioc.rules`

This grants `plugdev` group access to `/dev/hidraw0`. The rule was
needed for CM108 HID testing but is not required for normal beacon
operation (which uses the serial PTT method).

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Verify AIOC is detected
lsusb | grep 1209          # USB device 1209:7388
ls /dev/ttyACM*            # serial PTT port
aplay -l | grep AllInOne   # ALSA sound card

# Test audio + PTT manually (aioc-ptt tool)
/tmp/AIOC-PTT/aioc-ptt /dev/ttyACM0 \
  'aplay -D plughw:AllInOneCable,0 /tmp/cw_id.wav'

# Run beacon
cd ~/pi-fox-beacon/firmware/mvp
python3 beacon.py
```

---

## Files

| File | Description |
|------|-------------|
| `beacon.py` | Main controller — ioctl PTT + aplay audio |
| `audio_generator.py` | Waveform generation + aplay playback |
| `morse.py` | Morse code generator |
| `config.yaml` | Beacon configuration |
| `requirements.txt` | Python dependencies |
| `test_audio.py` | AIOC test utility |

---

## Configuration

Key settings in `config.yaml`:

```yaml
callsign: KE4HET

ptt:
  enabled: true
  port: /dev/ttyACM0    # AIOC serial port
  ptt_on_delay: 0.05
  ptt_off_delay: 0.05

audio:
  alsa_device: plughw:AllInOneCable,0
  amplitude: 0.7
```

---

## Troubleshooting

**AIOC not detected (no `1209:7388` in lsusb):**
- Swap the USB-C cable — most likely charge-only
- Try a different USB-A port on the Pi
- Check `vcgencmd get_throttled` — must be `0x0`

**PTT not working:**
- Do NOT use pyserial `s.dtr = True` — use ioctl (see beacon.py)
- Test manually: `/tmp/AIOC-PTT/aioc-ptt /dev/ttyACM0 'sleep 3'`
- Verify K1 connector fully seated in radio K-port (both plugs)

**No audio / aplay errors:**
- Confirm: `aplay -l | grep AllInOne`
- Test: `speaker-test -D plughw:AllInOneCable,0 -c 1 -t sine -f 700 -l 1`
- Do NOT use sounddevice — it causes USB timeouts on the Pi 3 B+

**First morse element clipped:**
- Increase `ptt.ptt_on_delay` in config.yaml (try 0.1)
