# Product brief — GRIDTWIN-24

## One-sentence thesis

GRIDTWIN-24 forecasts tomorrow's electricity demand, turns the forecast into transparent operational scenarios, and includes a low-voltage physical DC energy-bench design for later validation.

## Who has the problem?

Electricity users and operators need to understand when demand will rise and which loads can safely move without disrupting people or operations. The first paying customer should not be “everyone.” Start with facilities that have a person responsible for energy and a repeated bill: hostels, campuses, apartment common areas, clinics, co-working spaces, small hotels and small commercial facilities.

## Product promise

“Know tomorrow's demand. See the expensive or constrained hours. Test a practical load plan before changing the real site.”

## Three product surfaces

1. **Forecast desk:** 24-hour demand forecast, baseline comparison, uncertainty range (only if calibrated), peak/spike alerts and explanations.
2. **Energy scenario lab:** local-site load, PV, tariff and battery profile; optimise grid imports/exports and state of charge under power, efficiency, reserve, degradation and optional demand-charge constraints.
3. **Physical HIL rig:** a low-voltage DC demonstrator measures source and load channels and safely toggles selected demo loads according to an approved schedule.

## Why the hardware matters

A chart alone can be copied. A measured loop from forecast -> scenario -> command -> physical load response -> telemetry would create a stronger engineering demonstration once the hardware is assembled and validated. The bench validates the sensing and control path only; it does not validate utility-scale grid control or prove savings at a real building.

## Product boundaries

- Challenge model: forecasts the organiser's grid-demand series.
- Site energy module: forecasts / simulates one site's own load only after site interval data is available.
- HIL: validates low-voltage demo control and telemetry.
- Gemma 4: interprets requests and invokes allow-listed tools; it is not the numerical forecasting or safety controller.

## Product principles

Local-first, vendor-neutral, measurable, explainable, privacy-preserving, opt-in automation, and fail-safe by design.
