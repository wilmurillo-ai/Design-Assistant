import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Summary } from "@/types/dashboard";
import { formatUSD, formatPct } from "@/lib/format";
import {
  DollarSign,
  TrendingUp,
  Wallet,
  BarChart3,
} from "lucide-react";

interface Props {
  summary: Summary;
}

interface StatCard {
  title: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
  color?: "profit" | "loss" | "default";
}

export function SummaryCards({ summary }: Props) {
  const pnlColor = summary.total_pnl >= 0 ? "profit" : "loss";

  const cards: StatCard[] = [
    {
      title: "Total Invested",
      value: formatUSD(summary.total_invested),
      sub: `HL ${formatUSD(summary.hl_balance)} / BN ${formatUSD(summary.bn_balance)}`,
      icon: <DollarSign className="h-4 w-4" />,
    },
    {
      title: "Current Value",
      value: formatUSD(summary.current_value),
      sub: `ROI ${formatPct(summary.roi_pct)}`,
      icon: <Wallet className="h-4 w-4" />,
    },
    {
      title: "Total PnL",
      value: formatUSD(summary.total_pnl),
      icon: <TrendingUp className="h-4 w-4" />,
      color: pnlColor,
    },
    {
      title: "Annualized ROI",
      value: formatPct(summary.annualized_roi_pct),
      icon: <BarChart3 className="h-4 w-4" />,
      color: summary.annualized_roi_pct >= 0 ? "profit" : "loss",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title} className="border-border bg-card shadow-sm shadow-black/10">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardDescription className="text-muted-foreground text-sm">
              {card.title}
            </CardDescription>
            <span className="text-muted-foreground">{card.icon}</span>
          </CardHeader>
          <CardContent>
            <CardTitle
              className={`font-mono text-2xl font-bold ${
                card.color === "profit"
                  ? "text-profit"
                  : card.color === "loss"
                    ? "text-loss"
                    : "text-foreground"
              }`}
            >
              {card.value}
            </CardTitle>
            {card.sub && (
              <p className="mt-1 text-xs text-muted-foreground">{card.sub}</p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
