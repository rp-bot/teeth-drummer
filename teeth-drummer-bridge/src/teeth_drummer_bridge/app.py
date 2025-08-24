#!/usr/bin/env python3
"""
Teeth Drummer MIDI Bridge Daemon

A daemon that reads sensor data from an Arduino via serial connection
and broadcasts it as MIDI messages on a virtual MIDI port for DAWs to receive.
"""

import argparse
import logging
import signal
import sys
import time
from typing import Optional, Dict, Any
import json
import threading

try:
    import serial
    import mido
    import rtmidi
    from daemonize import Daemonize
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print(
        "Please install required packages: pip install pyserial mido python-rtmidi daemonize"
    )
    sys.exit(1)


class TeethDrummerBridge:
    """Main bridge class that handles serial reading and MIDI broadcasting."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.serial_conn: Optional[serial.Serial] = None
        self.midi_out: Optional[mido.open_output] = None
        self.running = False
        self.logger = logging.getLogger(__name__)

        # MIDI mapping configuration
        self.midi_mapping = config.get(
            "midi_mapping",
            {
                "note_on_channel": 1,
                "note_off_channel": 1,
                "velocity": 100,
                "note_range": (60, 72),  # C4 to C5
                "cc_channel": 1,
                "cc_controller": 1,
            },
        )

        # Serial parsing configuration
        self.serial_config = config.get(
            "serial", {"baudrate": 115200, "timeout": 1, "encoding": "utf-8"}
        )

        # MIDI port configuration
        self.midi_config = config.get(
            "midi", {"port_name": "TeethDrummer", "virtual": True}
        )

    def setup_logging(self, log_file: str = "/tmp/teeth_drummer_bridge.log"):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )

    def setup_serial(self, port: str) -> bool:
        """Initialize serial connection to Arduino."""
        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.serial_config["baudrate"],
                timeout=self.serial_config["timeout"],
            )
            self.logger.info(f"Serial connection established on {port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to open serial port {port}: {e}")
            return False

    def setup_midi(self) -> bool:
        """Initialize MIDI output port."""
        try:
            if self.midi_config["virtual"]:
                # Create virtual MIDI port
                self.midi_out = mido.open_output(
                    self.midi_config["port_name"],
                    virtual=True,
                    client_name="TeethDrummerBridge",
                )
            else:
                # Use existing MIDI port
                available_ports = mido.get_output_names()
                if not available_ports:
                    self.logger.error("No MIDI output ports available")
                    return False

                # Use first available port or specified one
                port_name = self.midi_config.get("port_name", available_ports[0])
                if port_name not in available_ports:
                    port_name = available_ports[0]

                self.midi_out = mido.open_output(port_name)

            self.logger.info(f"MIDI output established: {self.midi_out.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to setup MIDI: {e}")
            return False

    def parse_arduino_data(self, data: str) -> Optional[Dict[str, Any]]:
        """Parse incoming Arduino data and convert to MIDI events."""
        data = data.strip()

        # Try JSON format first
        try:
            parsed = json.loads(data)
            if "sensor" in parsed and "value" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

        # Try simple comma-separated format: sensor_id,value,type
        try:
            parts = data.split(",")
            if len(parts) >= 3:
                return {
                    "sensor": int(parts[0]),
                    "value": int(parts[1]),
                    "type": parts[2],
                }
        except (ValueError, IndexError):
            pass

        self.logger.warning(f"Invalid data format: {data}")
        return None

    def create_midi_message(
        self, sensor_data: Dict[str, Any]
    ) -> Optional[mido.Message]:
        """Create MIDI message from sensor data."""
        try:
            sensor_id = sensor_data["sensor"]
            value = sensor_data["value"]
            data_type = sensor_data.get("type", "hit")

            if data_type == "hit":
                # Create note on/off for hit detection
                note = self.midi_mapping["note_range"][0] + (
                    sensor_id % len(range(*self.midi_mapping["note_range"]))
                )
                velocity = min(127, max(1, value // 8))  # Scale value to velocity

                return mido.Message(
                    "note_on",
                    channel=self.midi_mapping["note_on_channel"] - 1,
                    note=note,
                    velocity=velocity,
                )

            elif data_type == "pressure":
                # Create continuous controller for pressure
                cc_value = min(127, max(0, value // 8))  # Scale value to CC range

                return mido.Message(
                    "control_change",
                    channel=self.midi_mapping["cc_channel"] - 1,
                    control=self.midi_mapping["cc_controller"],
                    value=cc_value,
                )

            else:
                self.logger.warning(f"Unknown data type: {data_type}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating MIDI message: {e}")
            return None

    def send_midi(self, message: mido.Message):
        """Send MIDI message to output port."""
        try:
            if self.midi_out and not self.midi_out.closed:
                self.midi_out.send(message)
                self.logger.debug(f"Sent MIDI: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send MIDI: {e}")

    def read_serial_loop(self):
        """Main loop for reading serial data and converting to MIDI."""
        if not self.serial_conn:
            self.logger.error("Serial connection not established")
            return

        self.logger.info("Starting serial read loop...")

        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline()
                    if line:
                        data = line.decode(self.serial_config["encoding"]).strip()
                        if data:
                            self.logger.debug(f"Received: {data}")

                            # Parse Arduino data
                            sensor_data = self.parse_arduino_data(data)
                            if sensor_data:
                                # Create and send MIDI message
                                midi_msg = self.create_midi_message(sensor_data)
                                if midi_msg:
                                    self.send_midi(midi_msg)

                time.sleep(0.001)  # Small delay to prevent busy waiting

            except serial.SerialException as e:
                self.logger.error(f"Serial error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in read loop: {e}")
                break

        self.logger.info("Serial read loop ended")

    def start(self, serial_port: str):
        """Start the bridge daemon."""
        self.setup_logging()
        self.logger.info("Starting Teeth Drummer MIDI Bridge...")

        # Setup connections
        if not self.setup_serial(serial_port):
            self.logger.error("Failed to setup serial connection")
            return False

        if not self.setup_midi():
            self.logger.error("Failed to setup MIDI connection")
            return False

        self.running = True

        # Start serial reading in a separate thread
        serial_thread = threading.Thread(target=self.read_serial_loop, daemon=True)
        serial_thread.start()

        self.logger.info("Bridge started successfully")

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")

        return True

    def stop(self):
        """Stop the bridge daemon."""
        self.logger.info("Stopping Teeth Drummer MIDI Bridge...")
        self.running = False

        if self.serial_conn:
            self.serial_conn.close()
            self.logger.info("Serial connection closed")

        if self.midi_out and not self.midi_out.closed:
            self.midi_out.close()
            self.logger.info("MIDI connection closed")

        self.logger.info("Bridge stopped")


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default configuration
        return {
            "midi_mapping": {
                "note_on_channel": 1,
                "note_off_channel": 1,
                "velocity": 100,
                "note_range": [60, 72],
                "cc_channel": 1,
                "cc_controller": 1,
            },
            "serial": {"baudrate": 115200, "timeout": 1, "encoding": "utf-8"},
            "midi": {"port_name": "TeethDrummer", "virtual": True},
        }
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    print(f"\nReceived signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Teeth Drummer MIDI Bridge Daemon")
    parser.add_argument("--serial-port", "-p", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument(
        "--config", "-c", default="config.json", help="Configuration file path"
    )
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")
    parser.add_argument(
        "--pid-file",
        default="/tmp/teeth_drummer_bridge.pid",
        help="PID file for daemon",
    )
    parser.add_argument(
        "--log-file",
        default="/tmp/teeth_drummer_bridge.log",
        help="Log file for daemon",
    )
    parser.add_argument(
        "--list-ports", action="store_true", help="List available serial ports"
    )

    args = parser.parse_args()

    # Handle signal interrupts
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.list_ports:
        try:
            import serial.tools.list_ports

            ports = serial.tools.list_ports.comports()
            print("Available serial ports:")
            for port in ports:
                print(f"  {port.device}: {port.description}")
            return
        except ImportError:
            print("pyserial not available for port listing")
            return

    # Check if serial port is provided when not listing ports
    if not args.serial_port:
        parser.error("--serial-port/-p is required when not listing ports")

    # Load configuration
    config = load_config(args.config)

    # Create bridge instance
    bridge = TeethDrummerBridge(config)

    if args.daemon:
        # Run as daemon
        def daemon_main():
            bridge.start(args.serial_port)

        daemon = Daemonize(
            app="teeth_drummer_bridge",
            pid=args.pid_file,
            action=daemon_main,
            foreground=False,
            verbose=True,
        )
        daemon.start()
    else:
        # Run in foreground
        try:
            bridge.start(args.serial_port)
        except KeyboardInterrupt:
            pass
        finally:
            bridge.stop()


if __name__ == "__main__":
    main()
