import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { api } from "../api";
import type { LoadShiftResponse } from "../api";
import { Card, Button, NumberField, Stat, Spinner } from "./ui";

export function LoadShiftTab() {
  const [baseLoad, setBaseLoad] = useState(1.2);
  const [capacity, setCapacity] = useState(2.0);
  const [offpeak, setOffpeak] = useState(3.0);
  const [peak, setPeak] = useState(7.0);
  const [result, setResult] = useState<LoadShiftResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.loadShift({
        base_load_kw: baseLoad,
        capacity_kw: capacity,
        offpeak_tariff: offpeak,
        peak_tariff: peak,
      });
      setResult(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const chartData = result
    ? result.scheduled_load_kw.map((v, h) => ({
        hour: `${h}:00`,
        baseline: result.baseline_load_with_earliest_tasks_kw[h],
        shifted: v,
      }))
    : [];

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <Card
        title="Flexible-load scenario"
        subtitle="Local-site scenario, separate from the grid dataset. Illustrative only."
        className="lg:col-span-1"
      >
        <div className="grid gap-3">
          <NumberField label="Base load (kW)" value={baseLoad} onChange={setBaseLoad} min={0.2} />
          <NumberField label="Peak capacity (kW)" value={capacity} onChange={setCapacity} min={0.2} />
          <NumberField label="Off-peak tariff (per kWh)" value={offpeak} onChange={setOffpeak} min={0} />
          <NumberField label="Peak tariff (per kWh)" value={peak} onChange={setPeak} min={0} />
          <div className="pt-1">
            <Button onClick={run} loading={loading}>
              Run scenario
            </Button>
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
      </Card>

      <Card title="Shifted schedule" className="lg:col-span-2">
        {loading && <Spinner label="Scheduling flexible loads..." />}
        {!loading && !result && (
          <p className="text-sm text-[var(--color-muted)]">
            Set parameters and run the scenario to see the optimised schedule.
          </p>
        )}
        {result && (
          <div className="grid gap-4">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <Stat label="Baseline cost" value={result.baseline_cost.toFixed(2)} />
              <Stat label="Scheduled cost" value={result.scheduled_cost.toFixed(2)} accent="green" />
              <Stat
                label="Estimated change"
                value={result.estimated_cost_difference.toFixed(2)}
                accent="amber"
              />
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" />
                  <XAxis dataKey="hour" tick={{ fill: "#8a97ab", fontSize: 11 }} minTickGap={16} />
                  <YAxis tick={{ fill: "#8a97ab", fontSize: 11 }} width={48} />
                  <Tooltip
                    contentStyle={{
                      background: "#121824",
                      border: "1px solid #232d3f",
                      borderRadius: 12,
                      color: "#e6eaf1",
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="baseline" name="Baseline" fill="#8a97ab" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="shifted" name="Shifted" fill="#34d399" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-[var(--color-muted)]">{result.note}</p>
          </div>
        )}
      </Card>
    </div>
  );
}
