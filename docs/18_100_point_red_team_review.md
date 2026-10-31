# 100-point red-team review — GRIDTWIN-24

This is a structured 100-check review of the project scope, code, validation, operator interface, physical demonstrator and business thesis. It is **not** a claim that 100 independent experiment runs or field tests were performed.

## Status legend

- `[x]` Implemented in the repository or checked locally.
- `[~]` Designed / partially implemented; must be validated with the organiser dataset, Gemma API, physical hardware or a customer.
- `[ ]` Not yet implemented; do not claim it in a demo or product specification.

## A. Problem fit and scope (1–10)

1. [x] The selected challenge is the official **Tomorrow's Load** statement.
2. [x] The core output is exactly 24 hourly values.
3. [x] The application produces a forecast-vs-actual validation view.
4. [x] The organiser dataset is kept separate from synthetic demo data.
5. [x] Energy scenarios are explicitly separated from the grid forecast series.
6. [x] The demo labels synthetic data as synthetic.
7. [x] No real-grid control capability is claimed.
8. [x] The optional hardware is described as a 12 V DC energy bench, not a complete microgrid.
9. [x] Gemma is an operator interface, not the numerical forecasting engine.
10. [x] The README states that forecast accuracy, savings and product viability are not yet established on real customer data.

## B. Data integrity and ingestion (11–20)

11. [x] Required timestamp and demand columns are explicitly mapped.
12. [x] Naive timestamps require a source timezone.
13. [x] Timezone-aware timestamps are converted to UTC.
14. [x] Duplicate timestamps are grouped and averaged.
15. [x] The loader resamples to an hourly index.
16. [x] Internal gaps of at most two hours can be time-interpolated.
17. [x] Longer or boundary gaps are rejected rather than silently dropped.
18. [~] The organiser's timestamp, timezone, units and missing-value conventions still need inspection.
19. [~] Data lineage and any dataset-specific quality flags need to be recorded after the dataset is released.
20. [ ] A production-grade immutable dataset-versioning and audit store is not implemented.

## C. Forecast model (21–30)

21. [x] The starter model produces a direct 1–24 hour forecast.
22. [x] Lag features use only data available at the forecast origin.
23. [x] Rolling features are calculated from historical observations only.
24. [x] Hour-of-day and day-of-week features are included.
25. [x] Annual cyclic features are included as a modelling hypothesis.
26. [x] The seasonal-naive baseline is included.
27. [x] Negative demand predictions are clipped to zero.
28. [~] The tree-based model must be compared with alternatives on the supplied dataset.
29. [~] Exogenous variables can be added only after verifying they are known at forecast issuance time.
30. [ ] Online model retraining and model registry are not implemented.

## D. Evaluation and statistical trust (31–40)

31. [x] Evaluation uses rolling forecast origins.
32. [x] Forecast windows are at least 24 hours apart.
33. [x] Random row splitting is not used for final model evaluation.
34. [x] MAE is reported.
35. [x] RMSE is reported.
36. [x] WAPE is reported when the denominator is non-zero.
37. [x] Top-decile peak recall is reported.
38. [x] Global permutation importance is labelled as predictive association, not causal explanation.
39. [x] Empirical bands are withheld if the residual sample is too small and a disjoint residual-slice coverage diagnostic is reported otherwise.
40. [~] No performance claim can be made until the organiser dataset has been evaluated and results reviewed.

## E. Flexible-load and battery scenario models (41–50)

41. [x] Flexible-load scheduling is a separate deterministic function.
42. [x] Task windows and task durations are checked.
43. [x] Capacity overload is exposed in the scenario result.
44. [x] The PV/battery model is a separate local-site simulation.
45. [x] Hourly energy balance is encoded in a linear programme.
46. [x] Battery charge and discharge power limits are applied.
47. [x] Battery state-of-charge bounds are applied.
48. [x] Charge/discharge efficiencies and throughput degradation cost are modelled.
49. [x] Terminal state of charge equals initial state of charge to avoid treating stored energy as free.
50. [~] Real tariff structures, export rules, battery warranties and measured site profiles must be configured for any customer pilot.

