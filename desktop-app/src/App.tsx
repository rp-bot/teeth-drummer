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

      {ports.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Port Name</th>
              <th>Type</th>
              <th>Vendor/Product</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {ports.map((port) => (
              <tr key={port.port_name}>
                <td>{port.port_name}</td>
                {port.port_type ? (
                  <>
                    <td>USB</td>
                    <td>{`0x${port.port_type.vid.toString(16)} / 0x${port.port_type.pid.toString(16)}`}</td>
                    <td>
                      {port.port_type.product && <div>Product: {port.port_type.product}</div>}
                      {port.port_type.manufacturer && <div>Mfg: {port.port_type.manufacturer}</div>}
                      {port.port_type.serial_number && <div>S/N: {port.port_type.serial_number}</div>}
                    </td>
                  </>
                ) : (
                  <td colSpan={3}>Non-USB Port</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No serial ports found. Is your Arduino connected?</p>
      )}
    </div>
  );
}

export default App;
