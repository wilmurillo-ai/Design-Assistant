import { useDashboardData } from "@/hooks/useDashboardData";
import { SummaryCards } from "@/components/SummaryCards";
import { OpportunityTable } from "@/components/OpportunityTable";
import { PositionDetail } from "@/components/PositionDetail";
import { TradeHistory } from "@/components/TradeHistory";

function LoadingState() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <div className="mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent mx-auto" />
        <p className="text-sm text-muted-foreground">Loading dashboard...</p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <p className="text-lg font-semibold text-loss">Error</p>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

export function Dashboard() {
  const { data, loading, error } = useDashboardData();

  if (loading) return <LoadingState />;
  if (error || !data) return <ErrorState message={error ?? "No data"} />;

  const updatedAt = new Date(data.updated_at).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              Funding Rate Arbitrage
            </h1>
            <p className="text-sm text-muted-foreground">
              Cross-exchange funding rate strategy dashboard
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-profit animate-pulse" />
            <span className="text-xs text-muted-foreground">
              Updated {updatedAt}
            </span>
          </div>
        </div>

        {/* Summary Cards */}
        <section className="mb-8">
          <SummaryCards summary={data.summary} />
        </section>

        {/* Position Detail */}
        <section className="mb-8">
          <PositionDetail position={data.position} />
        </section>

        {/* Opportunities */}
        <section className="mb-8">
          <OpportunityTable
            opportunities={data.opportunities}
            currentCoin={data.position?.coin ?? null}
          />
        </section>

        {/* Trade History */}
        <section className="mb-6">
          <TradeHistory trades={data.trades} />
        </section>
      </div>
    </div>
  );
}
