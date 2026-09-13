#!/usr/bin/env python3
"""
Main beacon control script for MVP implementation.

Transmission format (every 15 seconds, synced to system clock):
  1. Multi-tone pattern (~5 s, Byonics MF-15 compatible sweep)
  2. CW identification: DE {callsign}

Hardware:
  - Raspberry Pi 3 B+ / Debian 13 / Python 3.13
  - NA6D AIOC adapter v1.0
  - Baofeng K5PLUS (Kenwood K1 / K-port)

PTT:  ioctl TIOCMBIS (set DTR) + TIOCMBIC (clear RTS)
Audio: subprocess aplay via plughw:AllInOneCable,0
"""

import fcntl
import logging
import os
import struct
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

from audio_generator import AudioGenerator
from morse import create_morse_audio

# ---------------------------------------------------------------------------
# ioctl modem line constants (Linux)
# ---------------------------------------------------------------------------
try:
    import termios
    _TIOCMBIS = termios.TIOCMBIS
    _TIOCMBIC = termios.TIOCMBIC
    _TIOCM_DTR = termios.TIOCM_DTR
    _TIOCM_RTS = termios.TIOCM_RTS
except (ImportError, AttributeError):
    _TIOCMBIS = 0x5416
    _TIOCMBIC = 0x5417
    _TIOCM_DTR = 0x002
    _TIOCM_RTS = 0x004

# ---------------------------------------------------------------------------
# Byonics tone-index → frequency table
# Chromatic scale; index 26 ≈ 700 Hz (standard CW sidetone).
# Index 0 = silence.  Matches MF-15 / MF-PC tone numbering.
# ---------------------------------------------------------------------------
_TONE_TABLE = {
    i: 700.0 * (2 ** ((i - 26) / 12.0)) for i in range(32)
}
_TONE_TABLE[0] = 0.0  # silence


# ---------------------------------------------------------------------------
# PTT context manager
# ---------------------------------------------------------------------------
@contextmanager
def ptt_context(port, ptt_on_delay=0.05, ptt_off_delay=0.05):
    """
    Assert PTT via ioctl TIOCMBIS/TIOCMBIC on the AIOC serial port.

    AIOC v1.0 requires DTR asserted AND RTS cleared simultaneously.
    pyserial s.dtr = True alone does not work — raw ioctl is required.
    """
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    try:
        fcntl.ioctl(fd, _TIOCMBIS, struct.pack('I', _TIOCM_DTR))
        fcntl.ioctl(fd, _TIOCMBIC, struct.pack('I', _TIOCM_RTS))
        time.sleep(ptt_on_delay)
        yield
    finally:
        time.sleep(ptt_off_delay)
        fcntl.ioctl(fd, _TIOCMBIC, struct.pack('I', _TIOCM_DTR))
        fcntl.ioctl(fd, _TIOCMBIS, struct.pack('I', _TIOCM_RTS))
        os.close(fd)


