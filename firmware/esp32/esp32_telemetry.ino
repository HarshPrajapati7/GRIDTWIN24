/*
 * GRIDTWIN-24 low-voltage HIL energy bench firmware.
 * Scope: isolated 12 V DC tabletop demonstrator only. NEVER connect to AC mains.
 * Libraries: Adafruit INA3221, PubSubClient, ArduinoJson.
 * Hardware must include external MOSFET gate pulldowns, a physical ARM switch
 * in series with gate-drive signals, and a DC-rated E-stop that interrupts
 * the 12 V load bus. MCU checks are a secondary safeguard, not safety-rated.
 */
#include <WiFi.h>
#include <Wire.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Adafruit_INA3221.h>
#include <math.h>

const char* WIFI_SSID = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";
const char* MQTT_HOST = "192.168.1.10";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWORD = "";
const char* TOPIC_TELEMETRY = "gridtwin24/rig/telemetry";
const char* TOPIC_COMMAND = "gridtwin24/rig/command";

// Verify the selected MOSFET driver supports 3.3 V logic and the load's inrush.
const uint8_t LOAD_PIN[3] = {25, 26, 27};
const uint8_t ARM_PIN = 32;       // physical ARM switch sense; switch to GND
const uint8_t ESTOP_OK_PIN = 33;  // NC E-stop auxiliary loop; open when pressed
const float MAX_CHANNEL_AMPS[3] = {1.2f, 1.2f, 1.2f}; // MUST be set from actual parts
const float MAX_BUS_VOLTS = 15.0f;                    // for nominal 12 V bench only
const unsigned long SAFETY_CHECK_MS = 50;
const unsigned long TELEMETRY_PUBLISH_MS = 500;
const unsigned long RECONNECT_INTERVAL_MS = 5000;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
Adafruit_INA3221 ina3221;
bool loadState[3] = {false, false, false};
unsigned long lastWifiAttempt = 0;
unsigned long lastMqttAttempt = 0;
unsigned long lastSafetyCheck = 0;
unsigned long lastPublish = 0;
const char* currentFault = "none";

bool hardwareInterlocksOK() {
  return digitalRead(ARM_PIN) == LOW && digitalRead(ESTOP_OK_PIN) == LOW;
}

void allLoadsOff() {
  for (int i = 0; i < 3; i++) {
    loadState[i] = false;
    digitalWrite(LOAD_PIN[i], LOW);
  }
}

void latchFault(const char* reason) {
  allLoadsOff();
  currentFault = reason;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (String(topic) != TOPIC_COMMAND) return;
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) { latchFault("invalid_command_json"); return; }
  if (!hardwareInterlocksOK()) { latchFault("interlock_open"); return; }

  for (int i = 0; i < 3; i++) {
    String key = "load" + String(i + 1);
    if (!doc.containsKey(key)) continue;
    if (!doc[key].is<bool>()) { latchFault("invalid_command_type"); return; }
    bool requested = doc[key].as<bool>();
    if (!requested) {
      loadState[i] = false;
      digitalWrite(LOAD_PIN[i], LOW);
      continue;
    }
    if (String(currentFault) != "none") {
      allLoadsOff();
      return; // fault is latched; inspect and reboot locally after clearing cause
    }

    // The channel is currently off, so pre-switch current is not meaningful.
    // Validate bus voltage now; the fast safety loop checks current immediately
    // after energising the channel and shuts ALL outputs off on overcurrent.
    float busV = ina3221.getBusVoltage(i);
    if (!isfinite(busV) || busV <= 0.0f || busV > MAX_BUS_VOLTS) {
      latchFault("bus_voltage_out_of_range");
      return;
    }
    loadState[i] = true;
    digitalWrite(LOAD_PIN[i], HIGH);
  }
}

void maintainConnections() {
  unsigned long now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    allLoadsOff();
    if (mqtt.connected()) mqtt.disconnect();
    if (now - lastWifiAttempt >= RECONNECT_INTERVAL_MS) {
      lastWifiAttempt = now;
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    return;
  }

  if (!mqtt.connected()) {
    allLoadsOff(); // fail OFF on broker loss before attempting reconnection
    if (now - lastMqttAttempt >= RECONNECT_INTERVAL_MS) {
      lastMqttAttempt = now;
      String clientId = "gridtwin24-" + String((uint32_t)ESP.getEfuseMac(), HEX);
      bool ok = (String(MQTT_USER).length() == 0)
        ? mqtt.connect(clientId.c_str())
        : mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD);
      if (ok) mqtt.subscribe(TOPIC_COMMAND, 0);
    }
    return;
  }
  mqtt.loop();
}

void runSafetyChecks() {
  unsigned long now = millis();
  if (now - lastSafetyCheck < SAFETY_CHECK_MS) return;
  lastSafetyCheck = now;

  if (!hardwareInterlocksOK()) {
    latchFault("interlock_open");
    return;
  }

  for (int i = 0; i < 3; i++) {
    if (!loadState[i]) continue;
    float busV = ina3221.getBusVoltage(i);
    float amps = ina3221.getCurrentAmps(i);
    if (!isfinite(busV) || !isfinite(amps)) {
      latchFault("sensor_read_failure");
      return;
    }
    if (busV <= 0.0f || busV > MAX_BUS_VOLTS) {
      latchFault("bus_voltage_out_of_range");
      return;
    }
    if (amps < 0.0f || amps > MAX_CHANNEL_AMPS[i]) {
      latchFault("overcurrent");
      return;
    }
  }
}

void publishTelemetry() {
  if (!mqtt.connected()) return;
  unsigned long now = millis();
  if (now - lastPublish < TELEMETRY_PUBLISH_MS) return;
  lastPublish = now;

  StaticJsonDocument<512> doc;
  doc["armed"] = hardwareInterlocksOK();
  doc["fault"] = currentFault;
  doc["uptime_ms"] = now;
  for (int i = 0; i < 3; i++) {
    float v = ina3221.getBusVoltage(i);
    float a = ina3221.getCurrentAmps(i);
    String k = "channel" + String(i + 1);
    doc[k]["voltage_v"] = v;
    doc[k]["current_a"] = a;
    doc[k]["power_w"] = (isfinite(v) && isfinite(a)) ? v * a : 0.0f;
    doc[k]["load_on"] = loadState[i];
  }
  char buffer[512];
  size_t n = serializeJson(doc, buffer, sizeof(buffer));
  mqtt.publish(TOPIC_TELEMETRY, buffer, n, false);
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) {
    pinMode(LOAD_PIN[i], OUTPUT);
    digitalWrite(LOAD_PIN[i], LOW);
  }
  pinMode(ARM_PIN, INPUT_PULLUP);
  pinMode(ESTOP_OK_PIN, INPUT_PULLUP);
  allLoadsOff();

  Wire.begin();
  if (!ina3221.begin()) {
    latchFault("ina3221_not_detected");
    Serial.println("INA3221 not found; outputs remain OFF");
    while (true) { allLoadsOff(); delay(1000); }
  }
  // Configure shunt resistance only after verifying the exact breakout values.
  // Example API: ina3221.setShuntResistance(channel_index, resistance_ohms).

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setSocketTimeout(2);
  mqtt.setKeepAlive(10);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void loop() {
  // Hardware E-stop physically interrupts the 12 V load bus independently.
  // MCU interlocks and current checks are additional safeguards only.
  runSafetyChecks();
  maintainConnections();
  publishTelemetry();
}
