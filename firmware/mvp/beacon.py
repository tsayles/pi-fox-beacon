#!/usr/bin/env python3
"""
Main beacon control script for MVP implementation.

Controls beacon timing, message generation, and audio output
for USB sound interface + VOX mode operation.

Hardware Setup:
- Raspberry Pi 3 B+ (or compatible)
- UGREEN USB Audio Adapter (24bit/96kHz)
- BTECH APRS-K1 cable (Kenwood K1 to 3.5mm TRRS)
- Baofeng UV-5RX3 in VOX mode

The beacon:
1. Generates morse code or tone audio in software (numpy)
2. Outputs audio via ALSA to USB audio device (UGREEN adapter)
3. Audio travels through APRS-K1 cable to Baofeng microphone input
4. Baofeng VOX detects audio and automatically keys PTT
5. Beacon transmits on configured frequency

No GPIO or hardware PTT control required!
"""

import time
import logging
import yaml
import sys
from pathlib import Path
from datetime import datetime, timedelta

from audio_generator import AudioGenerator
from morse import create_morse_audio


class BeaconController:
    """Main beacon controller."""
    
    def __init__(self, config_file="config.yaml"):
        """
        Initialize beacon controller.
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.audio_gen = AudioGenerator(
            sample_rate=self.config['audio']['sample_rate'],
            amplitude=self.config['audio']['vox_trigger_level']
        )
        self.device_index = self.config['audio']['device_index']
        self.running = False
        self.last_id_time = None
        
        self.logger.info("Beacon controller initialized")
        self.logger.info(f"Callsign: {self.config['callsign']}")
        self.logger.info(f"Beacon interval: {self.config['beacon_interval_seconds']}s")
    
    def load_config(self, config_file):
        """Load configuration from YAML file."""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Configure logging."""
        log_config = self.config['logging']
        log_level = getattr(logging, log_config['level'])
        
        handlers = []
        
        if log_config['console']:
            handlers.append(logging.StreamHandler())
        
        if log_config['file']:
            handlers.append(logging.FileHandler(log_config['file']))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=handlers
        )
        
        self.logger = logging.getLogger(__name__)
    
    def generate_message_audio(self):
        """
        Generate audio for beacon message.
        
        Returns:
            numpy array of audio samples
        """
        msg_config = self.config['message']
        msg_type = msg_config['type']
        
        if msg_type == "morse":
            # Substitute callsign into message text
            text = msg_config['text'].format(
                callsign=self.config['callsign']
            )
            
            self.logger.debug(f"Generating morse: {text}")
            
            audio = create_morse_audio(
                text,
                wpm=self.config['morse']['wpm'],
                frequency=self.config['morse']['frequency'],
                sample_rate=self.config['audio']['sample_rate'],
                amplitude=self.config['audio']['vox_trigger_level']
            )
            
        elif msg_type == "tone":
            self.logger.debug("Generating tone")
            audio = self.audio_gen.generate_tone(
                msg_config['tone_frequency'],
                msg_config['tone_duration']
            )
        else:
            self.logger.error(f"Unknown message type: {msg_type}")
            return None
        
        # Add pre/post silence for VOX timing
        pre_silence = self.audio_gen.generate_silence(
            self.config['audio']['pre_audio_silence']
        )
        post_silence = self.audio_gen.generate_silence(
            self.config['audio']['post_audio_silence']
        )
        
        return self.audio_gen.concatenate_audio(pre_silence, audio, post_silence)
    
    def generate_id_audio(self):
        """
        Generate audio for CW identification.
        
        Returns:
            numpy array of audio samples
        """
        text = f"DE {self.config['callsign']}"
        self.logger.debug(f"Generating ID: {text}")
        
        audio = create_morse_audio(
            text,
            wpm=self.config['morse']['wpm'],
            frequency=self.config['morse']['frequency'],
            sample_rate=self.config['audio']['sample_rate'],
            amplitude=self.config['audio']['vox_trigger_level']
        )
        
        # Add pre/post silence
        pre_silence = self.audio_gen.generate_silence(
            self.config['audio']['pre_audio_silence']
        )
        post_silence = self.audio_gen.generate_silence(
            self.config['audio']['post_audio_silence']
        )
        
        return self.audio_gen.concatenate_audio(pre_silence, audio, post_silence)
    
    def needs_identification(self):
        """
        Check if station identification is required.
        
        Returns:
            True if ID is needed (every 10 minutes per FCC rules)
        """
        if self.last_id_time is None:
            return True
        
        id_interval = self.config['identification_interval_seconds']
        elapsed = (datetime.now() - self.last_id_time).total_seconds()
        
        return elapsed >= id_interval
    
    def transmit_beacon(self):
        """Transmit one beacon message."""
        try:
            # Check if we need to send ID
            if self.needs_identification():
                self.logger.info("Transmitting station identification")
                id_audio = self.generate_id_audio()
                if id_audio is not None:
                    self.audio_gen.play(id_audio, self.device_index)
                    self.last_id_time = datetime.now()
                    # Brief pause between ID and message
                    time.sleep(1.0)
            
            # Transmit beacon message
            self.logger.info("Transmitting beacon")
            message_audio = self.generate_message_audio()
            if message_audio is not None:
                self.audio_gen.play(message_audio, self.device_index)
                self.logger.info("Transmission complete")
            else:
                self.logger.error("Failed to generate message audio")
                
        except Exception as e:
            self.logger.error(f"Error during transmission: {e}")
    
    def run(self):
        """Run main beacon loop."""
        self.running = True
        self.logger.info("Starting beacon operation")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while self.running:
                self.transmit_beacon()
                
                # Wait for next beacon interval
                interval = self.config['beacon_interval_seconds']
                self.logger.info(f"Waiting {interval} seconds until next beacon...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop beacon operation."""
        self.running = False
        self.audio_gen.stop()
        self.logger.info("Beacon stopped")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Pi Fox Beacon - MVP Implementation")
    print("USB Audio + VOX Mode")
    print("=" * 60)
    print()
    
    # Check for config file
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("ERROR: config.yaml not found!")
        print("Please create config.yaml before running the beacon.")
        print("See config.yaml.example for template.")
        sys.exit(1)
    
    # Create and run beacon
    beacon = BeaconController()
    beacon.run()


if __name__ == "__main__":
    main()
