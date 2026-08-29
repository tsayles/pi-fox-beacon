#!/usr/bin/env python3
"""
Audio device and PTT test utility for MVP beacon.

Tests the NA6D AIOC adapter: USB audio output and hardware PTT via serial DTR.

Hardware Setup:
- Raspberry Pi (any model with USB)
- NA6D AIOC adapter plugged into USB port
- Radio connected to AIOC via Kenwood K1 cable

This script:
1. Lists all available audio output devices
2. Lists available serial ports (for AIOC PTT)
3. Plays a test tone through selected audio device
4. Optionally tests hardware PTT via AIOC serial port DTR
"""

import sounddevice as sd
import numpy as np
import sys


def list_devices():
    """List all available audio devices."""
    print("\n=== Available Audio Devices ===\n")
    devices = sd.query_devices()
    
    for idx, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            default_marker = " (DEFAULT)" if idx == sd.default.device[1] else ""
            print(f"[{idx}] {device['name']}{default_marker}")
            print(f"    Channels: {device['max_output_channels']} output")
            print(f"    Sample Rate: {device['default_samplerate']} Hz")
            print()


def list_serial_ports():
    """List available serial ports (potential AIOC ports)."""
    import glob
    print("\n=== Available Serial Ports (AIOC candidates) ===\n")
    ports = sorted(glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'))
    if ports:
        for p in ports:
            print(f"  {p}")
    else:
        print("  (none found)")
    print()


def play_test_tone(device_index=None, duration=2.0, frequency=700):
    """
    Play a test tone to verify audio output.
    
    Args:
        device_index: Audio device index (None for default)
        duration: Tone duration in seconds
        frequency: Tone frequency in Hz
    """
    sample_rate = 48000
    
    print(f"\n=== Playing Test Tone ===")
    print(f"Device: {device_index if device_index is not None else 'Default'}")
    print(f"Frequency: {frequency} Hz")
    print(f"Duration: {duration} seconds")
    print()
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.7 * np.sin(2 * np.pi * frequency * t)
    
    fade_samples = int(0.01 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    tone[:fade_samples] *= fade_in
    tone[-fade_samples:] *= fade_out
    
    try:
        sd.play(tone, sample_rate, device=device_index)
        sd.wait()
        print("✓ Test tone completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error playing test tone: {e}")
        return False


def test_ptt(port, duration=2.0):
    """
    Test hardware PTT via AIOC serial port DTR.

    Args:
        port: Serial port path (e.g. /dev/ttyACM0)
        duration: Seconds to hold PTT
    """
    try:
        import serial
    except ImportError:
        print("✗ pyserial not installed. Run: pip install pyserial")
        return False

    print(f"\n=== Testing Hardware PTT ===")
    print(f"Port: {port}")
    print(f"PTT ON for {duration} seconds — radio TX LED should light up")
    print()

    try:
        ser = serial.Serial(port, timeout=1)
        ser.dtr = True
        print("✓ PTT asserted (DTR=True)")
        import time
        time.sleep(duration)
        ser.dtr = False
        ser.close()
        print("✓ PTT released (DTR=False)")
        return True
    except Exception as e:
        print(f"✗ PTT test failed: {e}")
        return False


def main():
    """Main test utility."""
    print("=" * 60)
    print("Pi Fox Beacon - AIOC Test Utility")
    print("=" * 60)
    
    list_devices()
    list_serial_ports()
    
    # Audio device test
    print("=" * 60)
    print("Select an audio device to test:")
    print("  - Enter device number [0-N] to test specific device")
    print("  - Press ENTER to test default device")
    print("  - Type 'q' to quit")
    print()
    
    choice = input("Your choice: ").strip()
    
    if choice.lower() == 'q':
        print("Exiting.")
        return
    
    device_index = None
    if choice:
        try:
            device_index = int(choice)
        except ValueError:
            print(f"Invalid device index: {choice}")
            sys.exit(1)
    
    audio_ok = play_test_tone(device_index)
    
    # PTT test
    print()
    print("=" * 60)
    print("Test hardware PTT via AIOC? (requires AIOC connected)")
    ptt_choice = input("Enter serial port (e.g. /dev/ttyACM0) or press ENTER to skip: ").strip()
    
    if ptt_choice:
        ptt_ok = test_ptt(ptt_choice)
    else:
        ptt_ok = None
        print("Skipping PTT test.")
    
    # Summary
    print()
    print("=" * 60)
    print("Results:")
    if audio_ok:
        print("  ✓ Audio output: OK")
    else:
        print("  ✗ Audio output: FAILED")
        print("    - Verify AIOC is plugged in (lsusb)")
        print("    - Check: pip install sounddevice")
        print("    - Try: aplay -l")

    if ptt_ok is True:
        print("  ✓ Hardware PTT: OK")
        print()
        print("Next steps:")
        print("  1. Edit config.yaml — set your callsign and ptt.port")
        print("  2. Run: python beacon.py")
    elif ptt_ok is False:
        print("  ✗ Hardware PTT: FAILED")
        print("    - Check serial port with: ls /dev/ttyACM*")
        print("    - Verify user is in dialout group: sudo usermod -aG dialout $USER")
    else:
        print()
        print("Next steps:")
        print("  1. Edit config.yaml — set your callsign")
        print("  2. Set ptt.port to your AIOC serial port (e.g. /dev/ttyACM0)")
        print("  3. Run: python beacon.py")
    print()


if __name__ == "__main__":
    main()
