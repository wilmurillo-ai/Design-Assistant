import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Trade } from "@/types/dashboard";
import { formatUSD, formatTime, exchangeName } from "@/lib/format";

interface Props {
  trades: Trade[];
}

const typeStyles: Record<string, string> = {
  open: "bg-primary/20 text-primary border-primary/30",
  close: "bg-profit/20 text-profit border-profit/30",
  switch: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
};

const typeLabels: Record<string, string> = {
  open: "OPEN",
  close: "CLOSE",
  switch: "SWITCH",
};

export function TradeHistory({ trades }: Props) {
  const sorted = [...trades].sort(
    (a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()
  );

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg">Trade History</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-muted-foreground">Time</TableHead>
              <TableHead className="text-muted-foreground">Type</TableHead>
              <TableHead className="text-muted-foreground">Coin</TableHead>
              <TableHead className="text-muted-foreground">Direction</TableHead>
              <TableHead className="text-right text-muted-foreground">
                Size
              </TableHead>
              <TableHead className="text-right text-muted-foreground">
                PnL
              </TableHead>
              <TableHead className="text-muted-foreground">Reason</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((trade, i) => (
              <TableRow key={i} className="border-border hover:bg-secondary/50">
                <TableCell className="font-mono text-sm text-muted-foreground whitespace-nowrap">
                  {formatTime(trade.time)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${typeStyles[trade.type]}`}
                  >
                    {typeLabels[trade.type]}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono font-semibold">
                  {trade.coin}
                </TableCell>
                <TableCell className="text-sm">
                  <span className="text-profit">
                    L:{exchangeName(trade.direction.long_exchange).slice(0, 2)}
                  </span>
                  {" / "}
                  <span className="text-loss">
                    S:{exchangeName(trade.direction.short_exchange).slice(0, 2)}
                  </span>
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {trade.size}
                </TableCell>
                <TableCell
                  className={`text-right font-mono text-sm ${
                    trade.pnl != null
                      ? trade.pnl >= 0
                        ? "text-profit"
                        : "text-loss"
                      : "text-muted-foreground"
                  }`}
                >
                  {trade.pnl != null ? formatUSD(trade.pnl) : "---"}
                </TableCell>
                <TableCell className="max-w-[280px] truncate text-xs text-muted-foreground">
                  {trade.reason}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
