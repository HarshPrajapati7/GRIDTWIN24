# Start here — first 90 minutes

1. Read `README.md` and `docs/02_problem_statement_fit.md`.
2. Run `pip install -r requirements.txt` in a virtual environment.
3. Run `python scripts/generate_demo_data.py` and `python scripts/run_demo.py`; the script emits synthetic forecast, validation, feature-importance, flexible-load and PV/battery scenario outputs.
4. Run `pytest -q`.
5. Start `streamlit run streamlit_app.py` and inspect the synthetic example.
6. When organisers provide their dataset, do not train immediately. First fill in a data dictionary: timestamp, target column, unit, timezone, interval, related features and gaps.
7. Use the provided dataset in the model path; never use the synthetic fixture for the competition result.
8. Only after the forecast is complete, wire in Gemma tool calling and the DC hardware bench.
9. Read `docs/18_100_point_red_team_review.md` before presenting claims.
10. Follow `hardware/README.md` before powering any physical circuit.
