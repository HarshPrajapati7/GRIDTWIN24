# Originality and product-position review

## What already exists

- Home Assistant's Energy dashboard already visualises grid, solar, battery and device energy flows and supports automations through a broad hardware ecosystem.
- Commercial building-energy platforms already monitor, forecast and optimise building energy usage.
- Recent research already studies digital-twin-based microgrid control, energy management and hardware-in-the-loop validation.

Therefore, “AI predicts demand + smart dashboard + digital twin” is not a claim of world-first novelty.

## The specific proposition to validate

GRIDTWIN-24 is intended as a modular, vendor-neutral, open forecasting and scenario layer for smaller facilities that cannot justify or integrate a heavyweight enterprise building-management installation. It links:

1. a reproducible next-day demand forecast,
2. explicit price / capacity / comfort constraints,
3. a transparent schedule with assumptions and operator-visible confirmation,
4. a low-cost, isolated DC hardware bench design for later developer and operator validation,
5. Gemma 4 as a natural-language interface over deterministic tools.

## What would make this defensible

- Real pilot datasets across different building types.
- A better forecast than simple seasonal baselines at the customer's actual decision horizon.
- Measured operational outcome without comfort / service compromise.
- Reliable integration with heterogeneous meter and inverter interfaces.
- A low-friction onboarding process and transparent pricing.
- Customer retention because decisions and alerts are useful every week.

## What would disprove the business thesis

- Facility managers do not act on forecasts.
- Their tariff / contracted demand does not create an economic case for shifting.
- Interval-meter data is unavailable or too expensive to access.
- Existing BMS providers already solve the problem at lower total cost.
- The value of the software is smaller than the cost of installing and maintaining hardware.

## Founder rule

Do not build a hardware SKU before a read-only software pilot proves that customers want the decisions it enables. The HIL rig is for engineering demonstration and later integration R&D, not proof of product-market fit.


## The more specific product wedge

The product is not positioned as a new generic energy dashboard or as the first microgrid digital twin. Its differentiated prototype is the reproducible chain from a 24-hour forecast to a constrained local-site schedule and PV + battery dispatch simulation, with a designed low-voltage bench for later measured validation and human-reviewed operation. The current code does not provide persistent, tamper-evident action logging. Commercial value still needs to be validated with real site data and a buyer who has authority to change operating schedules.
