// src-tauri/src/core/serial_utils.rs

use serde::Serialize; // Used to make our struct passable to the frontend
use serialport::SerialPortType;

#[derive(Debug, Serialize, Clone)]
pub struct UsbInfo {
    vid: u16,
    pid: u16,
    product: Option<String>,
    manufacturer: Option<String>,
    serial_number: Option<String>,
  }

#[derive(Debug, Serialize, Clone)]
pub struct PortInfo {
    port_name: String,
    port_type: Option<UsbInfo>,
}

// This function will be exposed to the frontend as a Tauri command.
// It doesn't need #[tauri::command] here because we'll wrap it in main.rs.

pub fn list_serial_ports() -> Vec<PortInfo> {
    let available_ports = serialport::available_ports().unwrap_or_else(|_| {
        eprintln!("Error finding serial ports.");
        vec![]
    });

    let ports: Vec<PortInfo> = available_ports
        .into_iter()
        .map(|port| {
            let port_name = port.port_name.clone();

            let port_type = match port.port_type {
                SerialPortType::UsbPort(info) => Some(UsbInfo {
                    vid: info.vid,
                    pid: info.pid,
                    product: info.product,
                    manufacturer: info.manufacturer,
                    serial_number: info.serial_number, // Extract the serial number 
                }),
                _ => None,
            };

            PortInfo {
                port_name,
                port_type,
            }
        })
        .collect();

    ports
}