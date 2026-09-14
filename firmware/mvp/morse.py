#!/usr/bin/env python3
"""
Morse code generator for MVP beacon.

Converts text to morse code audio using international morse code timing.
"""

import numpy as np
from audio_generator import AudioGenerator


# International Morse Code table
MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', '/': '-..-.',
    ' ': ' ',     # Space between words
}


class MorseGenerator:
    """Generate morse code audio."""
    
    def __init__(self, wpm=20, frequency=700, sample_rate=48000, amplitude=0.5):
        """
        Initialize morse code generator.
        
        Args:
            wpm: Words per minute (PARIS standard)
            frequency: CW tone frequency in Hz
            sample_rate: Audio sample rate
            amplitude: Audio amplitude (0.0 to 1.0)
        """
        self.wpm = wpm
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.amplitude = amplitude
        self.audio_gen = AudioGenerator(sample_rate, amplitude)
        
        # Calculate timing units
        # Standard: PARIS = 50 dot units
        # 1 minute / WPM = time for PARIS
        # Time per dot unit = (60 / WPM) / 50
        self.dot_duration = 1.2 / wpm  # seconds per dot
        self.dash_duration = 3 * self.dot_duration
        self.element_space = self.dot_duration  # Space between dots/dashes
        self.char_space = 3 * self.dot_duration  # Space between characters
        self.word_space = 7 * self.dot_duration  # Space between words
    
    def text_to_morse(self, text):
        """
        Convert text to morse code string.
        
        Args:
            text: Plain text string
            
        Returns:
            String of dots, dashes, and spaces
        """
        text = text.upper()
        morse_chars = []
        
        for char in text:
            if char == ' ':
                morse_chars.append(' ')
            elif char in MORSE_CODE:
                morse_chars.append(MORSE_CODE[char])
            # Skip unknown characters
        
        return ' '.join(morse_chars)
    
    def generate_element(self, element_type):
        """
        Generate audio for a single morse element (dot or dash).
        
        Args:
            element_type: '.' for dot, '-' for dash
            
        Returns:
            numpy array of audio samples
        """
        if element_type == '.':
            duration = self.dot_duration
        elif element_type == '-':
            duration = self.dash_duration
        else:
            return self.audio_gen.generate_silence(0)
        
        # Generate tone with short fade to avoid key clicks
        return self.audio_gen.generate_tone(
            self.frequency,
            duration,
            fade_ms=5
        )
    
    def generate_morse_audio(self, text):
        """
        Generate complete morse code audio from text.
        
        Args:
            text: Plain text to convert to morse
            
        Returns:
            numpy array of complete morse code audio
        """
        morse = self.text_to_morse(text)
        audio_segments = []
        
        prev_was_space = False
        
        for i, symbol in enumerate(morse):
            if symbol == '.':
                audio_segments.append(self.generate_element('.'))
                audio_segments.append(
                    self.audio_gen.generate_silence(self.element_space)
                )
                prev_was_space = False
                
            elif symbol == '-':
                audio_segments.append(self.generate_element('-'))
                audio_segments.append(
                    self.audio_gen.generate_silence(self.element_space)
                )
                prev_was_space = False
                
            elif symbol == ' ':
                if not prev_was_space:
                    # End of character - add character space
                    # (we already have element_space, so add the remainder)
                    additional_space = self.char_space - self.element_space
                    audio_segments.append(
                        self.audio_gen.generate_silence(additional_space)
                    )
                    prev_was_space = True
        
        # Concatenate all segments
        if audio_segments:
            return self.audio_gen.concatenate_audio(*audio_segments)
        else:
            return self.audio_gen.generate_silence(0)


def create_morse_audio(text, wpm=20, frequency=700, sample_rate=48000, amplitude=0.5):
    """
    Convenience function to create morse code audio.
    
    Args:
        text: Text to convert to morse code
        wpm: Words per minute
        frequency: CW tone frequency in Hz
        sample_rate: Audio sample rate
        amplitude: Audio amplitude (0.0 to 1.0)
        
    Returns:
        numpy array of morse code audio
    """
    morse_gen = MorseGenerator(wpm, frequency, sample_rate, amplitude)
    return morse_gen.generate_morse_audio(text)


if __name__ == "__main__":
    # Test morse code generation
    print("Testing morse code generator...")
    
    test_text = "FOX DE N0CALL"
    print(f"Text: {test_text}")
    
    morse_gen = MorseGenerator(wpm=20, frequency=700, amplitude=0.3)
    morse_string = morse_gen.text_to_morse(test_text)
    print(f"Morse: {morse_string}")
    
    audio = morse_gen.generate_morse_audio(test_text)
    print(f"Audio samples: {len(audio)}")
    print(f"Duration: {len(audio) / morse_gen.sample_rate:.2f} seconds")
    
    print("Playing morse code...")
    morse_gen.audio_gen.play(audio)
    print("Done!")
