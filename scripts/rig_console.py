"""Human-confirmed MQTT console for the 12 V DC demo bench.

The console is deliberately separate from Gemma. It sends non-retained MQTT
commands only after the operator sees an armed/fault-free telemetry snapshot
and types an explicit confirmation phrase. The firmware independently checks
physical ARM/E-stop, voltage and current limits.
"""
from __future__ import annotations
import json
import os
import threading
import time
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:  # pragma: no cover - optional hardware environment
    raise SystemExit("Install paho-mqtt>=2.0 to use the physical bench console.") from exc

HOST = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
USERNAME = os.getenv("MQTT_USERNAME", "")
PASSWORD = os.getenv("MQTT_PASSWORD", "")
PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "gridtwin24").strip("/")
TELEMETRY_TOPIC = f"{PREFIX}/rig/telemetry"
COMMAND_TOPIC = f"{PREFIX}/rig/command"

latest: dict[str, Any] | None = None
latest_lock = threading.Lock()
message_event = threading.Event()
message_counter = 0
latest_received_at = 0.0


def on_connect(client, userdata, flags, reason_code, properties):
    if int(reason_code) == 0:
        print(f"Connected to MQTT broker {HOST}:{PORT}")
        client.subscribe(TELEMETRY_TOPIC, qos=0)
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, msg):
    global latest, message_counter, latest_received_at
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Ignoring invalid telemetry JSON")
        return
    if not isinstance(payload, dict):
        return
    with latest_lock:
        latest = payload
        latest_received_at = time.monotonic()
        message_counter += 1
    message_event.set()


def snapshot() -> tuple[dict[str, Any] | None, int, float]:
    with latest_lock:
        return (dict(latest) if latest is not None else None,
                message_counter, latest_received_at)


def wait_for_new_telemetry(after_counter: int, timeout: float) -> tuple[dict[str, Any] | None, int, float]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message_event.clear()
        state = snapshot()
        if state[1] > after_counter:
            return state
        message_event.wait(timeout=max(0.0, deadline - time.monotonic()))
    return snapshot()


def main() -> int:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="gridtwin24-human-console")
    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    print("GRIDTWIN-24 — 12 V DC energy bench console")
    print("This console is not certified safety equipment. E-stop and physical ARM remain mandatory.")
    try:
        client.connect(HOST, PORT, keepalive=20)
    except OSError as exc:
        print(f"Cannot connect to MQTT broker {HOST}:{PORT}: {exc}")
        return 2
    client.loop_start()
    try:
        print("Waiting for a telemetry packet...")
        initial = wait_for_new_telemetry(0, 10)
        if initial[0] is None:
            print("No telemetry received. No command will be sent.")
            return 2
        while True:
            state, sequence, received_at = snapshot()
            if not state:
                print("No telemetry snapshot available.")
                return 2
            age = time.monotonic() - received_at
            print("\nLatest telemetry:")
            print(json.dumps(state, indent=2))
            print(f"Telemetry age: {age:.2f} seconds")
            print("\nEnter channel 1-3, or q to quit:")
            choice = input("> ").strip().lower()
            if choice == "q":
                return 0
            if choice not in {"1", "2", "3"}:
                print("Choose 1, 2, 3 or q.")
                continue
            channel = int(choice)
            action = input("Turn load ON or OFF? [on/off]: ").strip().lower()
            if action not in {"on", "off"}:
                print("Invalid action.")
                continue
            if action == "on":
                if age > 2.0:
                    print("Refusing ON: telemetry is stale. Wait for a fresh telemetry packet.")
                    continue
                if not state.get("armed") or state.get("fault") not in (None, "none"):
                    print("Refusing ON: telemetry is not armed and fault-free. Check physical ARM/E-stop and fault state.")
                    continue
                phrase = input("Type exactly ENABLE-12V-LOAD to confirm: ").strip()
                if phrase != "ENABLE-12V-LOAD":
                    print("Confirmation mismatch; no command sent.")
                    continue
            else:
                phrase = input("Type exactly DISABLE-LOAD to confirm: ").strip()
                if phrase != "DISABLE-LOAD":
                    print("Confirmation mismatch; no command sent.")
                    continue
            if action == "on":
                # Re-check after the human prompt; telemetry may have gone stale
                # while the operator was reading and confirming the command.
                fresh_state, fresh_sequence, fresh_received_at = snapshot()
                fresh_age = time.monotonic() - fresh_received_at
                if (not fresh_state or fresh_age > 2.0 or
                        not fresh_state.get("armed") or
                        fresh_state.get("fault") not in (None, "none")):
                    print("Refusing ON: latest telemetry is stale, unarmed or faulted. No command sent.")
                    continue
            payload = json.dumps({f"load{channel}": action == "on"})
            before_publish_sequence = snapshot()[1]
            info = client.publish(COMMAND_TOPIC, payload=payload, qos=0, retain=False)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Publish failed ({info.rc}); no success claimed.")
                continue
            print("Command published (non-retained). Waiting for a new telemetry packet...")
            confirmation = wait_for_new_telemetry(before_publish_sequence, 3)
            verify = confirmation[0] or {}
            if confirmation[1] <= before_publish_sequence:
                print("No new telemetry confirmation received. Check the rig locally; do not assume the action occurred.")
                continue
            channel_state = verify.get(f"channel{channel}", {})
            confirmed_state = channel_state.get("load_on")
            requested_state = action == "on"
            result = "confirmed" if confirmed_state is requested_state else "not confirmed"
            print(json.dumps({"result": result, "armed": verify.get("armed"), "fault": verify.get("fault"), "channel": channel, "requested_load_on": requested_state, "telemetry_load_on": confirmed_state}, indent=2))
    except KeyboardInterrupt:
        print("\nConsole exiting. Use the physical E-stop to stop loads immediately.")
        return 0
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
