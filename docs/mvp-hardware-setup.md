# MVP Hardware Setup Guide

Quick reference for assembling and configuring the MVP beacon hardware.

---

## Bill of Materials

| Item | Part Number | Vendor | Order Date | Status |
|------|------------|--------|------------|--------|
| Raspberry Pi 3 Model B+ | — | SparkFun | 2026-08-08 | Order #430326 |
| UGREEN USB Audio Adapter | 24bit/96kHz TRRS | Amazon | 2026-08-08 | Ordered |
| BTECH APRS-K1 Cable | Universal Audio Interface | Amazon | (previous) | On hand |
| Baofeng K5PLUS | 10W tri-band HT (ASIN B0GTDDRGY7) | Amazon | — | On hand |

**Radio Specs:** VHF/1.25m/UHF tri-band, tri-power (10W/7W/4W), VOX capable, 2500mAh battery, 999 channels

**Optional backup:** Digirig Baofeng Cables Set (on hand)

---

## Assembly Instructions

### Step 1: Prepare Raspberry Pi

1. Flash Raspberry Pi OS (Lite or Desktop) to microSD card
2. Enable SSH (create empty `ssh` file in boot partition)
3. Configure WiFi (create `wpa_supplicant.conf` if headless)
4. Insert SD card and power on Pi
5. SSH into Pi and update system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Step 2: Install MVP Firmware

1. Clone repository:
   ```bash
   git clone https://github.com/tsayles/pi-fox-beacon.git
   cd pi-fox-beacon
   git checkout mvp-usb-sound-vox
   ```

2. Install Python dependencies:
   ```bash
   cd firmware/mvp
   pip install -r requirements.txt
   ```

3. Copy and edit configuration:
   ```bash
   cp config.yaml my-config.yaml
   nano my-config.yaml
   # Set your callsign, beacon interval, etc.
   ```

### Step 3: Connect Hardware

1. **Plug UGREEN USB adapter into Pi USB port**
   - Any of the 4 USB-A ports will work
   - Pi should auto-detect as USB audio device

2. **Connect BTECH APRS-K1 cable:**
   - 3.5mm TRRS plug → UGREEN adapter 3.5mm jack
   - Kenwood K1 connector → Baofeng K-port (side of radio)

3. **Configure Baofeng for VOX:**
   - Press MENU
   - Enter `4` (VOX) or navigate to VOX setting
   - Set VOX level: Start with `5` (range 1-10)
   - Set VOX delay: `1.0s` recommended
   - Press MENU to save and exit

4. **Set Baofeng frequency and power:**
   - Set to desired beacon frequency
   - Set power: HIGH (10W), MID (7W), or LOW (4W)
   - Disable CTCSS/DCS unless required

### Step 4: Test Audio Output

1. List audio devices:
   ```bash
   python test_audio.py
   ```

2. Select the UGREEN device (usually shows as "USB Audio Device")

3. Play test tone - radio should key up when tone plays

4. If VOX doesn't trigger:
   - Increase `vox_trigger_level` in config.yaml
   - Increase VOX sensitivity on radio (higher number)
   - Check cable connections

5. If VOX triggers on silence:
   - Decrease VOX sensitivity on radio (lower number)
   - Reduce `vox_trigger_level` in config.yaml

### Step 5: Run Beacon

1. Edit `config.yaml`:
   - Set your callsign (required for legal operation)
   - Set beacon interval (60 seconds recommended for testing)
   - Configure morse code message

2. Run beacon:
   ```bash
   python beacon.py
   ```

3. Press Ctrl+C to stop

---

## Configuration Tips

### Audio Levels

The UGREEN adapter output level is fixed, so adjust VOX trigger via:
- **config.yaml:** `vox_trigger_level` (0.0 to 1.0)
- **Radio:** VOX sensitivity (1-10, higher = more sensitive)

Start conservative:
- `vox_trigger_level: 0.5`
- Radio VOX: `5`

Then adjust up if needed.

### Morse Code Timing

For readable morse code:
- **WPM:** 15-20 recommended (faster = more spectrum efficient)
- **Tone frequency:** 600-800 Hz (standard CW tones)
- **Character spacing:** Use default Farnsworth timing

### Beacon Intervals

**For testing:**
- 30-60 seconds (rapid testing)

**For actual fox hunt:**
- 60-120 seconds (gives hunters time to take bearings)

**FCC Identification:**
- Every 10 minutes (automatic in beacon.py)
- Required for legal operation in USA

---

## Troubleshooting

### Audio device not found
```bash
# List all ALSA devices
aplay -l

# Test USB audio with speaker-test
speaker-test -D plughw:1,0 -c 2 -t sine
```

### VOX not reliable
- Check cable firmly seated in K-port
- Verify APRS-K1 TRRS plug fully inserted in UGREEN jack
- Try different VOX level on radio
- Ensure radio battery is charged (weak battery = unreliable VOX)

### Morse code sounds garbled
- Reduce WPM (slower = clearer)
- Check tone frequency (600-800 Hz optimal)
- Verify audio isn't clipping (reduce vox_trigger_level)

### Radio keys but no audio
- Check audio routing: `sudo alsamixer`, select USB device
- Unmute and set volume to 70-80%
- Verify cable polarity (APRS-K1 may have orientation)

---

## Running as Service (Optional)

To auto-start beacon on boot:

1. Create systemd service:
   ```bash
   sudo nano /etc/systemd/system/fox-beacon.service
   ```

2. Add:
   ```ini
   [Unit]
   Description=Fox Hunt Beacon
   After=network.target sound.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/pi-fox-beacon/firmware/mvp
   ExecStart=/usr/bin/python3 beacon.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fox-beacon
   sudo systemctl start fox-beacon
   ```

4. Check status:
   ```bash
   sudo systemctl status fox-beacon
   ```

---

## Next Steps

Once basic beacon is working:
- Field test transmission range
- Experiment with different VOX levels
- Add custom messages
- Test with actual fox hunt scenario
- Consider power bank for portable operation

See main MVP documentation for feature roadmap and migration path to full PiTower design.
