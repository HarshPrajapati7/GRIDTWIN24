# System architecture

```mermaid
flowchart TB
  A[Organiser hourly grid-demand dataset] --> B[Data audit + hourly canonicalisation]
  B --> C[Feature pipeline: lags, rolling stats, calendar, valid covariates]
  C --> D[24-hour forecasting model]
  D --> E[Rolling-origin evaluation + seasonal-naive baseline]
  E --> F[Forecast API: 24 points, metrics, intervals, peak flags]
  F --> G[Operator dashboard]
  F --> H[Flexible-load scheduler + PV/battery linear-programming optimiser]
  H --> I[Local-site PV + battery model: load, tariff, SOC, efficiency, capacity]
  I --> J[Dispatch plan + constraints + audit log]
  J --> K[human-confirmed MQTT console]
  K --> L[ESP32 + INA3221 + three fused 12V DC load branches]
  L --> M[Measured voltage/current/power + load state]
  M --> G
  N[Gemma 4 operator agent] -->|function calls| F
  N -->|function calls| H
  N -->|read-only by default| M
  N -->|no hardware-write tool| K
```

## Design rule

Keep three layers separate:

- **Forecasting layer:** statistical/ML model produces numbers.
- **Decision layer:** deterministic optimisation / scenario code proposes actions under explicit constraints.
- **Language layer:** Gemma 4 explains results and invokes approved tools.

The language model never calculates the official forecast, invents energy savings, or bypasses protection logic. The human-operated MQTT console and firmware are separate from the Gemma tool surface.

## Interfaces

- Dataset adapter -> canonical hourly `timestamp,demand` series.
- Forecast API -> JSON list of 24 hourly values plus model metadata and evaluation metrics.
- Scenario API -> schedule, estimated cost/demand deltas, and assumptions.
- HIL telemetry -> measured DC voltage/current/power, load state, interlock state and fault flags.
- Agent tools -> small allow-list over the above APIs.
