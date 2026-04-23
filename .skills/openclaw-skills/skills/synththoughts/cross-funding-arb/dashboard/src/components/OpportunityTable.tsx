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
import type { Opportunity } from "@/types/dashboard";
import { exchangeName, formatRate } from "@/lib/format";

interface Props {
  opportunities: Opportunity[];
  currentCoin: string | null;
}

const confidenceColor: Record<string, string> = {
  high: "bg-profit/20 text-profit border-profit/30",
  medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  low: "bg-muted-foreground/20 text-muted-foreground border-muted-foreground/30",
};

export function OpportunityTable({ opportunities, currentCoin }: Props) {
  const sorted = [...opportunities].sort(
    (a, b) => b.estimated_apr - a.estimated_apr
  );

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg">Arbitrage Opportunities</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-muted-foreground">Coin</TableHead>
              <TableHead className="text-muted-foreground">Long</TableHead>
              <TableHead className="text-muted-foreground">Short</TableHead>
              <TableHead className="text-right text-muted-foreground">
                Est. APR
              </TableHead>
              <TableHead className="text-center text-muted-foreground">
                Confidence
              </TableHead>
              <TableHead className="text-right text-muted-foreground">
                Spread
              </TableHead>
              <TableHead className="text-right text-muted-foreground">
                HL Rate
              </TableHead>
              <TableHead className="text-right text-muted-foreground">
                BN Rate
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((opp) => {
              const isHighApr = opp.estimated_apr >= 20;
              const isCurrent = opp.coin === currentCoin;
              return (
                <TableRow
                  key={opp.coin}
                  className={`border-border ${
                    isHighApr
                      ? "bg-primary/5 hover:bg-primary/10"
                      : "hover:bg-secondary/50"
                  }`}
                >
                  <TableCell className="font-mono font-semibold">
                    <span className="flex items-center gap-2">
                      {opp.coin}
                      {isCurrent && (
                        <Badge
                          variant="outline"
                          className="border-primary/50 text-primary text-[10px] px-1.5 py-0"
                        >
                          ACTIVE
                        </Badge>
                      )}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm">
                    {exchangeName(opp.long_exchange)}
                  </TableCell>
                  <TableCell className="text-sm">
                    {exchangeName(opp.short_exchange)}
                  </TableCell>
                  <TableCell
                    className={`text-right font-mono font-semibold ${
                      isHighApr ? "text-profit" : "text-foreground"
                    }`}
                  >
                    {opp.estimated_apr.toFixed(1)}%
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${confidenceColor[opp.confidence]}`}
                    >
                      {opp.confidence.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {(opp.spread * 100).toFixed(2)}%
                  </TableCell>
                  <TableCell
                    className={`text-right font-mono text-sm ${
                      opp.hl_rate < 0 ? "text-loss" : "text-profit"
                    }`}
                  >
                    {formatRate(opp.hl_rate)}
                  </TableCell>
                  <TableCell
                    className={`text-right font-mono text-sm ${
                      opp.bn_rate < 0 ? "text-loss" : "text-profit"
                    }`}
                  >
                    {formatRate(opp.bn_rate)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
