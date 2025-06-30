// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// Import our new module
mod core;

// Define a new Tauri command that wraps our utility function
#[tauri::command]
fn get_serial_ports() -> Vec<core::serial_utils::PortInfo> {
    core::serial_utils::list_serial_ports()
}

fn main() {
    tauri::Builder::default()
        // Register our command so the frontend can call it
        .invoke_handler(tauri::generate_handler![get_serial_ports])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}