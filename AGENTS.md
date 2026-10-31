# AGENTS.md — working rules for AI agents and contributors

GRIDTWIN24 is an energy-grid digital twin: load forecasting, battery/flexible-load
dispatch optimisation, a Gemma tool-using agent, an ESP32 hardware-in-the-loop rig,
and a Streamlit UI. This file is the contract for anyone (human or AI) changing the code.

## Golden rules (read these first)

1. **Do not rewrite working code.** If the tests pass and the demo runs, the code is
   working. Change only what the task needs and keep the diff as small as possible.
   No drive-by refactors, renames, or reformatting of files you were not asked to touch.

2. **Do not write from scratch.** Before adding new functionality, find a reputable
   existing implementation first (official library docs, a well-maintained GitHub repo,
   or a published example). Adapt that reference to this codebase instead of inventing an
   approach. Record where it came from (see Attribution below).

3. **Verify before you claim it is done.** Run the tests and the demo and read the real
   output. A command exiting 0 is not proof the feature works; check the actual values.

4. **Preserve the defensive, no-overclaim style.** The modules validate their inputs and
   label scenario results as estimates. Keep that. Never present synthetic or optimised
   figures as measured savings or as a real control command.

5. **No invented data or claims.** Only `data/synthetic_hourly_load.csv` exists, and it is
   synthetic smoke-test data. There is no real/organiser dataset in this repo. Keep code
   dataset-agnostic through `config/data_columns.*.yaml`; do not hardcode column names.

## Environment

- Python **>= 3.10** is required. On this machine the default `python` is 3.9 and will
  fail — use `py -3.13` for every command.
- Install deps: `py -3.13 -m pip install -r requirements.txt` (or `py -3.13 -m pip install -e .`).

## How to run and verify

| Task | Command | Expected |
| --- | --- | --- |
| Unit tests | `py -3.13 -m pytest -q` | `13 passed` |
| Generate demo data | `py -3.13 scripts/generate_demo_data.py` | writes `data/synthetic_hourly_load.csv` |
| End-to-end demo | `py -3.13 scripts/run_demo.py` | forecast metrics + 24h forecast + dispatch scenarios, exit 0 |
| UI (optional) | `py -3.13 -m streamlit run streamlit_app.py` | needs `pip install streamlit plotly` |

## Project layout

- `src/gridtwin/` — core library: `data.py`, `forecasting.py`, `battery.py`,
  `dispatch.py`, `gemma_tools.py`, `gemma_agent.py`, `demo_data.py`.
- `scripts/` — `run_demo.py`, `generate_demo_data.py`, `rig_console.py`.
- `tests/` — pytest suite (keep it green).
- `docs/` — product and design docs (`00`–`19`).
- `outputs/` — generated artifacts (gitignored except `.gitkeep`).
- `data/` — synthetic smoke-test data only.
- `firmware/esp32/`, `hardware/` — HIL rig firmware and bill of materials.

## Code conventions

- Start new modules with `from __future__ import annotations` so modern type hints keep
  working on older runners.
- Follow the existing style: type hints, small pure functions, no new heavy dependencies
  unless the task truly needs them.
- Cross-platform file handling: use `tempfile.TemporaryDirectory()` plus an explicit path
  for temp files. `NamedTemporaryFile` opened by name breaks on Windows (exclusive lock),
  which is why the forecasting test was changed.

## Git and push workflow

- `main` is the working branch. During active sessions an auto-snapshot commit runs about
  every 10 minutes so work is never lost; it pushes once a remote/upstream is configured.
- Use conventional commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `test:`.
- Never commit secrets. Only `.env.example` is tracked; a real `.env` must stay ignored.

## Attribution (applies to rule 2)

When you adapt external code, add a comment at the top of the block:
`# Adapted from <url> (<license>)`, stay within that license, and avoid pasting large
verbatim sections. Prefer understanding and re-expressing the reference over copying it.
