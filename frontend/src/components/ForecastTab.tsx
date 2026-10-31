import { useMemo } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { ForecastResponse } from "../api";
import { Card } from "./ui";

function hourLabel(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { weekday: "short", hour: "2-digit", hour12: false });
}

export function ForecastTab({ data }: { data: ForecastResponse }) {
  const chartData = useMemo(() => {
    const hist = data.history.map((h) => ({
      t: h.timestamp,
      label: hourLabel(h.timestamp),
      observed: h.demand,
    }));
    const fc = data.forecast.map((f) => ({
      t: f.timestamp,
      label: hourLabel(f.timestamp),
      forecast: f.forecast,
      band: f.lower != null && f.upper != null ? [f.lower, f.upper] : undefined,
      peak: f.peak_flag ? f.forecast : undefined,
    }));
    return [...hist, ...fc];
  }, [data]);

  return (
    <div className="grid gap-5">
      <Card
        title="Next 24 hours"
        subtitle="Observed history (7 days) and the model's 24-hour-ahead forecast with its empirical interval. Diamonds mark peak-flagged hours."
      >
        <div className="h-[460px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 16, bottom: 0, left: -8 }}>
              <defs>
                <linearGradient id="bandFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#34d399" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#34d399" stopOpacity={0.03} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" />
              <XAxis dataKey="label" tick={{ fill: "#8a97ab", fontSize: 11 }} minTickGap={28} />
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
              <Area
                type="monotone"
                dataKey="band"
                name="Empirical interval"
                stroke="none"
                fill="url(#bandFill)"
                connectNulls
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="observed"
                name="Observed history"
                stroke="#60a5fa"
                strokeWidth={2}
                dot={false}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="forecast"
                name="24h forecast"
                stroke="#34d399"
                strokeWidth={2.5}
                dot={{ r: 2 }}
                connectNulls
              />
              <Scatter dataKey="peak" name="Peak flag" fill="#f59e0b" shape="diamond" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-3 text-xs text-[var(--color-muted)]">
          {data.summary.peak_hours} forecast hours exceed the training-period 90th-percentile
          threshold ({data.summary.peak_threshold.toFixed(2)} units). This is a statistical flag,
          not a grid alert.
        </p>
      </Card>
    </div>
  );
}
