// Typed client for the GRIDTWIN-24 FastAPI backend.
// All numbers come from the deterministic Python pipeline; nothing is mocked.

export type HistoryPoint = { timestamp: string; demand: number };

export type ForecastPoint = {
  timestamp: string;
  forecast: number;
  lower: number | null;
  upper: number | null;
  peak_flag: boolean;
};

export type ValidationPoint = {
  timestamp: string;
  actual: number;
  model_forecast: number;
  seasonal_naive: number;
};

export type FeatureImportance = {
  feature: string;
  mae_increase: number;
  std: number;
};

export type ForecastSummary = {
  model_mae: number;
  naive_mae: number;
  improvement_pct: number;
  peak_hours: number;
  peak_threshold: number;
  interval_calibrated: boolean;
  validation_start: string;
  validation_end: string;
};

export type ForecastResponse = {
  source_label: string;
  synthetic: boolean;
  observations: number;
  history: HistoryPoint[];
  forecast: ForecastPoint[];
  validation: ValidationPoint[];
  feature_importance: FeatureImportance[];
  metrics: Record<string, unknown>;
  summary: ForecastSummary;
};

export type LoadShiftResponse = {
  base_load_kw: number[];
  baseline_load_with_earliest_tasks_kw: number[];
  scheduled_load_kw: number[];
  baseline_cost: number;
  scheduled_cost: number;
  estimated_cost_difference: number;
  tasks: Array<{
    name: string;
    baseline_start_hour: number;
    start_hour: number;
    end_hour_exclusive: number;
    power_kw: number;
    incremental_cost: number;
    overload_kw_hours: number;
  }>;
  capacity_kw: number | null;
  note: string;
};

export type BatteryResponse = {
  baseline_grid_import_kw: number[];
  optimised_grid_import_kw: number[];
  grid_export_kw: number[];
  battery_charge_kw: number[];
  battery_discharge_kw: number[];
  battery_soc_kwh: number[];
  baseline_cost: number;
  optimised_total_cost: number;
  estimated_cost_difference: number;
  baseline_peak_import_kw: number;
  optimised_peak_import_kw: number;
  peak_reduction_kw: number;
  pv_kw: number[];
  load_kw: number[];
  import_tariff: number[];
  note: string;
};

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = (body as { detail?: string }).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => jsonFetch<{ status: string; service: string; version: string }>("/api/health"),
  forecast: () => jsonFetch<ForecastResponse>("/api/forecast"),
  uploadForecast: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return jsonFetch<ForecastResponse>("/api/forecast/upload", { method: "POST", body: form });
  },
  loadShift: (body: {
    base_load_kw: number;
    capacity_kw: number;
    offpeak_tariff: number;
    peak_tariff: number;
  }) =>
    jsonFetch<LoadShiftResponse>("/api/load-shift", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  battery: (body: {
    battery_capacity_kwh: number;
    max_power_kw: number;
    demand_charge_per_kw: number;
  }) =>
    jsonFetch<BatteryResponse>("/api/battery", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
