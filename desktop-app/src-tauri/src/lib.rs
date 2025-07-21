// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
// Import our new module
mod core;
mod serial_handler;

// Define a new Tauri command that wraps our utility function
#[tauri::command]
fn get_serial_ports() -> Vec<core::serial_utils::PortInfo> {
    core::serial_utils::list_serial_ports()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![get_serial_ports])
        .setup(|app| {
            // Call the function from our new module to start the listener
            serial_handler::start_serial_listener(app.handle().clone());
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
