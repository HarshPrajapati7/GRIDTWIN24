import { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { ForecastResponse } from "../api";
import { Card } from "./ui";

function shortDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    hour12: false,
  });
}

export function EvaluationTab({ data }: { data: ForecastResponse }) {
  const valData = useMemo(
    () =>
      data.validation.map((v) => ({
        label: shortDate(v.timestamp),
        actual: v.actual,
        model: v.model_forecast,
        naive: v.seasonal_naive,
      })),
    [data],
  );

  const fiData = useMemo(
    () => [...data.feature_importance].sort((a, b) => a.mae_increase - b.mae_increase),
    [data],
  );

  return (
    <div className="grid gap-5">
      <Card
        title="Rolling-origin evaluation — forecast vs actual"
        subtitle={`Held-out validation ${shortDate(data.summary.validation_start)} → ${shortDate(
          data.summary.validation_end,
        )} (last 7 days shown).`}
      >
        <div className="h-[380px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={valData} margin={{ top: 10, right: 16, bottom: 0, left: -8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" />
              <XAxis dataKey="label" tick={{ fill: "#8a97ab", fontSize: 11 }} minTickGap={32} />
              <YAxis tick={{ fill: "#8a97ab", fontSize: 11 }} width={56} />
              <Tooltip
                contentStyle={{
                  background: "#121824",
                  border: "1px solid #232d3f",
                  borderRadius: 12,
                  color: "#e6eaf1",
                }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="actual" name="Actual" stroke="#e6eaf1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="model" name="GRIDTWIN model" stroke="#34d399" strokeWidth={2} dot={false} />
              <Line
                type="monotone"
                dataKey="naive"
                name="Seasonal-naive"
                stroke="#8a97ab"
                strokeWidth={1.5}
                strokeDasharray="5 4"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid gap-5 lg:grid-cols-5">
        <Card
          title="Forecast drivers"
          subtitle="Global permutation importance on held-out rows (MAE increase when shuffled)."
          className="lg:col-span-3"
        >
          <div className="h-[340px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fiData} layout="vertical" margin={{ top: 4, right: 16, bottom: 0, left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" horizontal={false} />
                <XAxis type="number" tick={{ fill: "#8a97ab", fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  tick={{ fill: "#8a97ab", fontSize: 11 }}
                  width={96}
                />
                <Tooltip
                  contentStyle={{
                    background: "#121824",
                    border: "1px solid #232d3f",
                    borderRadius: 12,
                    color: "#e6eaf1",
                  }}
                />
                <Bar dataKey="mae_increase" name="MAE increase" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Metrics — model vs baseline" className="lg:col-span-2">
          <div className="overflow-hidden rounded-xl border border-[var(--color-line)]">
            <table className="w-full text-sm">
              <thead className="bg-[var(--color-panel-2)] text-[var(--color-muted)]">
                <tr>
                  <th className="px-3 py-2 text-left font-medium">Metric</th>
                  <th className="px-3 py-2 text-right font-medium text-[var(--color-accent-2)]">Model</th>
                  <th className="px-3 py-2 text-right font-medium">Naive</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                <MetricRow label="MAE" model={data.summary.model_mae} naive={data.summary.naive_mae} better="low" />
                <MetricRow
                  label="Improvement"
                  modelText={`${data.summary.improvement_pct.toFixed(1)}%`}
                  naiveText="—"
                />
                <MetricRow label="Observations" modelText={data.observations.toLocaleString()} naiveText="—" />
                <MetricRow
                  label="Interval calibrated"
                  modelText={data.summary.interval_calibrated ? "yes" : "no"}
                  naiveText="—"
                />
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-[var(--color-muted)]">
            Global predictive importance, not a causal explanation for an individual hour.
          </p>
        </Card>
      </div>
    </div>
  );
}

function MetricRow({
  label,
  model,
  naive,
  modelText,
  naiveText,
  better,
}: {
  label: string;
  model?: number;
  naive?: number;
  modelText?: string;
  naiveText?: string;
  better?: "low" | "high";
}) {
  const modelWins =
    model != null && naive != null && better === "low" ? model < naive : false;
  return (
    <tr className="border-t border-[var(--color-line)]">
      <td className="px-3 py-2 text-slate-300">{label}</td>
      <td
        className={`px-3 py-2 text-right ${modelWins ? "font-semibold text-[var(--color-accent-2)]" : "text-slate-100"}`}
      >
        {modelText ?? model?.toFixed(3)}
      </td>
      <td className="px-3 py-2 text-right text-[var(--color-muted)]">
        {naiveText ?? naive?.toFixed(3)}
      </td>
    </tr>
  );
}
