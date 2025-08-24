#!/bin/bash

# Teeth Drummer MIDI Bridge Daemon Runner
# This script sets up the correct environment and runs the daemon

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set Python path to include the src directory
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Function to show usage
show_usage() {
    echo "Teeth Drummer MIDI Bridge Daemon"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --list-ports              List available serial ports"
    echo "  --serial-port PORT        Serial port (e.g., /dev/ttyUSB0)"
    echo "  --daemon                  Run as background daemon"
    echo "  --config FILE             Configuration file (default: config.json)"
    echo "  --pid-file FILE           PID file for daemon (default: /tmp/teeth_drummer_bridge.pid)"
    echo "  --log-file FILE           Log file (default: /tmp/teeth_drummer_bridge.log)"
    echo "  --help                    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --list-ports"
    echo "  $0 --serial-port /dev/ttyUSB0"
    echo "  $0 --serial-port /dev/ttyUSB0 --daemon"
    echo ""
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Build the command
CMD="python -m teeth_drummer_bridge"

# Add arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_usage
            exit 0
            ;;
        --list-ports)
            CMD="$CMD --list-ports"
            shift
            ;;
        --serial-port)
            CMD="$CMD --serial-port $2"
            shift 2
            ;;
        --daemon)
            CMD="$CMD --daemon"
            shift
            ;;
        --config)
            CMD="$CMD --config $2"
            shift 2
            ;;
        --pid-file)
            CMD="$CMD --pid-file $2"
            shift 2
            ;;
        --log-file)
            CMD="$CMD --log-file $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run the command
echo "Running: $CMD"
echo "Python path: $PYTHONPATH"
echo ""

exec $CMD
