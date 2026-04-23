export function providerSymbolsMap(providerResult) {
  return providerResult?.symbols ?? {};
}

export function providerRowsMap(providerResult) {
  const out = {};
  for (const [symbol, item] of Object.entries(providerSymbolsMap(providerResult))) {
    out[symbol] = item?.bars ?? [];
  }
  return out;
}

export function isFreshSymbol(item) {
  return item?.status === 'ok' && item?.freshness?.freshness_status === 'fresh';
}

export function staleSymbols(providerResult) {
  return Object.entries(providerSymbolsMap(providerResult))
    .filter(([, item]) => item?.status === 'stale')
    .map(([symbol]) => symbol);
}
