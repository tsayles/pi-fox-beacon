#!/usr/bin/env python3
"""
Audio generation module for MVP beacon.

Provides waveform generation and audio playback via aplay subprocess.
Sounddevice is NOT used — it causes USB transfer timeouts on the Pi
with the AIOC adapter. Use aplay with plughw:AllInOneCable,0 instead.
"""

import io
import subprocess
import wave

import numpy as np


class AudioGenerator:
    """Generate audio waveforms for beacon transmission."""

    def __init__(self, sample_rate=48000, amplitude=0.5):
        """
        Initialize audio generator.

        Args:
            sample_rate: Audio sample rate in Hz
            amplitude: Audio amplitude (0.0 to 1.0)
        """
        self.sample_rate = sample_rate
        self.amplitude = amplitude

    def generate_tone(self, frequency, duration, fade_ms=10):
        """
        Generate a pure tone with fade in/out.

        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
            fade_ms: Fade in/out duration in milliseconds

        Returns:
            numpy float32 array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        tone = (
            self.amplitude * np.sin(2 * np.pi * frequency * t)
        ).astype(np.float32)

        fade_samples = int((fade_ms / 1000.0) * self.sample_rate)
        if fade_samples > 0 and fade_samples < len(tone) // 2:
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return tone

    def generate_silence(self, duration):
        """
        Generate silence (zeros).

        Args:
            duration: Duration in seconds

        Returns:
            numpy float32 array of zero samples
        """
        return np.zeros(
            int(self.sample_rate * duration), dtype=np.float32
        )

    def concatenate_audio(self, *audio_arrays):
        """
        Concatenate multiple audio arrays.

        Args:
            *audio_arrays: Variable number of numpy audio arrays

        Returns:
            Single concatenated numpy array
        """
        return np.concatenate(audio_arrays)

    def to_wav_bytes(self, audio_data):
        """
        Convert numpy float32 audio array to WAV bytes.

        Args:
            audio_data: numpy float32 array (-1.0 to 1.0)

        Returns:
            bytes: WAV file content suitable for piping to aplay
        """
        buf = io.BytesIO()
        samples = (audio_data * 32767).astype(np.int16)
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.sample_rate)
            w.writeframes(samples.tobytes())
        return buf.getvalue()

    def play(self, audio_data, alsa_device='plughw:AllInOneCable,0'):
        """
        Play audio via aplay subprocess.

        Converts audio to WAV and pipes to aplay stdin. This avoids
        sounddevice/PortAudio which causes USB transfer timeouts on
        the Pi with the AIOC adapter.

        Args:
            audio_data: numpy float32 array of audio samples
            alsa_device: ALSA device string
        """
        wav_data = self.to_wav_bytes(audio_data)
        result = subprocess.run(
            ['aplay', '-D', alsa_device, '--buffer-size=48000'],
            input=wav_data,
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f'aplay failed: {result.stderr.decode().strip()}'
            )

    def stop(self):
        """No-op — aplay subprocess stops when play() returns."""
        pass


if __name__ == "__main__":
    print("Testing audio generator via aplay...")
    gen = AudioGenerator(amplitude=0.7)

    tone = gen.generate_tone(700, 1.0)
    silence = gen.generate_silence(0.3)
    audio = gen.concatenate_audio(tone, silence, tone)

    print("Playing 700Hz test tone (2.3s) on AIOC...")
    gen.play(audio)
    print("Done!")
