import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { ForecastResponse } from "./api";
import { Badge, Stat, Spinner } from "./components/ui";
import { ForecastTab } from "./components/ForecastTab";
import { EvaluationTab } from "./components/EvaluationTab";
import { LoadShiftTab } from "./components/LoadShiftTab";
import { BatteryTab } from "./components/BatteryTab";

type TabKey = "forecast" | "evaluation" | "loadshift" | "battery";

const TABS: { key: TabKey; label: string; icon: string }[] = [
  { key: "forecast", label: "Forecast", icon: "📈" },
  { key: "evaluation", label: "Evaluation", icon: "🎯" },
  { key: "loadshift", label: "Load-Shift", icon: "🔀" },
  { key: "battery", label: "Battery Lab", icon: "🔋" },
];

export default function App() {
  const [data, setData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabKey>("forecast");
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function loadDemo() {
    setLoading(true);
    setError(null);
    try {
      setData(await api.forecast());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDemo();
  }, []);

  async function onUpload(file: File) {
    setUploading(true);
    setError(null);
    try {
      setData(await api.uploadForecast(file));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      {/* Hero */}
      <header className="gt-fade overflow-hidden rounded-3xl border border-[var(--color-line)] bg-gradient-to-br from-[#141b29] via-[#17202f] to-[#271d0d] p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="flex items-center gap-2 text-3xl font-black tracking-tight text-slate-50 sm:text-4xl">
              <span className="text-[var(--color-accent)]">⚡</span> GRIDTWIN-24
            </h1>
            <p className="mt-1 text-sm text-[var(--color-muted)] sm:text-base">
              Forecast-to-Physics Energy Intelligence · Tomorrow's demand, today's decisions.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge>Problem 02 · Tomorrow's Load</Badge>
              <Badge tone="green">Deterministic ML</Badge>
              <Badge tone="green">Rolling-origin eval</Badge>
              <Badge tone="amber">LP battery dispatch</Badge>
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void onUpload(f);
              }}
            />
            <button
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              className="rounded-xl border border-[var(--color-line)] bg-[var(--color-panel)] px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-[var(--color-accent)] disabled:opacity-50"
            >
              {uploading ? "Processing…" : "⬆ Upload demand CSV"}
            </button>
            <button
              onClick={() => void loadDemo()}
              className="text-xs text-[var(--color-muted)] underline-offset-2 hover:text-slate-200 hover:underline"
            >
              reset to demo dataset
            </button>
          </div>
        </div>
      </header>

      {/* Data source banner */}
      {data && (
        <div
          className={`gt-fade mt-4 rounded-2xl border px-4 py-3 text-sm ${
            data.synthetic
              ? "border-amber-500/30 bg-amber-500/5 text-amber-200"
              : "border-emerald-500/30 bg-emerald-500/5 text-emerald-200"
          }`}
        >
          {data.synthetic ? "🧪 " : "✅ "}
          <span className="font-semibold">{data.source_label}.</span>{" "}
          {data.synthetic
            ? "These numbers are a software smoke test, not a real grid or customer result."
            : "Results below are computed live from your uploaded file."}
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error} — is the backend running on :8000?
        </div>
      )}

      {/* KPI row */}
      {data && (
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <Stat label="Observations" value={data.observations.toLocaleString()} />
          <Stat label="Model MAE" value={data.summary.model_mae.toFixed(2)} accent="green" />
          <Stat label="Baseline MAE" value={data.summary.naive_mae.toFixed(2)} />
          <Stat
            label="Beats baseline"
            value={`${data.summary.improvement_pct.toFixed(0)}%`}
            accent="amber"
          />
          <Stat label="Peak hours" value={String(data.summary.peak_hours)} accent="blue" />
        </div>
      )}

      {/* Tabs */}
      <nav className="mt-6 flex gap-1 overflow-x-auto rounded-2xl border border-[var(--color-line)] bg-[var(--color-panel)]/60 p-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
              tab === t.key
                ? "bg-[var(--color-accent)] text-black"
                : "text-[var(--color-muted)] hover:bg-[var(--color-panel-2)] hover:text-slate-200"
            }`}
          >
            <span className="mr-1.5">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main className="mt-5">
        {loading && (
          <div className="flex h-64 items-center justify-center">
            <Spinner label="Training the 24-hour model on the dataset…" />
          </div>
        )}
        {!loading && data && (
          <>
            {tab === "forecast" && <ForecastTab data={data} />}
            {tab === "evaluation" && <EvaluationTab data={data} />}
            {tab === "loadshift" && <LoadShiftTab />}
            {tab === "battery" && <BatteryTab />}
          </>
        )}
      </main>

      <footer className="mt-8 border-t border-[var(--color-line)] pt-4 text-xs text-[var(--color-muted)]">
        All metrics are computed live by the deterministic pipeline in{" "}
        <code className="text-slate-300">src/gridtwin/</code> via the FastAPI backend. Synthetic
        demo data is labelled as such and must not be reported as a real result.
      </footer>
    </div>
  );
}
