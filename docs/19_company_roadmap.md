# Company roadmap — from hackathon build to a real product

## Product thesis

GRIDTWIN-24 should become an energy-operations assistant for facilities that need a better view of tomorrow's demand and a safe way to test operational options. It should not start as a universal consumer energy app or a hardware manufacturer.

## Initial customer profile

Start with one campus, hostel operator, apartment common-area manager, clinic group or small hotel operator that:

- has a named facilities / electrical operations owner;
- can export interval meter data or permit a read-only metering pilot;
- has a tariff or demand-charge structure that makes peak timing relevant;
- has flexible, non-critical loads that can be scheduled without compromising safety or comfort;
- is willing to review forecasts and record whether the recommendations changed an operating decision.

Do not assume every site has a smart meter, time-of-use tariff, battery, PV system or permission to automate loads.

## Customer discovery questions

Ask the facilities manager to show actual, anonymised bills or interval records where possible.

1. What decision do you make each day about electricity use?
2. When do you know that a demand peak is coming?
3. What happens operationally or financially when a peak is higher than expected?
4. Which loads can be shifted, and which must never be shifted?
5. Who approves a change to operating schedules?
6. Which meter / BMS / inverter systems are installed, and who controls access?
7. How much time is spent preparing energy reports today?
8. What evidence would make you trust a forecast enough to act on it?
9. What would make this product too risky or too difficult to deploy?
10. Would you share a redacted dataset for a read-only evaluation or pay for a bounded pilot?

A verbal “interesting idea” is not validation. Look for data access, a named operational owner, recurring usage and willingness to fund a pilot.

## Staged roadmap

### Stage 0 — Hackathon prototype

- Use the organiser dataset for the official 24-hour forecast task.
- Benchmark against seasonal-naive and other suitable baselines.
- Publish the data-quality and leakage checks.
- Demonstrate local-site load shifting and PV/battery scenarios with labelled synthetic assumptions.
- Keep Gemma tool calls read-only / simulation-only.
- Build the 12 V energy bench only after the software path works and the actual component ratings are verified.

### Stage 1 — Read-only facility pilot

- Obtain a site-approved export of interval meter data and tariff details.
- Audit units, time zones, cadence, missing intervals and meter boundaries.
- Run daily forecasts and compare them with actual consumption.
- Deliver a weekly operations report.
- Record which forecasts changed a decision and whether the change was acceptable.

### Stage 2 — Paid scenario product

- Add site-specific load inventory and operating constraints.
- Model only flexible loads with an owner-approved schedule window.
- Compare baseline and proposed schedules using the real tariff.
- Show uncertainty, assumptions and estimated—not guaranteed—cost differences.
- Test a paid subscription or pilot fee with the customer.

### Stage 3 — Approved metering and hardware integrations

- Integrate certified meters / gateways through documented, read-only interfaces first.
- Validate calibration against a reference instrument.
- Commission only with qualified electrical professionals.
- Enable automation only for approved, non-critical loads and certified switching equipment.
- Add authentication, command expiry, replay protection, audit storage and a documented safety case before remote actuation.

### Stage 4 — Multi-site product

- Support portfolio-level dashboards and site comparisons.
- Add role-based access, tenant isolation, retention controls and exportable audit reports.
- Build robust integrations for supported meters / BMS vendors.
- Expand to a home / prosumer edition only after meter-data access, household usability and willingness to pay have been validated.

## Metrics that matter

### Model quality

- MAE / RMSE / WAPE by site and horizon.
- Performance against seasonal-naive baseline.
- Peak-hour precision and recall using a predeclared threshold.
- Prediction-interval coverage and width, if intervals are offered.
- Drift and missing-data rate.

### Customer value

- Number of forecasts reviewed each week.
- Number of proposed actions accepted / rejected and why.
- Percentage of recommendations completed safely.
- Measured peak kW and energy cost under a pre-agreed comparison method.
- Comfort / service incidents or operational exceptions.
- Renewal and willingness to pay.

### Product reliability

- Data ingestion success rate.
- Forecast report delivery success.
- Meter / gateway uptime.
- Alert false-positive / false-negative rates.
- Support time per site.

## What must be true before company formation / scale

- At least one real facility provides interval data and a named operations owner.
- The product solves a recurring decision problem, not just a one-off report.
- Forecast performance is measured against a credible baseline.
- A pilot shows a measurable benefit without unacceptable comfort, service or safety trade-offs.
- The customer is willing to pay for continued access.
- The integration / installation cost is compatible with the expected contract value.

## Kill criteria

Pause or change direction if facility managers do not act on forecasts, tariffs do not reward shifting, usable data cannot be obtained, the incumbent BMS already solves the problem at lower total cost, or the value is smaller than metering / support overhead.

## Commercial statement

The business model is a hypothesis, not proven revenue. Start with a read-only SaaS pilot, earn trust through transparent forecasts and measurable reports, and add hardware or actuation only when a paying customer has a specific need for it.
