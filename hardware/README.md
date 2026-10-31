# HIL hardware quick sheet

This is a 12 V DC tabletop energy bench only; it is not a complete microgrid and is not a certified safety system. Use the `BOM.csv`, `docs/05_hardware_hil_design.md` and `diagrams/hardware_hil.svg` together.

1. Assemble with the supply disconnected.
2. Follow the exact INA3221 breakout's wiring and shunt specifications.
3. Fuse each branch and the master feed. Add a suitable external gate-to-source pulldown resistor on every MOSFET channel so the load remains OFF while ESP32 GPIO pins are high-impedance.
4. Use only 3.3 V-logic-compatible MOSFET driver modules with sufficient DC load / inrush rating.
5. Fit a physical E-stop that interrupts the 12 V load bus, plus a separate local ARM switch wired in series with the gate-drive signals and also to the MCU interlock input.
6. Keep all ESP32 outputs OFF on boot, reboot, sensor fault, MQTT loss and interlock loss.
7. On Wi-Fi or MQTT loss the firmware forces all outputs OFF. Do not publish retained MQTT control commands; use an authenticated local broker ACL.
8. Do not connect the bench to AC mains, an electrical panel, utility meter or real building load.

Firmware currently uses example current / voltage guard thresholds. Set them from the exact hardware and chosen loads before powering the circuit. Confirm readings with a reference meter. The example code is not certified safety firmware.

## Optional operator console

Install dependencies with `pip install -r requirements.txt`, configure the `MQTT_*` variables from `.env.example`, then run `python scripts/rig_console.py`. The console requests explicit operator confirmation and checks for fresh telemetry after publishing. It does not replace physical interlocks.
