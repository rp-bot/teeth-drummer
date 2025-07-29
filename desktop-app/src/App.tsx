import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import "./App.css";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

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
  const [serialData, setSerialData] = useState<string[][]>([]); // Each event is a vector of strings

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
    let unlisten: (() => void) | undefined;
    // Listen for serial-data events from backend
    listen<{ values: string[] }>("serial-data", (event) => {
      setSerialData((prev) => [...prev, event.payload.values]);
    }).then((fn) => {
      unlisten = fn;
    });
    return () => {
      if (unlisten) unlisten();
    };
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

      {/* Real-time chart for the first value in serialData */}
      <div style={{ width: "100%", height: 300, marginTop: "2em" }}>
        <ResponsiveContainer>
          <LineChart
            data={serialData.slice(-100).map((values, idx) => ({
              idx,
              value1: Number(values[0]),
              value2: Number(values[1]),
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="idx" hide />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line type="monotone" dataKey="value1" stroke="#8884d8" dot={false} isAnimationActive={false} name="Value 1" />
            <Line type="monotone" dataKey="value2" stroke="#82ca9d" dot={false} isAnimationActive={false} name="Value 2" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default App;
