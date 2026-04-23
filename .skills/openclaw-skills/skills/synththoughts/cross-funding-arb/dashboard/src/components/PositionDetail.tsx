import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Position, PositionLeg } from "@/types/dashboard";
import {
  formatUSD,
  formatPct,
  formatRate,
  formatNum,
  exchangeName,
} from "@/lib/format";

interface Props {
  position: Position | null;
}

function InfoRow({
  label,
  value,
  color,
  mono = false,
  small = false,
}: {
  label: string;
  value: string;
  color?: "profit" | "loss" | "warn" | "muted";
  mono?: boolean;
  small?: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className={`${small ? "text-xs" : "text-sm"} text-muted-foreground`}>
        {label}
      </span>
      <span
        className={`${small ? "text-xs" : "text-sm"} font-medium ${mono ? "font-mono" : ""} ${
          color === "profit"
            ? "text-profit"
            : color === "loss"
              ? "text-loss"
              : color === "warn"
                ? "text-yellow-400"
                : color === "muted"
                  ? "text-muted-foreground"
                  : "text-foreground"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

/** Color helper for a cell value */
function cellColor(color?: "profit" | "loss" | "warn" | "muted") {
  if (color === "profit") return "text-profit";
  if (color === "loss") return "text-loss";
  if (color === "warn") return "text-yellow-400";
  if (color === "muted") return "text-muted-foreground";
  return "text-foreground";
}

/** A single row in the 3-col comparison: leftVal | label | rightVal */
function CompareRow({
  label,
  leftVal,
  rightVal,
  leftColor,
  rightColor,
}: {
  label: string;
  leftVal: string;
  rightVal: string;
  leftColor?: "profit" | "loss" | "warn" | "muted";
  rightColor?: "profit" | "loss" | "warn" | "muted";
}) {
  return (
    <div className="grid grid-cols-[110px_1fr_1fr] gap-x-2 items-center py-[3px]">
      <span className="text-xs text-muted-foreground whitespace-nowrap">
        {label}
      </span>
      <span className={`text-xs font-mono font-medium text-right ${cellColor(leftColor)}`}>
        {leftVal}
      </span>
      <span className={`text-xs font-mono font-medium text-right ${cellColor(rightColor)}`}>
        {rightVal}
      </span>
    </div>
  );
}

/** Section divider in comparison table */
function CompareDivider({ label }: { label: string }) {
  return (
    <div className="mt-2 pt-2 border-t border-border/30">
      <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
        {label}
      </span>
    </div>
  );
}

function formatSettleCountdown(min: number) {
  return min >= 60 ? `${Math.floor(min / 60)}h ${min % 60}m` : `${min}m`;
}

function fundingRateColor(leg: PositionLeg) {
  const isLong = leg.side === "long";
  // positive rate: longs pay shorts. Negative rate: shorts pay longs.
  return leg.funding_rate >= 0
    ? isLong ? "loss" as const : "profit" as const
    : isLong ? "profit" as const : "loss" as const;
}

function pnlColor(v: number) {
  return v >= 0 ? "profit" as const : "loss" as const;
}

function signUSD(v: number) {
  const rounded = Math.round(v * 100) / 100;
  return `${rounded >= 0 ? "+" : ""}${formatUSD(rounded)}`;
}

function NoPosition() {
  return (
    <Card className="border-border bg-card shadow-md shadow-black/20">
      <CardHeader>
        <CardTitle className="text-lg">Current Position</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
          <div className="text-4xl mb-2 opacity-30">---</div>
          <p className="text-sm">No active position</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function PositionDetail({ position }: Props) {
  if (!position || !position.has_position) return <NoPosition />;

  const { long_leg, short_leg } = position;
  const totalPnlColor = position.total_pnl >= 0 ? "profit" : "loss";
  const isDeltaNeutral = position.delta_neutral;

  return (
    <Card className="border-border bg-card shadow-md shadow-black/20">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <div className="flex items-center gap-3">
          <CardTitle className="text-lg">Current Position</CardTitle>
          <span className="text-2xl font-bold font-mono">{position.coin}</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className={`text-[10px] ${
              isDeltaNeutral
                ? "border-profit/50 text-profit bg-profit/10"
                : "border-yellow-500/50 text-yellow-400 bg-yellow-500/10"
            }`}
          >
            {isDeltaNeutral ? "DELTA NEUTRAL" : "EXPOSED"}
          </Badge>
          <Badge
            variant="outline"
            className="border-profit/50 text-profit bg-profit/10"
          >
            ACTIVE
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-[5fr_3fr]">
          {/* Left: Comparison table */}
          <div className="rounded-lg border border-border/50 bg-secondary/20 px-4 py-3">
            {/* Headers */}
            <div className="grid grid-cols-[110px_1fr_1fr] gap-x-2 items-center pb-2 mb-2 border-b border-border/40">
              <span />
              <div className="flex items-center justify-end gap-2">
                <span className="text-sm font-semibold">
                  {exchangeName(long_leg.exchange)}
                </span>
                <Badge
                  variant="outline"
                  className="text-[10px] px-1.5 py-0 border-profit/40 text-profit"
                >
                  LONG
                </Badge>
              </div>
              <div className="flex items-center justify-end gap-1.5">
                <span className="text-sm font-semibold">
                  {exchangeName(short_leg.exchange)}
                </span>
                <Badge
                  variant="outline"
                  className="text-[10px] px-1.5 py-0 border-loss/40 text-loss"
                >
                  SHORT
                </Badge>
              </div>
            </div>

            {/* Position rows */}
            <CompareRow
              label="Leverage"
              leftVal={`${long_leg.leverage}x`}
              rightVal={`${short_leg.leverage}x`}
            />
            <CompareRow
              label="Size"
              leftVal={`${formatNum(long_leg.size, 4)} ${position.coin}`}
              rightVal={`${formatNum(short_leg.size, 4)} ${position.coin}`}
            />
            <CompareRow
              label="Entry Price"
              leftVal={formatUSD(long_leg.entry_price)}
              rightVal={formatUSD(short_leg.entry_price)}
            />
            <CompareRow
              label="Mark Price"
              leftVal={formatUSD(long_leg.current_price)}
              rightVal={formatUSD(short_leg.current_price)}
            />
            <CompareRow
              label="Notional"
              leftVal={formatUSD(long_leg.notional)}
              rightVal={formatUSD(short_leg.notional)}
            />
            <CompareRow
              label="Price PnL"
              leftVal={signUSD(long_leg.unrealized_pnl)}
              rightVal={signUSD(short_leg.unrealized_pnl)}
              leftColor={pnlColor(long_leg.unrealized_pnl)}
              rightColor={pnlColor(short_leg.unrealized_pnl)}
            />

            {/* Funding section */}
            <CompareDivider label="Funding" />
            <CompareRow
              label="Rate"
              leftVal={formatRate(long_leg.funding_rate)}
              rightVal={formatRate(short_leg.funding_rate)}
              leftColor={fundingRateColor(long_leg)}
              rightColor={fundingRateColor(short_leg)}
            />
            <CompareRow
              label="Settlement"
              leftVal={`Every ${long_leg.settlement_cycle_h}h`}
              rightVal={`Every ${short_leg.settlement_cycle_h}h`}
              leftColor="muted"
              rightColor="muted"
            />
            <CompareRow
              label="Next In"
              leftVal={formatSettleCountdown(long_leg.next_settlement_min)}
              rightVal={formatSettleCountdown(short_leg.next_settlement_min)}
              leftColor={long_leg.next_settlement_min <= 5 ? "warn" : "muted"}
              rightColor={short_leg.next_settlement_min <= 5 ? "warn" : "muted"}
            />
            <CompareRow
              label="Earned"
              leftVal={`${signUSD(long_leg.accumulated_funding)} (${long_leg.funding_payments}×)`}
              rightVal={`${signUSD(short_leg.accumulated_funding)} (${short_leg.funding_payments}×)`}
              leftColor={pnlColor(long_leg.accumulated_funding)}
              rightColor={pnlColor(short_leg.accumulated_funding)}
            />
          </div>

          {/* Right: Aggregate panels stacked */}
          <div className="flex flex-col gap-3">
            {/* Total PnL */}
            <div className={`rounded-lg border px-4 py-3 ${
              totalPnlColor === "profit"
                ? "border-profit/20 bg-profit/[0.04]"
                : "border-loss/20 bg-loss/[0.04]"
            }`}>
              <p className="text-[11px] text-muted-foreground uppercase tracking-wider font-medium mb-1.5">Position PnL</p>
              <p
                className={`text-3xl font-bold font-mono leading-tight ${
                  totalPnlColor === "profit" ? "text-profit" : "text-loss"
                }`}
              >
                {signUSD(position.total_pnl)}
              </p>
              <p
                className={`text-sm font-mono mt-0.5 ${
                  totalPnlColor === "profit" ? "text-profit/80" : "text-loss/80"
                }`}
              >
                {formatPct(position.roi_pct)}
              </p>
              <div className="mt-3 pt-2.5 border-t border-border/30 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Funding PnL</span>
                  <span className={`font-mono font-medium ${cellColor(pnlColor(position.total_funding_pnl))}`}>
                    {signUSD(position.total_funding_pnl)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Price PnL</span>
                  <span className={`font-mono font-medium ${cellColor(pnlColor(position.total_price_pnl))}`}>
                    {signUSD(position.total_price_pnl)}
                  </span>
                </div>
              </div>
            </div>

            {/* Spread & Yield */}
            <div className="rounded-lg border border-border/50 bg-secondary/20 px-4 py-3">
              <p className="text-[11px] text-muted-foreground uppercase tracking-wider font-medium mb-1">Spread & Yield</p>
              <InfoRow
                label="Entry Spread"
                value={`${(position.entry_spread * 100).toFixed(4)}%`}
                mono
                small
              />
              <InfoRow
                label="Current Spread"
                value={`${(position.current_spread * 100).toFixed(4)}%`}
                mono
                small
              />
              <InfoRow
                label="Current APR"
                value={formatPct(position.current_apr)}
                color="profit"
                mono
                small
              />
              <InfoRow
                label="Est. Daily"
                value={`${formatUSD(position.projected_daily_usd)}/day`}
                color="profit"
                mono
                small
              />
            </div>

          </div>
        </div>
      </CardContent>
    </Card>
  );
}
