# Technical acceptance tests

## Dataset
- [ ] Actual timestamp, demand and units confirmed from organiser data dictionary / file.
- [ ] Timezone recorded; timestamps sorted and unique after documented aggregation.
- [ ] Missing intervals counted and reported.
- [ ] Future-known and future-unknown covariates separated.

## Forecast
- [ ] Exactly 24 hourly timestamps are emitted for the next local/UTC day according to dataset convention.
- [ ] Seasonal-naive baseline is computed.
- [ ] At least 3 non-overlapping rolling-origin forecast windows where data length permits.
- [ ] No random row split for time-series generalisation claim.
- [ ] MAE, RMSE and WAPE calculated in original demand units.
- [ ] Peak threshold declared before looking at held-out labels.
- [ ] Interval calibration count, observed coverage and width are reported.

## Scenario engine
- [ ] Each task's power, duration and allowed window validated.
- [ ] Capacity constraints checked and violations shown.
- [ ] Tariff units and time zone documented.
- [ ] Baseline scenario includes the same flexible tasks as the optimised scenario.
- [ ] Output explicitly marked as an estimate, not measured saving.

## HIL
- [ ] DC bus only; no AC mains connection.
- [ ] Supply current limit set; branch fuses installed.
- [ ] Sensor calibrated against a reference meter.
- [ ] Physical E-stop cuts the 12 V load bus.
- [ ] Hardware ARM switch required.
- [ ] Boot / disconnect / overcurrent / sensor-fault tests force outputs OFF.
- [ ] Command and telemetry audit trail available.

## Gemma 4
- [ ] Tool arguments schema-validated.
- [ ] Numeric outputs come from deterministic tools.
- [ ] No direct GPIO or raw command endpoint exposed to the model.
- [ ] Human confirmation required for any HIL state change.
- [ ] Tool calls and returned results logged.

## Product claims
- [ ] No “saves X%” claim without real pilot data.
- [ ] No assertion that grid forecast equals individual building load.
- [ ] No assertion that a tabletop rig proves grid-scale operational safety.


## PV + battery scenario
- [ ] 24 values supplied for load, PV and tariff.
- [ ] SOC start and end match; battery limits and efficiency respected.
- [ ] Terminal SOC prevents free depletion of initial battery energy.
- [ ] Compare cost with and without battery, including degradation and demand-charge assumptions.
- [ ] Results labelled as simulation, not actual savings or commands.
