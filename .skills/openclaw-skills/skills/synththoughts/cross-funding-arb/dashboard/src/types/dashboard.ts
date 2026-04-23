export interface DashboardData {
  updated_at: string;
  summary: Summary;
  position: Position | null;
  opportunities: Opportunity[];
  trades: Trade[];
}

export interface Summary {
  total_invested: number;
  current_value: number;
  total_pnl: number;
  roi_pct: number;
  annualized_roi_pct: number;
  hl_balance: number;
  bn_balance: number;
}

export interface PositionLeg {
  exchange: string;
  side: "long" | "short";
  size: number;
  entry_price: number;
  current_price: number;
  notional: number; // current size * current price
  unrealized_pnl: number; // price movement PnL
  leverage: number;
  funding_rate: number; // current period rate
  settlement_cycle_h: number; // 1 for HL, 8 for BN
  next_settlement_min: number; // minutes until next settlement
  accumulated_funding: number; // total funding earned/paid since entry (USD)
  funding_payments: number; // number of settlements since entry
}

export interface Position {
  has_position: boolean;
  coin: string;
  direction: Direction;
  entry_time: string;
  entry_spread: number;
  current_spread: number;

  long_leg: PositionLeg;
  short_leg: PositionLeg;

  // Delta neutrality
  delta_neutral: boolean;
  delta_exposure: number; // absolute size difference
  delta_exposure_pct: number; // as % of position size

  // Aggregate PnL
  total_funding_pnl: number; // sum of both legs' accumulated_funding
  total_price_pnl: number; // sum of both legs' unrealized_pnl
  total_pnl: number; // funding + price
  roi_pct: number;
  current_apr: number; // annualized from funding rate spread
  projected_daily_usd: number; // expected daily funding income
}

export interface Direction {
  long_exchange: string;
  short_exchange: string;
}

export interface Opportunity {
  coin: string;
  estimated_apr: number;
  long_exchange: string;
  short_exchange: string;
  spread: number;
  confidence: "high" | "medium" | "low";
  hl_rate: number;
  bn_rate: number;
}

export interface Trade {
  time: string;
  type: "open" | "close" | "switch";
  coin: string;
  direction: Direction;
  size: number;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  reason: string;
}
