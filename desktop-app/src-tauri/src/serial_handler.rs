use std::{
    io::{self, BufRead, BufReader},
    thread,
    time::Duration,
};
use tauri::{AppHandle, Emitter, Manager};

// UPDATE: The payload now contains a Vector of Strings
#[derive(Clone, serde::Serialize)]
struct Payload {
    values: Vec<String>,
}

pub fn start_serial_listener(app_handle: AppHandle) {
    thread::spawn(move || {
        println!("[Serial Thread] Started.");

        let port_name = "/dev/ttyUSB0";
        let baud_rate = 9600;

        match serialport::new(port_name, baud_rate).open() {
            Ok(port) => {
                println!("[Serial Thread] Successfully opened port '{}'.", port_name);

                let mut reader = BufReader::new(port);
                let mut line_buf = String::new();

                loop {
                    match reader.read_line(&mut line_buf) {
                        Ok(_) => {
                            let line = line_buf.trim_end(); // Get the line without the trailing newline

                            if !line.is_empty() {
                                // ---- NEW LOGIC HERE ----
                                // Split the line by the tab character '\t'
                                // and collect the parts into a Vec<String>
                                let values: Vec<String> =
                                    line.split('\t').map(|s| s.to_string()).collect();

                                println!("[Serial Thread] Parsed values: {:?}", values);

                                // Emit the vector of values in our payload
                                app_handle.emit("serial-data", Payload { values }).unwrap();
                            }

                            line_buf.clear(); // Clear the buffer for the next line
                        }
                        Err(ref e) if e.kind() == io::ErrorKind::TimedOut => (),
                        Err(e) => {
                            eprintln!("[Serial Thread] Error reading line: {:?}", e);
                            break;
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!(
                    "[Serial Thread] Failed to open port '{}'. Error: {}",
                    port_name, e
                );
            }
        }
    });
}
