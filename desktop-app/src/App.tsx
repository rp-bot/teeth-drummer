import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

// Must match the Rust `UsbInfo` struct
interface UsbInfo {
  vid: number;
  pid: number;
  product?: string;
  manufacturer?: string;
  serial_number?: string; // Add the serial number here
}
// Must match the Rust `PortInfo` struct
interface PortInfo {
  port_name: string;
  port_type?: UsbInfo;
}

function App() {
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [selectedPort, setSelectedPort] = useState<string>("");
  const [isListening, setIsListening] = useState(false);

  const refreshPorts = async () => {
    try {
      const portList = await invoke<PortInfo[]>("get_serial_ports");
      setPorts(portList);
    } catch (e) {
      console.error(e);
      setPorts([]);
    }
  };

  useEffect(() => {
    refreshPorts();
  }, []);

  return (
    <div className="container">
      <h1>Arduino MIDI Controller</h1>
      <h2>Available Serial Ports</h2>
      <button onClick={refreshPorts}>Refresh Ports</button>

      {/* Port selection dropdown */}
      <div style={{ margin: "1em 0" }}>
        <select value={selectedPort} onChange={(e) => setSelectedPort(e.target.value)} disabled={isListening}>
          <option value="">Select a port</option>
          {ports.map((port) => (
            <option key={port.port_name} value={port.port_name}>
              {port.port_name}
            </option>
          ))}
        </select>
        <button
          style={{ marginLeft: "1em" }}
          onClick={async () => {
            if (selectedPort) {
              await invoke("start_serial_listener_cmd", { portName: selectedPort });
              setIsListening(true);
            }
          }}
          disabled={!selectedPort || isListening}
        >
          Start Listening
        </button>
        <button
          style={{ marginLeft: "1em" }}
          onClick={async () => {
            await invoke("stop_serial_listener_cmd");
            setIsListening(false);
          }}
          disabled={!isListening}
        >
          Stop Listening
        </button>
      </div>

      {/* Removed the table/list of ports. Optionally, show a message if no ports are found. */}
      {ports.length === 0 && <p>No serial ports found. Is your Arduino connected?</p>}
    </div>
  );
}

export default App;
