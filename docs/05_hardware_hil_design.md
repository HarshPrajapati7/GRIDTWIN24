# Hardware-in-the-loop (HIL) demonstrator

## Purpose

Build a small, physical, 12 V DC energy bench. It is intended to demonstrate that the software can receive telemetry, evaluate a dispatch scenario, request a guarded low-voltage load-state change and verify the result using measured current and voltage after the circuit is assembled and validated. It is not a complete microgrid: the first version has a DC supply and switched loads, not a real PV inverter, grid connection or battery power stage.

It does **not** emulate the dynamic behaviour of a real utility grid, validate grid-scale power electronics, or connect to household mains.

## Recommended demonstrator

- One 12 V DC bus powered by a current-limited, enclosed, certified DC adapter.
- Three separate 12 V DC load branches: LED strip/module, small DC fan and another low-power resistive/LED load.
- One 3-channel INA3221 current/voltage monitor; its bus-voltage range is 0–26 V. Current capability is determined by the exact breakout's shunts, thermal design and wiring, not by the 26 V voltage rating alone.
- Three 3.3 V-logic-compatible MOSFET driver modules to switch each DC load.
- ESP32 development board publishes telemetry over Wi-Fi/MQTT.
- Inline fuse for each load branch, correctly rated wire and terminal blocks.
- Physical normally-closed emergency-stop loop that interrupts the 12 V load supply.
- Separate physical ARM switch wired in series with the gate-drive signals and also sensed by the MCU; software commands are ignored unless the interlocks are satisfied. Fit an external gate-to-source pulldown resistor (for example 100 kΩ, subject to the MOSFET driver design) on every channel so outputs stay OFF while the ESP32 pins are high-impedance.

## Optional visual upgrade

A small solar panel, compatible charge controller and protected low-voltage battery can be added only if time, supervision and correctly rated protection hardware are available. For the first prototype, a current-limited DC supply plus a simulated PV/battery profile is safer and more repeatable.

## Bill of materials

| Item | Qty | Purpose | Selection note |
|---|---:|---|---|
| ESP32 DevKit | 1 | Telemetry and command gateway | Use a supported board with Wi-Fi |
| INA3221 breakout | 1 | Three-channel DC current/voltage sensing | Check exact shunt values and continuous current ratings |
| 12 V DC power adapter | 1 | Isolated low-voltage source | Certified enclosed supply, current-limited; no exposed mains work |
| 12 V DC loads | 3 | Physical load channels | Keep aggregate current within every component rating |
| Logic-level MOSFET driver modules | 3 | Switch DC load branches | Must be compatible with 3.3 V gate logic and load inrush |
| Branch fuses + holders | 3+ | Overcurrent protection | Fuse each branch close to the source |
| Emergency-stop switch | 1 | Physical interruption of load bus | Normally closed safety loop; correctly DC-rated |
| ARM switch | 1 | Local arming interlock | Software cannot arm the hardware by itself |
| Terminal blocks, wire, enclosure | as needed | Safe assembly | Strain relief, insulation and appropriate wire gauge |
| Optional PV panel + controller + protected battery | 1 set | Real small-scale solar/storage demonstration | Optional stretch only; follow manufacturer/BMS guidance |

## Data path

1. INA3221 reports bus voltage and branch current.
2. ESP32 computes branch power and publishes timestamped telemetry.
3. Backend records telemetry and compares actual channel draw with the scheduled state.
4. Scenario engine proposes a load plan.
5. User reviews and confirms the plan.
6. ESP32 accepts only the permitted load-state commands while physical ARM and E-stop interlocks are healthy.
7. Any sensor fault, overcurrent or interlock loss forces all load outputs OFF. Faults remain latched until the cause is inspected locally and the controller is rebooted. The firmware also forces outputs OFF on Wi-Fi/MQTT loss and uses a non-blocking reconnect schedule.

## Manual operator console

The optional `scripts/rig_console.py` subscribes to telemetry and sends a command only after a human types an explicit confirmation phrase. It does not replace the physical ARM switch or E-stop. Set `MQTT_HOST`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD` and `MQTT_TOPIC_PREFIX`, then run `python scripts/rig_console.py`. The console waits for a fresh telemetry update after publishing and reports whether the channel state was actually confirmed. Do not interpret broker publish success as proof that a load switched.

## Hardware validation checklist

- Verify polarity and wiring with the supply disconnected.
- Verify sensor readings against a known meter / known load before trusting telemetry.
- Check the shunt resistance and board current/thermal rating from the exact breakout revision.
- Test each branch individually before connecting all loads.
- Test E-stop physically, not only through software.
- Test boot state: every MOSFET gate must default OFF.
- Test MQTT disconnect and ESP32 reboot: every output must fail OFF.
- Test overcurrent and sensor-disconnect behaviour.
- Log command, user confirmation, interlock state and measured response.

## Safety boundary

Do not connect this prototype to AC mains, distribution boards, utility meters or a real building load. Do not construct a homemade mains energy meter. For commercial pilots, use certified metering / smart-plug / inverter interfaces and qualified electrical installers. Do not use the prototype as a protective relay, anti-islanding device, battery management system or grid controller.
