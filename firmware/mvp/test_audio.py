#!/usr/bin/env python3
"""
Audio device test utility for MVP beacon.

Lists available audio output devices and plays a test tone
to verify USB audio dongle configuration.
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


def play_test_tone(device_index=None, duration=2.0, frequency=1000):
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
    print(f"Sample Rate: {sample_rate} Hz")
    print()
    print("You should hear a tone. If using VOX mode, the radio should key up.")
    print()
    
    # Generate test tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add fade in/out to avoid clicks
    fade_samples = int(0.01 * sample_rate)  # 10ms fade
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


def main():
    """Main test utility."""
    print("=" * 60)
    print("Pi Fox Beacon - Audio Device Test Utility")
    print("=" * 60)
    
    # List all devices
    list_devices()
    
    # Get user choice
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
    
    # Play test tone
    success = play_test_tone(device_index)
    
    if success:
        print()
        print("If you heard the tone and/or the radio keyed up,")
        print("the audio device is working correctly.")
        print()
        print("Next steps:")
        print("  1. Edit config.yaml and set device_index to the working device")
        print("  2. Adjust vox_trigger_level if needed")
        print("  3. Run beacon.py to start the beacon")
    else:
        print()
        print("Audio test failed. Try a different device or check connections.")
    
    print()


if __name__ == "__main__":
    main()
