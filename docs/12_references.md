# References

## Event / problem statement

- Hacktoberfest Hack Day Lucknow — Major League Hacking event page and prize categories: https://www.mlh.com/events/hacktoberfest-hack-day-lucknow-x-faculty-of-engineering-and-technology-university-of-lucknow
- Official problem statement: the six-page PDF supplied by the participant. “Tomorrow's Load” is page 3; it requests 24 hourly next-day grid-demand forecasts and a forecast-vs-actual view. Bonus ideas: low/high ranges, peak flags, explanatory drivers.

## Gemma 4

- Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Gemma 4 function calling: https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4
- Google Gen AI Python SDK manual function calling examples: https://googleapis.github.io/python-genai/
- Gemma 4 on Gemini API: https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api
- Gemma 4 official overview: https://deepmind.google/models/gemma/gemma-4/

Gemma 4 has multimodal inputs and function calling. Its function-calling documentation explicitly states that the application must execute and validate tool calls itself; the model does not execute code automatically.

## Forecasting / leakage

- “Data Leakage From Full-Series Signal Decomposition Inflates the Reported Accuracy of Short-Term Energy Forecasting Hybrids: A Leakage-Controlled Re-Evaluation,” International Journal of Energy Research, first published 9 October 2026: https://onlinelibrary.wiley.com/doi/10.1155/er/4433079
- “Leakage-aware benchmarking of temporal data preparation for hourly energy forecasting,” Energy Conversion and Management: X, May 2026: https://doi.org/10.1016/j.ecmx.2026.101791

## Optimisation

- SciPy `linprog` (HiGHS) linear optimisation interface: https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html

## Hardware

- Texas Instruments INA3221: 26 V, triple-channel, 13-bit I2C current/voltage monitor, 0–26 V common-mode range; channel current depends on shunt and implementation: https://www.ti.com/product/INA3221
- Adafruit INA3221 Arduino library: https://github.com/adafruit/Adafruit_INA3221
- Adafruit INA3221 Arduino guide: https://learn.adafruit.com/adafruit-ina3221-breakout/arduino
- Espressif ESP32 hardware design guidelines: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html

## Existing product landscape / market risks

- Home Assistant Energy dashboard: https://www.home-assistant.io/docs/energy/
- Home Assistant battery integration and CT-clamp installation warning: https://www.home-assistant.io/docs/energy/battery
- Schneider Electric India building energy management: https://www.se.com/in/en/work/software/ecostruxure-building/large-buildings-energy-management/
- CEEW, “How can India create a demand flexibility market?” (2026): https://www.ceew.in/publications/how-india-can-create-demand-flexibility-market-five-pillars
- Smart Meter India FAQ: consumer access via utility portal/app; personalised data sharing requires consent: https://smartmeterindia.org/images/PDF/FAQsSmartMeterBooklet.pdf

## Related microgrid research

- “Digital twin based microgrid control and energy management: Trends, challenges, and future directions,” Computers and Electrical Engineering, June 2026: https://www.sciencedirect.com/science/article/pii/S0045790626001722
- “Development and experimental validation of a low-cost, real-time energy management system for microgrid clusters...” (HIL research): https://www.sciencedirect.com/science/article/pii/S2352152X2504931X

## How to use these references

They establish technical context, current product alternatives and model/hardware capabilities. They do not prove that GRIDTWIN-24 is unique, commercially viable, safe for mains installation, or capable of a particular saving. Those claims require independent tests and customer pilots.
