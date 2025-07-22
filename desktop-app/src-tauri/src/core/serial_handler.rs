// src-tauri/src/core/serial_handler.rs

use once_cell::sync::Lazy;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{self, Sender};
use std::sync::Mutex;
use std::{
    io::{self, BufRead, BufReader},
    thread,
};
use tauri::{AppHandle, Emitter};
use midir::{MidiOutput, MidiOutputPort};

// --- New ---
// MIDI note constants for clarity
const MIDI_NOTE_C3: u8 = 60;
const MIDI_NOTE_G3: u8 = 67;

#[derive(Clone, serde::Serialize)]
struct Payload {
    values: Vec<String>,
}

// --- New: Global state management ---
// This struct will hold the sender for our MIDI channel.
// By wrapping it in a Mutex, we can safely access it from multiple threads.
struct MidiThreadState {
    // The Option allows us to store the sender when the thread is running
    // and set it to None when it's stopped.
    midi_channel_sender: Option<Sender<Vec<String>>>,
}

// `Lazy` from once_cell ensures this shared state is initialized only once.
static MIDI_THREAD_STATE: Lazy<Mutex<MidiThreadState>> = Lazy::new(|| {
    Mutex::new(MidiThreadState {
        midi_channel_sender: None,
    })
});

// --- Unchanged: Flag for the serial thread ---
static STOP_FLAG: AtomicBool = AtomicBool::new(false);


// src-tauri/src/core/serial_handler.rs

// --- Replace the old midi_worker function with this new, robust version ---
fn midi_worker(rx: mpsc::Receiver<Vec<String>>) {
    println!("[MIDI Thread] Started.");
    
    // Setup MIDI output
    let midi_out = match MidiOutput::new("TauriMIDIEmitter") {
        Ok(midi_out) => midi_out,
        Err(e) => {
            eprintln!("[MIDI Thread] Error creating MIDI output: {}", e);
            return;
        }
    };
    
    // Find an output port
    let out_ports = midi_out.ports();
    let out_port: &MidiOutputPort = match out_ports.get(0) {
        Some(port) => port,
        None => {
            eprintln!("[MIDI Thread] No MIDI output ports found.");
            return;
        }
    };
    
    println!("[MIDI Thread] Found MIDI Port: {}", midi_out.port_name(out_port).unwrap());
    
    let mut conn = match midi_out.connect(out_port, "tauri-midi-port") {
        Ok(c) => c,
        Err(e) => {
            eprintln!("[MIDI Thread] Error connecting to MIDI port: {}", e);
            return;
        }
    };
    
    // Main loop for the MIDI thread
    for received_values in rx {
        // --- FIX #1: Validate and Clamp the Data ---
        // We parse the value and then clamp it to the valid MIDI range (0-127).
        // .min(127) ensures we never send a value higher than 127.
        let velocity1 = received_values.get(0)
            .and_then(|s| s.parse::<u8>().ok())
            .unwrap_or(0)
            .min(127);
            
        let velocity2 = received_values.get(1)
            .and_then(|s| s.parse::<u8>().ok())
            .unwrap_or(0)
            .min(127);
        
        // --- FIX #2: Handle the Result from conn.send ---
        // Instead of `unwrap()`, we check if an error occurred. This prevents the panic.
        if let Err(e) = conn.send(&[0x90, MIDI_NOTE_C3, velocity1]) {
             eprintln!("[MIDI Thread] Error sending C3 NoteOn: {}", e);
        }
        if let Err(e) = conn.send(&[0x90, MIDI_NOTE_G3, velocity2]) {
             eprintln!("[MIDI Thread] Error sending G3 NoteOn: {}", e);
        }
    }
    
    // Send Note Off messages when the loop finishes. It's also good practice
    // to handle potential errors here, though they are less likely.
    let _ = conn.send(&[0x90, MIDI_NOTE_C3, 0]);
    let _ = conn.send(&[0x90, MIDI_NOTE_G3, 0]);
    
    println!("[MIDI Thread] Channel closed. Shutting down.");
}

// --- Updated: Start function now launches both threads ---
pub fn start_serial_listener(app_handle: AppHandle, port_name: String) {
    STOP_FLAG.store(false, Ordering::SeqCst);
    
    // Create the Multi-Producer, Single-Consumer channel
    let (tx, rx) = mpsc::channel::<Vec<String>>();
    
    // Store the sender in our global state so `stop_serial_listener` can access it
    MIDI_THREAD_STATE.lock().unwrap().midi_channel_sender = Some(tx.clone());
    
    // --- Spawn the new MIDI thread ---
    thread::spawn(move || {
        midi_worker(rx);
    });
    
    // --- Spawn the existing serial thread ---
    thread::spawn(move || {
        println!("[Serial Thread] Started.");
        let baud_rate = 9600;

        match serialport::new(&port_name, baud_rate).open() {
            Ok(port) => {
                println!("[Serial Thread] Successfully opened port '{}'.", port_name);
                let mut reader = BufReader::new(port);
                let mut line_buf = String::new();

                loop {
                    if STOP_FLAG.load(Ordering::SeqCst) {
                        println!("[Serial Thread] Stop flag set. Exiting.");
                        break;
                    }
                    match reader.read_line(&mut line_buf) {
                        Ok(_) => {
                            let line = line_buf.trim_end();
                            if !line.is_empty() {
                                let values: Vec<String> = line.split('\t').map(|s| s.to_string()).collect();

                                // 1. Emit to frontend (fast)
                                app_handle.emit("serial-data", Payload { values: values.clone() }).unwrap();
                                
                                // 2. Send to MIDI thread (also very fast)
                                if let Err(e) = tx.send(values) {
                                     eprintln!("[Serial Thread] Failed to send to MIDI thread, it might have shut down: {}", e);
                                     break; // Exit if the channel is broken
                                }
                            }
                            line_buf.clear();
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
                eprintln!("[Serial Thread] Failed to open port '{}'. Error: {}", port_name, e);
            }
        }
    });
}

// --- Updated: Stop function now shuts down both threads gracefully ---
pub fn stop_serial_listener() {
    // 1. Signal the serial thread to stop its loop
    STOP_FLAG.store(true, Ordering::SeqCst);
    
    // 2. Signal the MIDI thread to stop by dropping the sender
    // We lock the state, take the sender out (leaving `None`), and when it goes
    // out of scope at the end of this line, it's dropped. This closes the channel.
    if let Some(sender) = MIDI_THREAD_STATE.lock().unwrap().midi_channel_sender.take() {
        // Dropping `sender` here is what signals the midi_worker to exit its loop
        println!("[Main] MIDI channel sender dropped. Signaling MIDI thread to stop.");
    }
}