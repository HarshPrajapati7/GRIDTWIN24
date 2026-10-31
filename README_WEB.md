# GRIDTWIN-24 — Web Application (React + FastAPI)

A production-grade dashboard for the GRIDTWIN-24 energy-intelligence pipeline.
The React frontend renders **only real data** computed by the deterministic
Python model in `src/gridtwin/` — the FastAPI backend imports those functions
directly and never re-implements or fakes any number.

```
 React (Vite + TS + Tailwind + Recharts)         FastAPI (backend/main.py)
 ────────────────────────────────────────        ──────────────────────────────
 frontend/src/App.tsx         ──  /api/forecast   ─► gridtwin.forecasting
   ├─ ForecastTab             ──  /api/load-shift  ─► gridtwin.dispatch
   ├─ EvaluationTab           ──  /api/battery     ─► gridtwin.battery
   ├─ LoadShiftTab            ──  /api/forecast/upload
   └─ BatteryTab
```

## Prerequisites

- Python **3.10+** (this machine: use `py -3.13`)
- Node.js 18+ and npm (this machine: Node 22, npm 11)
- Python deps: `pip install -r requirements.txt`
  (adds `fastapi`, `uvicorn`, `python-multipart`)

## Run it — development (hot reload)

Two processes. The Vite dev server proxies `/api` to the backend.

```powershell
# terminal 1 — backend
py -3.13 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Or just run the helper:

```powershell
powershell -ExecutionPolicy Bypass -File run_web_dev.ps1
```

## Run it — production (single origin)

Build the React app once; FastAPI then serves the UI **and** the API from one
port (no CORS, no second server):

```powershell
powershell -ExecutionPolicy Bypass -File run_web_prod.ps1
```

Open **http://localhost:8000**.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/api/health` | Liveness probe |
| GET  | `/api/forecast` | Train + evaluate on the synthetic demo dataset (cached) |
| POST | `/api/forecast/upload` | Train + evaluate on an uploaded hourly CSV |
| POST | `/api/load-shift` | Flexible-load scheduling scenario |
| POST | `/api/battery` | PV + battery LP dispatch scenario |

The first `/api/forecast` call trains the model and takes ~20–30s; the UI
shows a spinner. Results are cached per dataset, so later calls are instant.

## Using your own data

Click **Upload demand CSV** in the header. The file needs at least
`timestamp` and `demand` columns (naive timestamps are assumed `Asia/Kolkata`
— verify against your dataset). The banner turns green and every metric is then
computed live from your file. Click *reset to demo dataset* to go back.

## Honesty

The bundled demo dataset is **synthetic** and is labelled as such in the UI. Do
not report its metrics as a real grid or customer result. Upload the organiser's
real dataset to produce real numbers.

## What was NOT changed

Per `AGENT.md`, no existing `src/gridtwin/` model code was rewritten. The web
layer is additive: a new `backend/` API that calls the existing functions, and
a new `frontend/` React app. The original Streamlit app (`streamlit_app.py`)
still works independently.
