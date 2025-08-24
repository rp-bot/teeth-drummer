#!/usr/bin/env python3
"""
Test script to verify Teeth Drummer MIDI Bridge setup
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    required_modules = [
        'serial',
        'mido', 
        'rtmidi',
        'daemonize'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_serial_ports():
    """Test if serial ports can be listed."""
    print("\nTesting serial port access...")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            print("Available serial ports:")
            for port in ports:
                print(f"  {port.device}: {port.description}")
        else:
            print("No serial ports found")
        return True
    except Exception as e:
        print(f"✗ Serial port test failed: {e}")
        return False

def test_midi():
    """Test if MIDI functionality works."""
    print("\nTesting MIDI functionality...")
    try:
        import mido
        ports = mido.get_output_names()
        print(f"Available MIDI output ports: {ports}")
        
        # Test virtual port creation
        try:
            test_port = mido.open_output('TestPort', virtual=True, client_name='TestClient')
            test_port.close()
            print("✓ Virtual MIDI port creation works")
            return True
        except Exception as e:
            print(f"✗ Virtual MIDI port creation failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ MIDI test failed: {e}")
        return False

def test_bridge_import():
    """Test if the bridge module can be imported."""
    print("\nTesting bridge module import...")
    try:
        from teeth_drummer_bridge.app import TeethDrummerBridge
        print("✓ Bridge module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Bridge module import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Teeth Drummer MIDI Bridge Setup Test")
    print("=" * 40)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test serial ports
    serial_ok = test_serial_ports()
    
    # Test MIDI
    midi_ok = test_midi()
    
    # Test bridge module
    bridge_ok = test_bridge_import()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    
    if not failed_imports and serial_ok and midi_ok and bridge_ok:
        print("✓ All tests passed! The system is ready to run the daemon.")
        print("\nNext steps:")
        print("1. Connect your Arduino")
        print("2. Upload the arduino_example.ino sketch")
        print("3. Run: python -m teeth_drummer_bridge --list-ports")
        print("4. Start the daemon: python -m teeth_drummer_bridge --serial-port /dev/ttyUSB0")
        return 0
    else:
        print("✗ Some tests failed:")
        if failed_imports:
            print(f"  - Missing modules: {', '.join(failed_imports)}")
            print("    Run: pip install -r requirements.txt")
        if not serial_ok:
            print("  - Serial port access issues")
            print("    Check permissions: sudo usermod -a -G dialout $USER")
        if not midi_ok:
            print("  - MIDI functionality issues")
            print("    Install ALSA: sudo apt-get install alsa-utils")
        if not bridge_ok:
            print("  - Bridge module import issues")
            print("    Check PYTHONPATH and module structure")
        return 1

if __name__ == '__main__':
    sys.exit(main())