## F. Gemma 4 agent (51–60)

51. [x] Gemma is optional; the core application runs without an API key.
52. [x] The default model ID is configured in one place.
53. [x] Function calls pass through a fixed Python allow-list.
54. [x] Forecast values come from deterministic Python outputs.
55. [x] Flexible-load scenarios run in Python.
56. [x] PV/battery scenarios run in Python.
57. [x] Rig telemetry access is read-only.
58. [x] The agent has no GPIO or hardware-write tool.
59. [~] A live API run still requires an API key, current account access and end-to-end validation.
60. [ ] Persistent, tamper-evident tool-call audit storage is not implemented.

## G. User interface and usability (61–70)

61. [x] A Streamlit dashboard is included.
62. [x] Users can upload a CSV.
63. [x] Users can map timestamp and demand columns.
64. [x] Users can specify the source timezone for naive timestamps.
65. [x] Forecast and evaluation metrics are displayed.
66. [x] Forecast-vs-actual comparison is displayed.
67. [x] Feature importance is available when evaluation rows support it.
68. [x] Flexible-load and PV/battery scenario labs are separated from the official grid series.
69. [~] A full interactive session against the real organiser dataset must be completed on event day.
70. [ ] Multi-tenant authentication, roles, billing and facility onboarding are not implemented.

## H. Physical energy bench (71–80)

71. [x] The scope is 12 V DC only.
72. [x] The design uses an ESP32 telemetry gateway.
73. [x] The design uses an INA3221 three-channel monitor.
74. [x] Three switched DC load branches are documented.
75. [x] Branch fuses are specified.
76. [x] A physical E-stop interrupts the 12 V load bus.
77. [x] A separate physical ARM switch is specified in the gate-drive path.
78. [x] External MOSFET gate-to-source pulldowns are specified.
79. [~] Firmware has not been compiled against the exact selected Arduino library versions or tested on the assembled circuit.
80. [~] Current thresholds, shunt values, thermal limits and physical fail-safe behaviour must be validated on the actual components before energising loads.

## I. Safety, security and privacy (81–90)

81. [x] No AC mains connection is part of the prototype.
82. [x] The E-stop is physical, not a software command.
83. [x] Firmware defaults outputs to OFF at boot.
84. [x] Firmware forces outputs OFF on Wi-Fi/MQTT loss.
85. [x] Faults are latched until local inspection and reboot.
86. [x] MQTT command messages are non-retained.
87. [x] The human console requires an explicit typed confirmation.
88. [x] The console rechecks telemetry freshness before an ON command and looks for a new packet after publishing.
89. [~] Broker ACLs, unique credentials, network isolation and command authentication must be configured and penetration-tested before any wider deployment.
90. [ ] Formal electrical certification, product safety assessment and independent security audit are not completed.

## J. Commercial viability and delivery (91–100)

91. [x] A first customer hypothesis is defined: small multi-building facilities with a facilities owner and usable interval data.
92. [x] A software-first, read-only pilot is the proposed first deployment.
93. [x] Hardware is not required to prove the first software value proposition.
94. [x] The business model separates SaaS, commissioning and later hardware revenue.
95. [x] Existing energy dashboards and building-management systems are acknowledged as competitors.
96. [~] No customer interviews or signed pilot commitments are included in this package.
97. [~] No real-site energy savings have been measured.
98. [x] A synthetic demo, slide deck, architecture diagrams and technical documentation are included.
99. [~] The organiser dataset and live Gemma account are required to complete the event-specific validation.
100. [ ] Product-market fit, recurring revenue, manufacturing design and commercial electrical compliance remain unproven.

## Release decision

**Suitable for:** a hackathon prototype, synthetic-data walkthrough, code review and supervised 12 V DC bench development after component-specific safety checks.

**Not yet suitable for:** claiming real dataset accuracy, guaranteeing cost or energy savings, autonomous building control, connecting to mains, or selling as a certified energy-management controller.

The next acceptance gates are: (1) evaluate with the organiser dataset, (2) validate the Gemma API path, (3) bench-test the actual electronics under supervision, and (4) secure a read-only customer pilot with interval-meter data.
