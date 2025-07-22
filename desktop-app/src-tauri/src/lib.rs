// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
// Import our new module
mod core;

// Define a new Tauri command that wraps our utility function
#[tauri::command]
fn get_serial_ports() -> Vec<core::serial_utils::PortInfo> {
    core::serial_utils::list_serial_ports()
}

#[tauri::command]
fn start_serial_listener_cmd(app_handle: tauri::AppHandle, port_name: String) {
    core::serial_handler::start_serial_listener(app_handle, port_name);
}

#[tauri::command]
fn stop_serial_listener_cmd() {
    core::serial_handler::stop_serial_listener();
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            get_serial_ports,
            start_serial_listener_cmd,
            stop_serial_listener_cmd
        ])
        .setup(|_app| {
            // Listener is started on demand from frontend
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
