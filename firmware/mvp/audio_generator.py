#!/usr/bin/env python3
"""
Audio generation module for MVP beacon.

Provides functions for generating tones, morse code audio, and
managing audio output through USB sound interface.
"""

import numpy as np
import sounddevice as sd


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
            numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Generate sine wave
        tone = self.amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in/out to avoid clicks
        fade_samples = int((fade_ms / 1000.0) * self.sample_rate)
        if fade_samples > 0 and fade_samples < len(tone) // 2:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            tone[:fade_samples] *= fade_in
            tone[-fade_samples:] *= fade_out
        
        return tone
    
    def generate_silence(self, duration):
        """
        Generate silence (zeros).
        
        Args:
            duration: Duration in seconds
            
        Returns:
            numpy array of zero samples
        """
        num_samples = int(self.sample_rate * duration)
        return np.zeros(num_samples)
    
    def concatenate_audio(self, *audio_arrays):
        """
        Concatenate multiple audio arrays.
        
        Args:
            *audio_arrays: Variable number of numpy audio arrays
            
        Returns:
            Single concatenated numpy array
        """
        return np.concatenate(audio_arrays)
    
    def play(self, audio_data, device_index=None, blocking=True):
        """
        Play audio data through the specified device.
        
        Args:
            audio_data: numpy array of audio samples
            device_index: Audio device index (None for default)
            blocking: If True, wait for playback to complete
        """
        sd.play(audio_data, self.sample_rate, device=device_index)
        if blocking:
            sd.wait()
    
    def stop(self):
        """Stop any currently playing audio."""
        sd.stop()


def create_morse_audio(text, wpm, frequency, sample_rate=48000, amplitude=0.5):
    """
    Create audio waveform from morse code text.
    
    This is a placeholder that will be implemented in morse.py.
    For now, just returns a simple tone burst.
    
    Args:
        text: Text to convert to morse code
        wpm: Words per minute
        frequency: CW tone frequency in Hz
        sample_rate: Audio sample rate
        amplitude: Audio amplitude (0.0 to 1.0)
        
    Returns:
        numpy array of morse code audio
    """
    # Placeholder implementation
    # TODO: Implement actual morse code generation in morse.py
    gen = AudioGenerator(sample_rate, amplitude)
    tone = gen.generate_tone(frequency, 2.0)  # 2 second tone for now
    return tone


if __name__ == "__main__":
    # Simple test
    print("Testing audio generator...")
    gen = AudioGenerator(amplitude=0.3)
    
    # Generate 1kHz test tone
    tone = gen.generate_tone(1000, 1.0)
    silence = gen.generate_silence(0.5)
    
    # Play tone -> silence -> tone
    audio = gen.concatenate_audio(tone, silence, tone)
    
    print("Playing test audio (2.5 seconds)...")
    gen.play(audio)
    print("Done!")
