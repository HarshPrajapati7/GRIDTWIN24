# Business model and go-to-market

## The product is not “AI for everyone” on day one

The energy problem affects everyone, but the first buyer should be someone who controls a building, sees repeated bills and can authorise a pilot. Start with one segment, not the entire energy market.

## Initial ideal customer profile

- Private college / university campus with multiple buildings.
- Hostel / PG operator with shared loads and a facilities manager.
- Apartment association with common-area pumps, lifts, lighting and HVAC.
- Small hotel, clinic, co-working building or retail chain.

Selection filter: the site should have at least several months of interval consumption data or a practical way to capture it; a clear facilities owner; flexible non-critical loads; and a bill / demand structure where forecasting can affect a decision.

## Product modules

| Module | Buyer value | Monetisation hypothesis |
|---|---|---|
| Forecast & alert SaaS | Next-day demand, peak warnings, reports | Monthly per-site subscription |
| Scenario / scheduling | Explore load shifting against tariff and operating constraints | Higher SaaS tier |
| Gateway / metering integration | Continuous readings from approved meters or IoT devices | Hardware + commissioning fee |
| Multi-site console | Benchmark buildings and report portfolio performance | Enterprise contract |
| Open-source core | Adoption, community integrations, trust | Paid hosting, support, analytics and fleet management |

## The ROI proof required

Do not claim savings from the hackathon demo. A real pilot needs:

1. A pre-agreed baseline period.
2. Metered interval data at an appropriate resolution.
3. A written list of actions the operator agrees are safe and acceptable.
4. Measurement of actual kWh, peak kW / demand charges where applicable, cost and comfort/operational impact.
5. Weather, occupancy, tariff and operating-hour controls where relevant.
6. A comparison period and a written methodology.

## Go-to-market sequence

1. **Campus / hostel pilot:** start read-only from bills or interval-meter exports; provide forecast and peak report.
2. **Paid analytics pilot:** show that the team makes a recurring, useful decision from the report.
3. **Hardware gateway:** add sensor/approved meter integration only where it fills a specific data gap.
4. **Automated scheduling:** enable only certified devices and operator-approved flexible loads.
5. **Multi-site expansion:** sell portfolio analytics to operators managing multiple facilities.

## Competition and differentiation

Home Assistant already supports energy, grid, solar, battery and individual-device sources. Commercial building platforms such as Schneider EcoStruxure and Indian providers also offer energy monitoring and optimisation. The product is not novel merely because it predicts load or shows energy graphs.

The defensible wedge to test is: **a vendor-neutral, transparent, low-cost forecasting + scenario + measured-validation stack for smaller multi-building facilities, with an open protocol and a reproducible low-voltage HIL demonstration.**

## Business risks

- Smart-meter interval data may be difficult to obtain or share. Utility data sharing requires customer consent and access arrangements.
- Many household tariffs do not reward time shifting in the same way; tariff configuration must be jurisdiction- and customer-specific.
- Existing BMS / EMS vendors have installed bases and service teams.
- Hardware installation, calibration and maintenance may cost more than software customers will pay.
- Savings are site-specific and cannot be guaranteed.

## Founder validation plan

Before building a company, interview 10 facility managers and 5 electrical/energy service contractors. Ask for anonymised bills / interval data, identify the exact operational decisions they make, and test whether they would pay for a forecast report or a pilot. Do not ask only whether they “like the idea.” Ask for a paid pilot or access to real data.
