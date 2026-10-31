# Red-team review and risk register

| Risk | Why it matters | Mitigation / stop condition |
|---|---|---|
| Wrong dataset schema | Model silently targets wrong column | Manual schema audit, unit check, explicit mapping, summary stats |
| Bad timestamps / gaps | Invalid hourly lags and fake patterns | Duplicate/gap report, timezone audit, reject excessive gaps |
| Temporal leakage | Inflated validation | Rolling-origin 24h forecasts, time-only splits, leakage checklist |
| Baseline beats ML | Fancy model has no value | Show baseline honestly; retain baseline if it wins |
| Very little history | Weekly/seasonal patterns unlearnable | Fall back to persistence/naive; show limited-data warning |
| Future weather unavailable | Cannot use realised future weather | Use only forecast-issued-at-origin variables or omit |
| Uncalibrated intervals | False assurance | Withhold bands until enough residuals; report coverage/width |
| Peak threshold gaming | Looks good only on selected test set | Predeclare threshold or derive from training data only |
| Grid vs site mismatch | Grid forecast cannot directly control one building | Strictly separate challenge forecast and site-local profile |
| Hardware current limits | Component overheating/fire risk | Confirm exact ratings, branch fuses, current-limited supply, enclosure |
| E-stop software-only | MCU failure can leave load on | E-stop physically breaks 12V load bus; default-off hardware |
| MQTT / Wi-Fi loss | Commands can be stale | Fail OFF on lost comms; commands are non-retained. Expiry, sequence IDs, authenticated commands and replay protection are required before any production connection. They are not implemented in the bench prototype. |
| Gemma hallucination | Invented savings / unsafe commands | Tools return numeric truth; schema validation; no direct GPIO |
| Privacy / occupancy inference | Meter traces can reveal routines | Data minimisation, local processing option, consent, retention controls |
| No willingness to pay | Interesting demo, no company | Customer interviews, real data pilot, paid validation |
| Strong incumbents | Existing EMS systems | Narrow ICP; vendor-neutral integration; demonstrate ease and measurable value |
| Overbuilt hackathon scope | Core forecast remains unfinished | Forecast/evaluation first; HIL and agent after core passes |
| Unsupported “savings” claim | Damages credibility | No saving claims without controlled site pilot |
| Product name collision | Brand launch risk | Treat GRIDTWIN-24 as working title; trademark/domain search before launch |

## Go / no-go gates

- **Gate 1 — Dataset:** timestamp, demand and units can be mapped and validated.
- **Gate 2 — Forecast:** 24 outputs produced and evaluated against a baseline.
- **Gate 3 — Trust:** no leakage; test dates and metrics reproducible; interval claims calibrated.
- **Gate 4 — Physical demo:** sensor readings agree with reference checks; all fail-safe tests pass.
- **Gate 5 — Product:** at least one facility partner shares interval data and confirms a recurring decision problem.
