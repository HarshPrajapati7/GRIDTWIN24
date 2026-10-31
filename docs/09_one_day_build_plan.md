# Build plan

## One-day hackathon MVP (protect the required deliverable)

**P0 — required core**
1. Inspect organiser data and create a canonical hourly series.
2. Run seasonal-naive benchmark.
3. Train one horizon-conditioned model.
4. Generate next 24 hourly forecasts.
5. Validate using rolling origins and show forecast-vs-actual chart.

**P1 — high-value bonus**
6. Add peak/spike markers, driver explanation and empirical interval if calibration data is adequate.
7. Build a clean dashboard with an evaluation panel.

**P2 — differentiator**
8. Add scenario simulator for flexible local-site loads, explicit tariff and capacity constraints.
9. Add Gemma tool-calling interface for forecast explanation and scenario queries.

**P3 — physical wow factor**
10. Connect the ESP32/INA3221 12 V bench; measure 3 channels; use an operator-confirmed schedule to switch low-voltage demo loads.
11. Record the action and telemetry in an audit timeline.

If time is tight, do not drop P0 to build P3. A functioning physical demo is a bonus, not a substitute for the official problem.

## Suggested team split (if the organisers place you in a team)

| Workstream | Deliverable |
|---|---|
| Data / ML | Data audit, baseline, 24h model, time-based evaluation |
| Product / frontend | Dashboard, forecast-vs-actual chart, peak view |
| Backend / agent | FastAPI, scenario functions, Gemma tool calling |
| Hardware / integration | ESP32 firmware, sensor telemetry, safe DC load control |
| Integration / QA | End-to-end demo, tests, demo script, slides |

For a smaller team, merge frontend with integration and leave hardware as a stretch feature.

## 30-day post-hackathon plan

- Week 1: reproduce results on the actual organiser dataset; write model card and data card.
- Week 2: obtain one consenting pilot site's interval data; build site-specific ingestion.
- Week 3: compare forecast and simple baseline; interview facility manager; implement tariff / operating constraints.
- Week 4: deliver read-only paid pilot report; evaluate whether customer will continue. Only then build field hardware integration.
