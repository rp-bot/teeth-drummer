# Teeth Drummer MIDI Bridge

A daemon that reads sensor data from an Arduino via serial connection and broadcasts it as MIDI messages on a virtual MIDI port for DAWs to receive.

## Features

- **Serial Communication**: Reads JSON-formatted sensor data from Arduino
- **Virtual MIDI Port**: Creates a virtual MIDI port that DAWs can connect to
- **Configurable Mapping**: Customizable MIDI note ranges, channels, and controllers
- **Daemon Mode**: Can run as a background daemon
- **Real-time Processing**: Low-latency conversion from sensor data to MIDI
- **Multiple Sensor Types**: Supports both hit detection and pressure sensors

## Requirements

### System Dependencies

- Python 3.7+
- ALSA MIDI support (for Linux)
- Serial port access

### Python Dependencies

- `pyserial>=3.5` - Serial communication
- `mido>=1.2.10` - MIDI handling
- `python-rtmidi>=1.4.9` - Real-time MIDI
- `daemonize>=2.5.0` - Daemon functionality

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd teeth-drummer-bridge
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   # or
   pip install pyserial mido python-rtmidi daemonize
   ```

3. **Install system dependencies** (Linux):

   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-rtmidi libasound2-dev

   # Arch Linux
   sudo pacman -S python-rtmidi alsa-lib
   ```

## Arduino Setup

### Hardware Requirements

- Arduino board (Uno, Nano, etc.)
- Sensors (piezo, pressure, accelerometer, etc.)
- ArduinoJson library

### Software Setup

1. Install the ArduinoJson library in Arduino IDE
2. Upload the provided `arduino_example.ino` sketch
3. Connect sensors to analog pins A0 and A1

### Expected Data Format

The Arduino should send JSON-formatted data:

```json
{"sensor": 1, "value": 512, "type": "hit"}
{"sensor": 2, "value": 256, "type": "pressure"}
```

- `sensor`: Sensor ID (integer)
- `value`: Sensor reading (0-1023 for analog)
- `type`: Data type ("hit" or "pressure")

## Configuration

Create a `config.json` file to customize the behavior:

```json
{
  "midi_mapping": {
    "note_on_channel": 1,
    "note_off_channel": 1,
    "velocity": 100,
    "note_range": [60, 72],
    "cc_channel": 1,
    "cc_controller": 1
  },
  "serial": {
    "baudrate": 115200,
    "timeout": 1,
    "encoding": "utf-8"
  },
  "midi": {
    "port_name": "TeethDrummer",
    "virtual": true
  }
}
```

### Configuration Options

#### MIDI Mapping

- `note_on_channel`: MIDI channel for note-on messages (1-16)
- `note_off_channel`: MIDI channel for note-off messages (1-16)
- `velocity`: Default velocity for note messages (1-127)
- `note_range`: Range of MIDI notes to use [min, max]
- `cc_channel`: MIDI channel for control change messages (1-16)
- `cc_controller`: MIDI controller number for pressure data (0-127)

#### Serial Settings

- `baudrate`: Serial communication speed
- `timeout`: Serial read timeout in seconds
- `encoding`: Character encoding for serial data

#### MIDI Settings

- `port_name`: Name of the virtual MIDI port
- `virtual`: Whether to create a virtual port (true) or use existing port (false)

## Usage

### Basic Usage

1. **List available serial ports**:

   ```bash
   python -m teeth_drummer_bridge --list-ports
   ```

2. **Run in foreground mode**:

   ```bash
   python -m teeth_drummer_bridge --serial-port /dev/ttyUSB0
   ```

3. **Run as daemon**:
   ```bash
   python -m teeth_drummer_bridge --serial-port /dev/ttyUSB0 --daemon
   ```

### Command Line Options

- `--serial-port, -p`: Serial port (required)
- `--config, -c`: Configuration file path (default: config.json)
- `--daemon, -d`: Run as background daemon
- `--pid-file`: PID file location for daemon (default: /tmp/teeth_drummer_bridge.pid)
- `--log-file`: Log file location (default: /tmp/teeth_drummer_bridge.log)
- `--list-ports`: List available serial ports

### Daemon Management

**Start daemon**:

```bash
python -m teeth_drummer_bridge --serial-port /dev/ttyUSB0 --daemon
```

**Stop daemon**:

```bash
kill $(cat /tmp/teeth_drummer_bridge.pid)
```

**Check daemon status**:

```bash
ps aux | grep teeth_drummer_bridge
```

**View logs**:

```bash
tail -f /tmp/teeth_drummer_bridge.log
```

## DAW Integration

### Supported DAWs

- Ableton Live
- FL Studio
- Logic Pro
- Reaper
- Pro Tools
- Bitwig Studio
- And any other DAW with MIDI input support

### Setup in DAW

1. Start the daemon
2. In your DAW, go to MIDI preferences
3. Look for "TeethDrummer" in the MIDI input list
4. Enable the port for input
5. Create a MIDI track and select "TeethDrummer" as input
6. The sensor data will now trigger MIDI notes and control changes

### MIDI Mapping

- **Hit sensors**: Generate note-on messages with velocity based on impact strength
- **Pressure sensors**: Generate control change messages for continuous control
- **Note range**: Configurable range of MIDI notes (default: C4 to C5)
- **Channels**: Separate channels for different sensor types

## Troubleshooting

### Common Issues

1. **Serial port not found**:

   ```bash
   # Check available ports
   python -m teeth_drummer_bridge --list-ports

   # Check permissions
   sudo usermod -a -G dialout $USER
   ```

2. **MIDI port not appearing**:

   ```bash
   # Check ALSA MIDI
   aconnect -l

   # Install ALSA utilities
   sudo apt-get install alsa-utils
   ```

3. **Permission denied**:

   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER

   # Log out and back in, or run:
   newgrp dialout
   ```

4. **Daemon not starting**:

   ```bash
   # Check logs
   tail -f /tmp/teeth_drummer_bridge.log

   # Check if port is already in use
   lsof /dev/ttyUSB0
   ```

### Debug Mode

Run in foreground with verbose logging:

```bash
python -m teeth_drummer_bridge --serial-port /dev/ttyUSB0 --log-level DEBUG
```

## Development

### Project Structure

```
teeth-drummer-bridge/
├── src/teeth_drummer_bridge/
│   ├── __init__.py
│   ├── __main__.py
│   └── app.py              # Main daemon implementation
├── tests/                  # Test files
├── config.json            # Configuration file
├── arduino_example.ino    # Arduino example sketch
└── README.md              # This file
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Test serial communication
python -m teeth_drummer_bridge --list-ports
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ArduinoJson library for JSON parsing
- mido library for MIDI handling
- python-rtmidi for real-time MIDI support
