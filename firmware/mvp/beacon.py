#!/usr/bin/env python3
"""
Main beacon control script for MVP implementation.

Controls beacon timing, message generation, and audio output
for AIOC (All-In-One Cable) hardware PTT mode.

Hardware Setup:
- Raspberry Pi (any model with USB)
- NA6D AIOC adapter (USB sound card + serial PTT in one device)
- Baofeng UV-5R series radio (Kenwood K1 / K-port)

The beacon:
1. Asserts PTT via AIOC serial port DTR line
2. Waits briefly for radio to key up
3. Generates morse code or tone audio in software (numpy)
4. Outputs audio via ALSA to AIOC USB sound device
5. Releases PTT after audio completes

Fallback (VOX mode):
- Set ptt.enabled: false in config.yaml
- Radio must be configured for VOX mode
"""

import time
import logging
import yaml
import sys
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime

from audio_generator import AudioGenerator
from morse import create_morse_audio


@contextmanager
def ptt_context(port, ptt_on_delay=0.05, ptt_off_delay=0.05):
    """
    Context manager that asserts PTT via serial DTR on enter and releases on exit.

    Args:
        port: Serial port path (e.g. /dev/ttyACM0)
        ptt_on_delay: Seconds to wait after asserting PTT
        ptt_off_delay: Seconds to wait before releasing PTT
    """
    try:
        import serial as _serial
    except ImportError as exc:
        raise ImportError(
            "pyserial is required for hardware PTT. Install with: pip install pyserial"
        ) from exc

    ser = None
    try:
        ser = _serial.Serial(port, timeout=1)
        ser.dtr = True
        time.sleep(ptt_on_delay)
        yield
    finally:
        time.sleep(ptt_off_delay)
        if ser is not None:
            ser.dtr = False
            ser.close()


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
            amplitude=self.config['audio']['amplitude']
        )
        self.device_index = self.config['audio']['device_index']
        self.running = False
        self.last_id_time = None
        
        ptt_cfg = self.config.get('ptt', {})
        self.ptt_enabled = ptt_cfg.get('enabled', False)
        self.ptt_port = ptt_cfg.get('port', '/dev/ttyACM0')
        self.ptt_on_delay = ptt_cfg.get('ptt_on_delay', 0.05)
        self.ptt_off_delay = ptt_cfg.get('ptt_off_delay', 0.05)
        
        self.logger.info("Beacon controller initialized")
        self.logger.info(f"Callsign: {self.config['callsign']}")
        self.logger.info(f"Beacon interval: {self.config['beacon_interval_seconds']}s")
        self.logger.info(
            f"PTT mode: {'hardware DTR (' + self.ptt_port + ')' if self.ptt_enabled else 'VOX (software audio level)'}"
        )
    
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
            text = msg_config['text'].format(callsign=self.config['callsign'])
            self.logger.debug(f"Generating morse: {text}")
            audio = create_morse_audio(
                text,
                wpm=self.config['morse']['wpm'],
                frequency=self.config['morse']['frequency'],
                sample_rate=self.config['audio']['sample_rate'],
                amplitude=self.config['audio']['amplitude']
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
            amplitude=self.config['audio']['amplitude']
        )
        
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
    
    def _transmit(self, audio):
        """
        Key PTT, play audio, and release PTT.

        Uses hardware DTR PTT via AIOC when enabled, otherwise relies
        on the radio's VOX mode to key from the audio signal.

        Args:
            audio: numpy array of audio samples
        """
        if self.ptt_enabled:
            with ptt_context(self.ptt_port, self.ptt_on_delay, self.ptt_off_delay):
                self.audio_gen.play(audio, self.device_index)
        else:
            self.audio_gen.play(audio, self.device_index)

    def transmit_beacon(self):
        """Transmit one beacon message."""
        try:
            if self.needs_identification():
                self.logger.info("Transmitting station identification")
                id_audio = self.generate_id_audio()
                if id_audio is not None:
                    self._transmit(id_audio)
                    self.last_id_time = datetime.now()
                    time.sleep(1.0)
            
            self.logger.info("Transmitting beacon")
            message_audio = self.generate_message_audio()
            if message_audio is not None:
                self._transmit(message_audio)
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
    print("AIOC Hardware PTT Mode")
    print("=" * 60)
    print()
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("ERROR: config.yaml not found!")
        print("Please create config.yaml before running the beacon.")
        print("See config.yaml.example for template.")
        sys.exit(1)
    
    beacon = BeaconController()
    beacon.run()


if __name__ == "__main__":
    main()
