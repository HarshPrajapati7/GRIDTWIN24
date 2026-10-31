import { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { api } from "../api";
import type { BatteryResponse } from "../api";
import { Card, Button, NumberField, Stat, Spinner } from "./ui";

export function BatteryTab() {
  const [capacity, setCapacity] = useState(8.0);
  const [power, setPower] = useState(2.0);
  const [demandCharge, setDemandCharge] = useState(20.0);
  const [result, setResult] = useState<BatteryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.battery({
        battery_capacity_kwh: capacity,
        max_power_kw: power,
        demand_charge_per_kw: demandCharge,
      });
      setResult(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const dispatchData = result
    ? result.optimised_grid_import_kw.map((v, h) => ({
        hour: `${h}`,
        baseline: result.baseline_grid_import_kw[h],
        optimised: v,
        pv: result.pv_kw[h],
      }))
    : [];
  const socData = result
    ? result.battery_soc_kwh.map((v, h) => ({ hour: `${h}`, soc: v }))
    : [];

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <Card
        title="PV + battery dispatch"
        subtitle="LP optimiser (scipy HiGHS). Synthetic site profile; does not control a real battery."
        className="lg:col-span-1"
      >
        <div className="grid gap-3">
          <NumberField label="Battery capacity (kWh)" value={capacity} onChange={setCapacity} min={1} step={1} />
          <NumberField label="Charge/discharge limit (kW)" value={power} onChange={setPower} min={0.5} step={0.5} />
          <NumberField
            label="Daily peak charge (per kW)"
            value={demandCharge}
            onChange={setDemandCharge}
            min={0}
            step={5}
          />
          <div className="pt-1">
            <Button onClick={run} loading={loading}>
              Optimise dispatch
            </Button>
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
      </Card>

      <div className="grid gap-5 lg:col-span-2">
        <Card title="Grid import — baseline vs optimised">
          {loading && <Spinner label="Solving linear program..." />}
          {!loading && !result && (
            <p className="text-sm text-[var(--color-muted)]">
              Set parameters and optimise to see the dispatch plan.
            </p>
          )}
          {result && (
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                <Stat
                  label="Bill delta"
                  value={result.estimated_cost_difference.toFixed(2)}
                  accent="green"
                />
                <Stat
                  label="Peak reduction"
                  value={`${result.peak_reduction_kw.toFixed(2)} kW`}
                  accent="amber"
                />
                <Stat
                  label="Optimised peak"
                  value={`${result.optimised_peak_import_kw.toFixed(2)} kW`}
                  accent="blue"
                />
              </div>
              <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={dispatchData} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
                    <defs>
                      <linearGradient id="pvFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" />
                    <XAxis dataKey="hour" tick={{ fill: "#8a97ab", fontSize: 11 }} />
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
                    <Area type="monotone" dataKey="pv" name="PV generation" stroke="#f59e0b" fill="url(#pvFill)" />
                    <Line type="monotone" dataKey="baseline" name="Grid import — no battery" stroke="#8a97ab" strokeWidth={1.5} strokeDasharray="5 4" dot={false} />
                    <Line type="monotone" dataKey="optimised" name="Grid import — optimised" stroke="#34d399" strokeWidth={2.5} dot={false} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </Card>

        {result && (
          <Card title="Battery state of charge">
            <div className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={socData} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
                  <defs>
                    <linearGradient id="socFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#60a5fa" stopOpacity={0.03} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#232d3f" />
                  <XAxis dataKey="hour" tick={{ fill: "#8a97ab", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#8a97ab", fontSize: 11 }} width={48} />
                  <Tooltip
                    contentStyle={{
                      background: "#121824",
                      border: "1px solid #232d3f",
                      borderRadius: 12,
                      color: "#e6eaf1",
                    }}
                  />
                  <Area type="monotone" dataKey="soc" name="Stored energy (kWh)" stroke="#60a5fa" fill="url(#socFill)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-3 text-xs text-[var(--color-muted)]">{result.note}</p>
          </Card>
        )}
      </div>
    </div>
  );
}
