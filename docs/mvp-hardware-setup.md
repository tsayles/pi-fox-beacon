# MVP Hardware Setup Guide

Quick reference for assembling and configuring the MVP beacon hardware using the NA6D AIOC adapter.

---

## Bill of Materials

| Item | Part Number | Vendor | Order Date | Status |
|------|------------|--------|------------|--------|
| Raspberry Pi 3 Model B+ | — | SparkFun | 2026-08-08 | Order #430326 |
| NA6D AIOC Adapter | All-In-One Cable (USB-C, Kenwood K1) | na6d.com | TBD | To order |
| Baofeng K5PLUS | 10W tri-band HT (ASIN B0GTDDRGY7) | Amazon | — | On hand |

**AIOC:** Single USB-C device providing USB sound card + hardware PTT + radio programming. Replaces the separate USB audio dongle and BTECH APRS-K1 cable used in the original VOX-only approach.

**Radio Specs:** VHF/1.25m/UHF tri-band, tri-power (10W/7W/4W), 2500mAh battery, 999 channels. Uses Kenwood K1 (2-pin) connector — compatible with AIOC.

---

## Assembly Instructions

### Step 1: Prepare Raspberry Pi

#### Recommended OS Image

**Raspberry Pi OS Lite (64-bit)** — Debian 13 (Trixie), Kernel 6.18

The beacon runs headless (no desktop required). The Lite image keeps
the footprint small and is the right choice for the Pi 3 Model B+.

> **Download page:**
> <https://www.raspberrypi.com/software/operating-systems/>
>
> Under **"Raspberry Pi OS (64-bit)"**, choose **Raspberry Pi OS Lite**.
> Released 18 Jun 2026 · ~501 MB download · ~2.8 GB on SD card.

