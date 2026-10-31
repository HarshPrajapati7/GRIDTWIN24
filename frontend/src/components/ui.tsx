import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
  title,
  subtitle,
  action,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div
      className={`gt-fade rounded-2xl border border-[var(--color-line)] bg-[var(--color-panel)]/80 backdrop-blur p-5 shadow-[0_8px_30px_rgba(0,0,0,0.25)] ${className}`}
    >
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-100">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-[var(--color-muted)]">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

export function Stat({
  label,
  value,
  sub,
  accent = "default",
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: "default" | "amber" | "green" | "blue";
}) {
  const accentMap: Record<string, string> = {
    default: "text-slate-100",
    amber: "text-[var(--color-accent)]",
    green: "text-[var(--color-accent-2)]",
    blue: "text-[var(--color-info)]",
  };
  return (
    <div className="gt-fade rounded-2xl border border-[var(--color-line)] bg-[var(--color-panel)]/80 p-4 backdrop-blur">
      <div className="text-[11px] uppercase tracking-wider text-[var(--color-muted)]">{label}</div>
      <div className={`mt-1 text-2xl font-bold tabular-nums ${accentMap[accent]}`}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-[var(--color-muted)]">{sub}</div>}
    </div>
  );
}

export function Badge({
  children,
  tone = "default",
}: {
  children: ReactNode;
  tone?: "default" | "green" | "amber";
}) {
  const toneMap: Record<string, string> = {
    default: "border-[var(--color-info)]/40 text-[var(--color-info)]",
    green: "border-[var(--color-accent-2)]/40 text-[var(--color-accent-2)]",
    amber: "border-[var(--color-accent)]/40 text-[var(--color-accent)]",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border bg-[var(--color-panel-2)] px-2.5 py-1 text-[11px] font-semibold ${toneMap[tone]}`}
    >
      {children}
    </span>
  );
}

export function Button({
  children,
  onClick,
  disabled,
  loading,
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading && (
        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-black/40 border-t-black" />
      )}
      {children}
    </button>
  );
}

export function NumberField({
  label,
  value,
  onChange,
  step = 0.1,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: number;
  min?: number;
  max?: number;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-[var(--color-muted)]">{label}</span>
      <input
        type="number"
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(e) => onChange(Number(e.target.value))}
        className="rounded-lg border border-[var(--color-line)] bg-[var(--color-ink)] px-3 py-2 text-sm text-slate-100 outline-none focus:border-[var(--color-accent)]"
      />
    </label>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-[var(--color-muted)]">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--color-line)] border-t-[var(--color-accent)]" />
      {label}
    </div>
  );
}
