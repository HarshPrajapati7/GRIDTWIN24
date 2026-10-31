# Build status and verification boundaries

## Locally verified

- Python source compilation: passed (`python -m compileall -q src scripts streamlit_app.py`).
- Automated tests: 13 passed (`pytest -q`).
- Synthetic demonstration script: completed and generated a 24-row next-day forecast, rolling-origin validation CSV, feature-importance CSV, metrics JSON, flexible-load scenario JSON and PV/battery scenario JSON.
- PowerPoint: 16 slides; rendered to PNG previews; automated slide overflow test passed.
- Architecture diagrams: Graphviz source rendered to PNG/SVG.
- 100-point red-team checklist: present in `docs/18_100_point_red_team_review.md`.

## Not yet verified / external dependencies

- The organisers' dataset was not included in this package. No competition accuracy result is claimed.
- The synthetic dataset is only a deterministic smoke-test fixture. Its metrics must not be reported as real grid or customer results.
- A live Gemma 4 API call was not run because no user API key/account access was supplied. Install `google-genai` and verify model availability before a live demo.
- The Streamlit application code is included and compiles, but the Streamlit runtime was not launched in this environment because the `streamlit` package is not installed here. It is listed in `requirements.txt`.
- ESP32 firmware was not compiled against the exact selected board and Arduino library versions. The physical energy bench has not been assembled or tested.
- MQTT console / firmware integration has not been tested against a live broker or physical board.
- No actual site energy savings, customer adoption, willingness to pay or product-market fit have been measured.

## Safety boundary

The hardware design is for an isolated, fused 12 V DC tabletop energy bench only. Never connect it to AC mains, distribution boards, utility meters or live building loads. Verify the exact board, shunts, driver modules, fuses, wires, power supply and E-stop ratings before assembly. Use qualified supervision. This prototype is not a certified controller or protective device.

## Reproducible commands

```bash
python -m venv .venv
# Activate the environment for your OS
pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_demo.py
pytest -q
streamlit run streamlit_app.py
```

See `README.md`, `hardware/README.md` and `docs/` for the complete setup and project explanation.