The easiest way to flash the image is
[Raspberry Pi Imager](https://www.raspberrypi.com/software/), which
lets you preconfigure hostname, SSH, and Wi-Fi credentials before
writing — skip steps 2–3 below if you use it.

1. Flash **Raspberry Pi OS Lite (64-bit)** to a microSD card (8 GB+)

2. **Enable SSH** — create an empty file named `ssh` on the boot
   partition before first boot. Without this file SSH will not start:
   ```bash
   touch /media/$USER/bootfs/ssh
   ```

3. **Configure cloud-init** — edit `user-data` on the boot partition
   to set hostname, user, SSH key, and packages. Minimum
   `user-data` for this project:
   ```yaml
   #cloud-config
   hostname: pi-fox-beacon
   manage_etc_hosts: true
   users:
     - name: tsayles
       groups: adm,dialout,sudo,audio,video,plugdev,users,input,netdev,spi,i2c,gpio
       sudo: ALL=(ALL) NOPASSWD:ALL
       shell: /bin/bash
       ssh_authorized_keys:
         - <your public key from ~/.ssh/id_ed25519.pub>
   packages:
     - openssh-server
     - avahi-daemon
     - git
     - python3-numpy
     - python3-serial
     - python3-yaml
     - alsa-utils
   package_update: true
   runcmd:
     - systemctl enable ssh
     - systemctl start ssh
     - systemctl enable avahi-daemon
     - su - tsayles -c "git clone https://github.com/tsayles/pi-fox-beacon.git /home/tsayles/pi-fox-beacon"
     - cp /home/tsayles/pi-fox-beacon/firmware/mvp/fox-beacon.service /etc/systemd/system/
     - systemctl daemon-reload
     - systemctl enable fox-beacon
   ```
   > **Note:** `openssh-server` must be in the packages list —
   > it is not enabled by default on Raspberry Pi OS Trixie when
   > using cloud-init. The `ssh` empty file alone is not sufficient.

4. Enable DHCP on ethernet — edit `network-config` on the boot
   partition:
   ```yaml
   network:
     version: 2
     ethernets:
       eth0:
         dhcp4: true
         optional: false
   ```

5. Unmount/eject SD card, insert into Pi, and power on.
   First boot takes **3–5 minutes** while cloud-init runs
   (`apt update`, package install, git clone).

6. SSH in once it's up:
   ```bash
   ssh tsayles@pi-fox-beacon.local
   # or by IP if mDNS isn't resolving:
   ssh tsayles@<dhcp-ip>
   ```

### Step 2: Install MVP Firmware

The cloud-init `runcmd` above handles this automatically on first boot.
To do it manually:

1. Clone repository:
   ```bash
   git clone https://github.com/tsayles/pi-fox-beacon.git
   cd pi-fox-beacon
   ```

2. Install Python dependencies:
   ```bash
   cd firmware/mvp
   pip install -r requirements.txt --break-system-packages
   ```

3. Install and enable the systemd service:
   ```bash
   sudo cp firmware/mvp/fox-beacon.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable fox-beacon
   sudo systemctl start fox-beacon
   ```

### Step 3: Connect Hardware

1. **Plug AIOC into Pi USB port**
   - Use a good quality USB-C data cable (not charge-only)
   - Pi should detect two new devices: USB sound card + serial port

2. **Connect AIOC to radio:**
   - Plug the AIOC's Kenwood K1 connector into the radio's K-port (side of radio)

3. **Verify AIOC is detected:**
   ```bash
   lsusb | grep -i aioc   # or look for STM32 device
   aplay -l               # should show AIOC as a sound card
   ls /dev/ttyACM*        # should show /dev/ttyACM0 (or similar)
   ```

4. **Grant serial port access:**
   ```bash
   sudo usermod -aG dialout $USER
   # Log out and back in (or run: newgrp dialout)
   ```

5. **Set radio frequency and power:**
   - Set to desired beacon frequency
   - Set power: HIGH (10W), MID (7W), or LOW (4W)
   - Disable CTCSS/DCS unless required
   - VOX does NOT need to be enabled when using AIOC hardware PTT

### Step 4: Test Audio and PTT

1. Run the test utility:
   ```bash
   python test_audio.py
   ```

2. Select the AIOC audio device when prompted

3. Enter the AIOC serial port for PTT test (e.g. `/dev/ttyACM0`)
   - Radio TX LED should light up during PTT test
   - You should hear the test tone from a nearby receiver

4. If PTT doesn't work:
   - Check `ls /dev/ttyACM*` to confirm port name
   - Verify dialout group membership: `groups $USER`
   - Try `sudo python test_audio.py` as a temporary workaround

### Step 5: Run Beacon

1. Edit `config.yaml`:
   - Set your callsign (required for legal operation)
   - Set `ptt.port` to your AIOC serial port
   - Set beacon interval (15 seconds — clock-synced to :00/:15/:30/:45)

2. Run beacon:
   ```bash
   python beacon.py
   ```

3. Press Ctrl+C to stop

---

## Configuration Tips

### Audio Levels

With hardware PTT, audio level affects FM deviation (audio quality), not PTT reliability:
- **config.yaml:** `audio.amplitude` (0.0 to 1.0)
- Start with `0.7` — adjust down if audio sounds over-deviated

### PTT Timing

```yaml
ptt:
  ptt_on_delay: 0.05   # Time after PTT before audio (radio TX settle)
  ptt_off_delay: 0.05  # Time after audio before PTT release
```

Increase `ptt_on_delay` slightly (e.g. 0.1s) if the first morse element is clipped.

### Morse Code Timing

For readable morse code:
- **WPM:** 15-20 recommended
- **Tone frequency:** 600-800 Hz (standard CW tones)

### Beacon Intervals

**Nominal interval (testing and fox hunting):** 15 seconds, clock-synced
to :00, :15, :30, :45 per the system clock.  
**FCC Identification:** Included in every transmission (`DE {callsign}`
appended after the tone pattern).

---

## Troubleshooting

### AIOC not detected

```bash
# List USB devices
lsusb

# List ALSA sound cards
aplay -l

# Check for serial port
ls /dev/ttyACM* /dev/ttyUSB*
```

If not showing up, try a different USB cable (must be data cable, not charge-only).

### Permission denied on serial port

```bash
sudo usermod -aG dialout $USER
# Then log out and back in
```

### Audio device not found

```bash
# Test USB audio with speaker-test
speaker-test -D plughw:1,0 -c 2 -t sine
```

### PTT asserts but no audio / audio but no PTT

- Run `test_audio.py` to test each function separately
- Check AIOC serial port name: `ls /dev/ttyACM*`
- Verify `ptt.port` in config.yaml matches

### Morse code sounds garbled

- Reduce WPM (slower = clearer)
- Check tone frequency (600-800 Hz optimal)
- Verify audio isn't clipping (reduce `audio.amplitude`)

### Radio keys but no audio

```bash
sudo alsamixer   # Select AIOC device, unmute and set volume to 70-80%
```

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
- Experiment with different PTT timing values
- Add custom messages
- Test with actual fox hunt scenario
- Consider power bank for portable operation

See main MVP documentation for feature roadmap and migration path to full PiTower design.