# ---------------------------------------------------------------------------
# Beacon controller
# ---------------------------------------------------------------------------
class BeaconController:
    """Main beacon controller."""

    def __init__(self, config_file="config.yaml"):
        self.config = self.load_config(config_file)
        self.setup_logging()

        audio_cfg = self.config['audio']
        self.audio_gen = AudioGenerator(
            sample_rate=audio_cfg['sample_rate'],
            amplitude=audio_cfg['amplitude']
        )
        self.alsa_device = audio_cfg['alsa_device']

        ptt_cfg = self.config.get('ptt', {})
        self.ptt_enabled = ptt_cfg.get('enabled', False)
        self.ptt_port = ptt_cfg.get('port', '/dev/ttyACM0')
        self.ptt_on_delay = ptt_cfg.get('ptt_on_delay', 0.05)
        self.ptt_off_delay = ptt_cfg.get('ptt_off_delay', 0.05)

        self.running = False

        interval = self.config['beacon_interval_seconds']
        self.logger.info("Beacon controller initialized")
        self.logger.info(f"Callsign: {self.config['callsign']}")
        self.logger.info(
            f"Interval: {interval}s "
            f"(clock-synced :00 :{interval} ...)"
        )
        self.logger.info(
            "PTT: "
            + (f"ioctl DTR ({self.ptt_port})"
               if self.ptt_enabled else "VOX")
        )
        self.logger.info(f"Audio: {self.alsa_device}")

    # ------------------------------------------------------------------
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def setup_logging(self):
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

    # ------------------------------------------------------------------
    # Tone pattern generation (Byonics MF-15 compatible)
    # ------------------------------------------------------------------
    def _generate_tone_pattern(self):
        """
        Generate multi-tone identification pattern from config sequence.

        The sequence string and speed_ms use the same format as the
        Byonics MicroFox MF-15 / MF-PC transmitters.  Tone indices map
        to a chromatic scale with index 26 = 700 Hz.
        """
        tones_cfg = self.config.get('tones', {})
        if not tones_cfg.get('enabled', True):
            return self.audio_gen.generate_silence(0)

        speed_ms = tones_cfg.get('speed_ms', 75)
        seq_str = tones_cfg.get('sequence', '')
        if not seq_str:
            return self.audio_gen.generate_silence(0)

        speed_sec = speed_ms / 1000.0
        sr = self.audio_gen.sample_rate
        n = int(sr * speed_sec)
        amp = self.audio_gen.amplitude
        fade = min(int(0.005 * sr), n // 2)

        chunks = []
        for idx in (int(x.strip()) for x in seq_str.split(',')):
            freq = _TONE_TABLE.get(idx, 0.0)
            if freq == 0.0:
                chunks.append(np.zeros(n, dtype=np.float32))
            else:
                t = np.linspace(0, speed_sec, n, False)
                chunk = (amp * np.sin(2 * np.pi * freq * t)
                         ).astype(np.float32)
                chunk[:fade] *= np.linspace(0, 1, fade)
                chunk[-fade:] *= np.linspace(1, 0, fade)
                chunks.append(chunk)

        return np.concatenate(chunks) if chunks \
            else self.audio_gen.generate_silence(0)

    # ------------------------------------------------------------------
    # CW ID generation
    # ------------------------------------------------------------------
    def _generate_id_audio(self):
        """Generate 'DE {callsign}' CW audio."""
        text = f"DE {self.config['callsign']}"
        self.logger.debug(f"CW ID: {text}")
        return create_morse_audio(
            text,
            wpm=self.config['morse']['wpm'],
            frequency=self.config['morse']['frequency'],
            sample_rate=self.audio_gen.sample_rate,
            amplitude=self.audio_gen.amplitude
        )

    # ------------------------------------------------------------------
    # Transmission
    # ------------------------------------------------------------------
    def _transmit(self, audio):
        """Key PTT, play audio, release PTT."""
        if self.ptt_enabled:
            with ptt_context(
                self.ptt_port,
                self.ptt_on_delay,
                self.ptt_off_delay
            ):
                self.audio_gen.play(audio, self.alsa_device)
        else:
            self.audio_gen.play(audio, self.alsa_device)

    def transmit_beacon(self):
        """
        Transmit one beacon cycle.

        Format:  [tone pattern ~5 s]  [pause]  [DE {callsign} CW]
        """
        try:
            tone_audio = self._generate_tone_pattern()
            pause_sec = self.config.get('message', {}).get(
                'pause_before_cw', 0.3
            )
            pause = self.audio_gen.generate_silence(pause_sec)
            id_audio = self._generate_id_audio()

            audio = self.audio_gen.concatenate_audio(
                tone_audio, pause, id_audio
            )

            dur = len(audio) / self.audio_gen.sample_rate
            self.logger.info(
                f"TX: DE {self.config['callsign']} "
                f"({dur:.1f}s)"
            )
            self._transmit(audio)
            self.logger.info("TX complete")

        except Exception as e:
            self.logger.error(f"Error during transmission: {e}")

    # ------------------------------------------------------------------
    # Clock-synchronised main loop
    # ------------------------------------------------------------------
    def _seconds_until_next_slot(self):
        """
        Return seconds until the next clock-aligned beacon slot.

        Slots land at :00, :15, :30, :45 (or whatever the configured
        interval is).  Never returns less than 0.1 s so we don't
        fire twice on the same boundary.
        """
        interval = self.config['beacon_interval_seconds']
        now = datetime.now()
        elapsed = now.second + now.microsecond / 1_000_000
        wait = interval - (elapsed % interval)
        return wait if wait >= 0.1 else wait + interval

    def run(self):
        """Run beacon loop, firing on clock-aligned boundaries."""
        self.running = True
        interval = self.config['beacon_interval_seconds']
        self.logger.info("Starting beacon — press Ctrl+C to stop")
        self.logger.info(
            f"Next slot in "
            f"{self._seconds_until_next_slot():.1f}s"
        )

        try:
            while self.running:
                wait = self._seconds_until_next_slot()
                time.sleep(wait)
                self.transmit_beacon()
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.logger.info("Beacon stopped")


# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Pi Fox Beacon - MVP")
    print("=" * 60)
    print()
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("ERROR: config.yaml not found!")
        sys.exit(1)
    BeaconController(config_file).run()


if __name__ == "__main__":
    main()
