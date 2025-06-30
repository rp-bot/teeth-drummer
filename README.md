# Teeth Drummer MIDI Controller

A comprehensive MIDI controller system designed specifically for the teeth drumming community. This project consists of three main components that work together to capture teeth drumming gestures and convert them into musical MIDI data.

## What is Teeth Drumming?

Teeth drumming is a unique musical technique where performers use their teeth, jaw, and mouth movements to create rhythmic patterns and beats. This MIDI controller system enables teeth drummers to translate their physical gestures into digital music through Force Sensitive Resistors (FSRs) and real-time MIDI conversion.

## System Architecture

The system consists of three interconnected components:

1. **Wearable Hardware** - Arduino-based sensor system with Force Sensitive Resistors
2. **Desktop Application** - Cross-platform app for serial-to-MIDI conversion
3. **Software Instrument** - Audio plugin for DAW integration

```
┌─────────────────┐    Serial     ┌─────────────────┐    MIDI     ┌─────────────────┐
│   Arduino FSR   │──────────────▶│  Desktop App    │────────────▶│      DAW        │
│    Hardware     │               │  (Tauri/Rust)   │             │   + Plugin      │
└─────────────────┘               └─────────────────┘             └─────────────────┘
```
