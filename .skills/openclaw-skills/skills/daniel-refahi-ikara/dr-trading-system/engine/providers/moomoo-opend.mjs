import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

function normalizeRows(result) {
  if (!result || !Array.isArray(result.rows)) return [];
  return result.rows.map((row) => ({
    date: row.date,
    open: Number(row.open),
    high: Number(row.high),
    low: Number(row.low),
    close: Number(row.close),
    volume: Number(row.volume)
  })).filter((row) => Number.isFinite(row.open) && Number.isFinite(row.high) && Number.isFinite(row.low) && Number.isFinite(row.close) && Number.isFinite(row.volume));
}

function daysBetween(dateA, dateB) {
  const a = new Date(`${dateA}T00:00:00Z`);
  const b = new Date(`${dateB}T00:00:00Z`);
  return Math.floor((a - b) / 86400000);
}

function classifyStatus(item, rows, staleDays, maxStaleDays) {
  const error = item?.error ?? '';
  if (error.includes('No right to get the quote')) return 'permission_denied';
  if (error.includes('code is wrong') || error.includes('stock code') || error.includes('incorrect')) return 'symbol_invalid';
  if (!item?.ok && error) return 'provider_error';
  if (!rows.length) return 'empty';
  if (staleDays != null && staleDays > maxStaleDays) return 'stale';
  return 'ok';
}

export async function fetchMoomooOpenDData({
  market,
  symbols,
  lookbackDays = 80,
  asOfDate = null,
  maxStaleDays = 7,
  connection
}) {
  const pythonBin = connection?.python_bin;
  const host = connection?.host ?? '127.0.0.1';
  const port = connection?.port ?? 11111;

  if (!pythonBin) throw new Error('moomoo_opend adapter requires connection.python_bin');

  const script = String.raw`
from futu import OpenQuoteContext, KLType, AuType
import json, sys
symbols = json.loads(sys.argv[1])
lookback = int(sys.argv[2])
host = sys.argv[3]
port = int(sys.argv[4])
ctx = OpenQuoteContext(host=host, port=port)
out = {}
for symbol in symbols:
    try:
        result = ctx.request_history_kline(symbol, ktype=KLType.K_DAY, max_count=lookback, autype=AuType.QFQ)
        ret, data, *rest = result
        if ret != 0:
            out[symbol] = {"ok": False, "error": str(data)}
            continue
        rows = []
        for _, r in data.iterrows():
            rows.append({
                "date": str(r['time_key']).split(' ')[0],
                "open": float(r['open']),
                "high": float(r['high']),
                "low": float(r['low']),
                "close": float(r['close']),
                "volume": float(r['volume'])
            })
        out[symbol] = {"ok": True, "rows": rows}
    except Exception as e:
        out[symbol] = {"ok": False, "error": str(e)}
ctx.close()
print(json.dumps(out))
`;

  const { stdout } = await execFileAsync(pythonBin, ['-c', script, JSON.stringify(symbols), String(lookbackDays), String(host), String(port)], { maxBuffer: 1024 * 1024 * 20 });
  const start = stdout.indexOf('{');
  const end = stdout.lastIndexOf('}');
  if (start === -1 || end === -1 || end < start) throw new Error('moomoo_opend adapter did not receive JSON payload');
  const parsed = JSON.parse(stdout.slice(start, end + 1));

  const symbolData = {};
  let okCount = 0;
  let staleCount = 0;
  let permissionCount = 0;
  let failedCount = 0;

  for (const symbol of symbols) {
    const item = parsed[symbol] ?? { ok: false, error: 'missing provider response' };
    const rows = normalizeRows(item);
    const latestBarDate = rows.length ? rows[rows.length - 1].date : null;
    const staleDays = asOfDate && latestBarDate ? daysBetween(asOfDate, latestBarDate) : null;
    const status = classifyStatus(item, rows, staleDays, maxStaleDays);

    if (status === 'ok') okCount += 1;
    else if (status === 'stale') staleCount += 1;
    else if (status === 'permission_denied') permissionCount += 1;
    else failedCount += 1;

    symbolData[symbol] = {
      provider: 'moomoo_opend',
      market,
      symbol_requested: symbol,
      symbol_provider: symbol,
      status,
      error_code: status === 'permission_denied' ? 'permission_denied' : status === 'symbol_invalid' ? 'symbol_invalid' : status === 'provider_error' ? 'provider_error' : null,
      error_message: item?.error ?? null,
      freshness: {
        latest_bar_date: latestBarDate,
        as_of_date: asOfDate,
        stale_days: staleDays,
        freshness_status: latestBarDate == null ? 'unknown' : staleDays != null && staleDays > maxStaleDays ? 'stale' : 'fresh'
      },
      bars: rows
    };
  }

  const overallStatus = permissionCount === symbols.length ? 'permission_denied' : okCount > 0 && (staleCount > 0 || failedCount > 0 || permissionCount > 0) ? 'partial' : okCount > 0 ? 'ok' : staleCount === symbols.length ? 'stale' : 'failed';

  return {
    provider_summary: {
      provider: 'moomoo_opend',
      market,
      symbols_requested: symbols.length,
      symbols_ok: okCount,
      symbols_stale: staleCount,
      symbols_permission_denied: permissionCount,
      symbols_failed: failedCount,
      overall_status: overallStatus
    },
    symbols: symbolData
  };
}
