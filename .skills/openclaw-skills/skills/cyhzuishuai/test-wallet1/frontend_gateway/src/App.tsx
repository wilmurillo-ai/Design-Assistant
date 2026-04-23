import React, { useState, useEffect } from 'react';
import { Shield, Send, CreditCard, Settings, LogOut, CheckCircle, AlertCircle, RefreshCw, ChevronDown, ChevronRight, Copy } from 'lucide-react';
import './index.css';

function formatPreviewJson(value: any) {
  return JSON.stringify(value, null, 2);
}

type WalletAsset = {
  chain: string;
  contract_address: string;
  symbol: string;
  balance_str?: string;
  decimals: number;
  ui_balance?: number;
};

const NATIVE_ASSET_META: Record<string, { symbol: string; decimals: number }> = {
  ethereum: { symbol: 'ETH', decimals: 18 },
  base: { symbol: 'ETH', decimals: 18 },
  bsc: { symbol: 'BNB', decimals: 18 },
  solana: { symbol: 'SOL', decimals: 9 },
  sui: { symbol: 'SUI', decimals: 9 },
};

function normalizeGatewayAssets(snapshot: any): Record<string, WalletAsset[]> {
  const grouped: Record<string, WalletAsset[]> = {};
  for (const entry of Object.values(snapshot || {})) {
    const items = Array.isArray((entry as any)?.Assets) ? (entry as any).Assets : [];
    for (const item of items) {
      const chain = String(item?.chain || '').toLowerCase().trim();
      const contract = String(item?.contract_address || '').trim();
      if (!chain || !contract) continue;
      grouped[chain] ||= [];
      if (grouped[chain].some(existing => existing.contract_address === contract)) continue;
      grouped[chain].push(item as WalletAsset);
    }
  }
  return grouped;
}

function getNativeAsset(chain: string): WalletAsset {
  const meta = NATIVE_ASSET_META[chain] || { symbol: 'NATIVE', decimals: 18 };
  return {
    chain,
    contract_address: 'native',
    symbol: meta.symbol,
    decimals: meta.decimals,
    ui_balance: 0,
  };
}

function parseDisplayAmountToAtomic(value: string, decimals: number): { atomic: string; error: string } {
  const normalized = value.trim();
  if (!normalized) {
    return { atomic: '', error: '' };
  }
  if (!/^\d+(\.\d+)?$/.test(normalized)) {
    return { atomic: '', error: 'Amount must be a positive decimal number.' };
  }

  const [wholePart, fracPart = ''] = normalized.split('.');
  if (fracPart.length > decimals) {
    return {
      atomic: '',
      error: `Amount exceeds ${decimals} decimal places for this asset.`,
    };
  }

  const atomic = `${wholePart}${fracPart.padEnd(decimals, '0')}`.replace(/^0+(?=\d)/, '');
  if (!atomic || /^0+$/.test(atomic)) {
    return { atomic: '0', error: 'Amount must be greater than zero.' };
  }
  return { atomic, error: '' };
}

function compactBalance(value?: number): string {
  if (typeof value !== 'number') {
    return '0';
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: 6 });
}

function utf8ToHex(value: string): string {
  return Array.from(new TextEncoder().encode(value))
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('');
}

function normalizeHexInput(value: string): string {
  return value.trim().replace(/^0x/i, '').toLowerCase();
}

function normalizeGatewayStatus(value: string): 'active' | 'locked' | 'offline' {
  const normalized = String(value || '').toLowerCase().trim();
  if (normalized === 'active' || normalized === 'ready') return 'active';
  if (normalized === 'offline' || normalized === 'inactive') return 'offline';
  return 'locked';
}

function normalizeHistoryChain(value: string): string {
  const normalized = String(value || '').toLowerCase().trim();
  if (normalized === 'eth' || normalized === 'evm' || normalized === '1') return 'ethereum';
  if (normalized === 'bnb' || normalized === 'binance' || normalized === '56') return 'bsc';
  if (normalized === '8453') return 'base';
  if (normalized === 'sol' || normalized === '501') return 'solana';
  if (normalized === '784') return 'sui';
  return normalized;
}

function shortAddress(value: string, head = 10, tail = 8): string {
  const normalized = String(value || '').trim();
  if (!normalized) return '';
  if (normalized.length <= head + tail + 3) return normalized;
  return `${normalized.slice(0, head)}...${normalized.slice(-tail)}`;
}

function App() {
  const [session, setSession] = useState(() => {
    const saved = localStorage.getItem('clay_session');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return { ...parsed, connected: false }; // Need to re-auth status on mount
      } catch (e) { }
    }
    return { url: window.location.origin, token: '', connected: false };
  });

  const [sandboxState, setSandboxState] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('wallet');
  const [toast, setToast] = useState<{ msg: string, type: string } | null>(null);

  const showToast = (msg: string, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const saveSession = (s: any) => {
    localStorage.setItem('clay_session', JSON.stringify({ url: s.url, token: s.token }));
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/status`, {
        headers: {
          'Authorization': `Bearer ${session.token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSandboxState(data);
        const newSession = { ...session, connected: true };
        setSession(newSession);
        saveSession(newSession);
        showToast('Connected to Local Sandbox', 'success');
      } else {
        showToast(`Connection failed: HTTP ${res.status}`, 'error');
      }
    } catch (err) {
      showToast('Sandbox unreachable. Check URL and CORS.', 'error');
    }
  };

  const fetchStatus = async (force = false) => {
    if (!force && !session.connected) return;
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/status`, {
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSandboxState(data);
        if (!session.connected) {
          const newSession = { ...session, connected: true };
          setSession(newSession);
          saveSession(newSession);
        }
      } else if (res.status === 401) {
        setSession({ ...session, connected: false });
        showToast('Session expired or invalid token', 'error');
      }
    } catch {
      showToast('Lost connection to Sandbox', 'error');
    }
  };

  useEffect(() => {
    // Auto-reconnect if session exists
    if (!session.connected && session.token) {
      fetchStatus(true);
    }
  }, []);

  useEffect(() => {
    if (session.connected) {
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [session.connected]);

  if (!session.connected) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div className="card animate-in" style={{ width: '400px' }}>
          <div className="card-header" style={{ justifyContent: 'center', flexDirection: 'column', gap: '4px', border: 'none', padding: '0 0 20px 0' }}>
            <img src="/logo.png" alt="Claw Wallet" style={{ width: '56px', height: '56px', borderRadius: '12px', marginBottom: '12px' }} />
            <h1 className="page-title" style={{ fontSize: '1.4rem', fontWeight: '800', margin: 0 }}>Claw Wallet</h1>
            <p className="page-subtitle" style={{ fontSize: '0.85rem' }}>Connect to your Local Agent Sandbox</p>
          </div>
          <form onSubmit={handleConnect} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Sandbox URL</label>
              <input
                type="text"
                value={session.url}
                onChange={e => setSession({ ...session, url: e.target.value })}
                className="input-field"
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Agent Token</label>
              <input
                type="password"
                value={session.token}
                onChange={e => setSession({ ...session, token: e.target.value })}
                className="input-field"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '10px' }}>
              Connect to Wallet
            </button>
          </form>
        </div>
        {toast && (
          <div className={`toast show`} style={{ borderColor: toast.type === 'success' ? 'var(--success)' : 'var(--danger)' }}>
            {toast.type === 'success' ? <CheckCircle size={20} color="var(--success)" /> : <AlertCircle size={20} color="var(--danger)" />}
            {toast.msg}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <img src="/logo.png" alt="Claw" style={{ width: '32px', height: '32px', borderRadius: '8px' }} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="sidebar-title" style={{ margin: 0, lineHeight: 1.2 }}>Claw Wallet</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)', fontSize: '0.7rem', fontWeight: 600 }}>
                <div className="dot" style={{ background: 'currentColor', width: '6px', height: '6px' }}></div>
                Connected
              </div>
            </div>
          </div>
        </div>

        <div className={`nav-item ${activeTab === 'wallet' ? 'active' : ''}`} onClick={() => setActiveTab('wallet')}>
          <CreditCard size={20} /> My Assets
        </div>
        <div className={`nav-item ${activeTab === 'send' ? 'active' : ''}`} onClick={() => setActiveTab('send')}>
          <Send size={20} /> Send / Transfer
        </div>
        <div className={`nav-item ${activeTab === 'sign' ? 'active' : ''}`} onClick={() => setActiveTab('sign')}>
          <Shield size={20} /> Arbitrary Sign
        </div>
        <div className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
          <RefreshCw size={20} /> History
        </div>
        <div className={`nav-item ${activeTab === 'addresses' ? 'active' : ''}`} onClick={() => setActiveTab('addresses')}>
          <Copy size={20} /> Addresses
        </div>
        <div className={`nav-item ${activeTab === 'policy' ? 'active' : ''}`} onClick={() => setActiveTab('policy')}>
          <Shield size={20} /> Security Policy
        </div>
        <div className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
          <Settings size={20} /> Settings
        </div>

        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
          <div className="nav-item" style={{ color: 'var(--danger)' }} onClick={() => {
            localStorage.removeItem('clay_session');
            setSession({ ...session, connected: false, token: '' });
          }}>
            <LogOut size={20} /> Disconnect
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeTab === 'wallet' && <WalletView state={sandboxState} session={session} showToast={showToast} />}
        {activeTab === 'send' && <SendView session={session} state={sandboxState} showToast={showToast} />}
        {activeTab === 'sign' && <GenericSignView session={session} state={sandboxState} showToast={showToast} />}
        {activeTab === 'history' && <HistoryView session={session} />}
        {activeTab === 'addresses' && <AddressesView state={sandboxState} />}
        {activeTab === 'policy' && <PolicyView state={sandboxState} session={session} showToast={showToast} />}
        {activeTab === 'settings' && <SettingsView state={sandboxState} session={session} showToast={showToast} onRefresh={fetchStatus} />}
      </div>

      {/* Toast */}
      {toast && (
        <div className="toast show" style={{ borderColor: toast.type === 'success' ? 'var(--success)' : 'var(--danger)' }}>
          {toast.type === 'success' ? <CheckCircle size={20} color="var(--success)" /> : <AlertCircle size={20} color="var(--danger)" />}
          {toast.msg}
        </div>
      )}
    </div>
  );
}

// Subcomponents



function WalletView({ state, session, showToast }: any) {
  const evmAddr = state?.addresses?.ethereum || state?.addresses?.evm || '';
  const solAddr = state?.addresses?.solana || '';
  const suiAddr = state?.addresses?.sui || '';
  const copyToClip = (txt: string) => { if (txt) navigator.clipboard.writeText(txt); };

  const [assets, setAssets] = useState<any>(null);
  const [prices, setPrices] = useState<any>({});
  const [securityData, setSecurityData] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedSmall, setExpandedSmall] = useState<Record<string, boolean>>({});

  const chainToID: any = { ethereum: 1, bsc: 56, base: 8453, solana: 501, sui: 784 };

  const fetchData = async () => {
    try {
      const authHeader = { 'Authorization': `Bearer ${session.token}` };
      const [aRes, pRes, sRes] = await Promise.all([
        fetch(`${session.url}/api/v1/wallet/assets`, { headers: authHeader }),
        fetch(`${session.url}/api/v1/price/cache`, { headers: authHeader }),
        fetch(`${session.url}/api/v1/security/cache`, { headers: authHeader })
      ]);
      const [aData, pData, sData] = await Promise.all([aRes.json(), pRes.json(), sRes.json()]);
      setAssets(aData);
      setPrices(pData.prices || {});
      setSecurityData(sData.security || {});
    } catch (e) { } finally { setLoading(false); }
  };

  useEffect(() => {
    if (!session.connected) return;
    fetchData();
    const inv = setInterval(fetchData, 10000); // UI poll 10s
    return () => clearInterval(inv);
  }, [session.connected, session.token]);

  const handleRefreshAssets = async () => {
    setRefreshing(true);
    try {
      await fetch(`${session.url}/api/v1/wallet/refresh`, {
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      await fetchData();
      showToast('Asset refresh triggered');
    } catch (e) {
      showToast('Refresh failed', 'error');
    } finally {
      setRefreshing(false);
    }
  };

  const getAssetUSD = (a: any) => {
    const key = (a.contract_address === 'native' ? `native:${a.chain}` : `token:${a.chain}:${a.contract_address}`).toLowerCase();
    return (a.ui_balance * (prices[key] || 0));
  };

  const renderAssetGroup = (title: string, chainKey: string, address: string) => {
    const group = assets ? Object.entries(assets).find(([k]) => k.startsWith(chainKey)) : null;
    let items: any[] = group ? ((group[1] as any).Assets || []) : [];
    const blockHighRisk = state?.policy?.block_high_risk_tokens ?? true;

    // Annotate with USD
    items = items.map(a => ({ ...a, usdVal: getAssetUSD(a) }));

    // Filter malicious tokens if blocked by policy
    if (blockHighRisk) {
      items = items.filter(a => {
        if (a.contract_address === 'native') return true;
        const cid = chainToID[a.chain.toLowerCase()];
        const sKey = `${cid}:${a.contract_address.toLowerCase()}`;
        const r = securityData[sKey];
        return !(r && r.risk_level >= 4);
      });
    }

    // Sort
    items = items.sort((a, b) => {
      // Native always first
      if (a.contract_address === 'native') return -1;
      if (b.contract_address === 'native') return 1;
      // Then by USD value
      return b.usdVal - a.usdVal;
    });

    const totalUSD = items.reduce((sum, a) => sum + a.usdVal, 0);
    const mainItems = items.filter(a => a.usdVal >= 1);
    const smallItems = items.filter(a => a.usdVal < 1);
    const isExpanded = expandedSmall[chainKey];

      const renderItem = (a: any) => {
        const chainID = chainToID[a.chain.toLowerCase()];
        const secKey = `${chainID}:${a.contract_address.toLowerCase()}`;
        const risk = securityData[secKey];

        return (
          <div key={a.contract_address + a.symbol} className="glass-block" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600 }}>{a.symbol}</span>
                  {risk && risk.risk_level > 2 && (
                    <span className={`badge ${risk.risk_level >= 4 ? 'danger' : 'warning'}`} style={{ fontSize: '0.6rem', padding: '1px 4px' }}>
                      {risk.risk_label}
                    </span>
                  )}
                </div>
                <span style={{ color: 'var(--success)', fontWeight: 700, fontSize: '0.9rem' }}>
                  {a.usdVal > 0 ? `$${a.usdVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'}
                </span>
              </div>
              <div style={{ fontWeight: 800, fontSize: '1.4rem', color: 'var(--text-primary)', letterSpacing: '-0.5px' }}>
                {a.ui_balance.toLocaleString(undefined, { maximumFractionDigits: 6 })}
              </div>
            </div>
            <div
              onClick={(e) => { e.stopPropagation(); copyToClip(a.contract_address); showToast('Address copied'); }}
              title="Click to copy address"
              style={{
                fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '10px',
                fontFamily: 'monospace', cursor: 'pointer',
                borderTop: '1px solid rgba(0,0,0,0.05)', paddingTop: '8px',
                display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden'
              }}
            >
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1, opacity: 0.7 }}>
                {a.contract_address}
              </span>
              <Copy size={12} style={{ opacity: 0.5, flexShrink: 0 }} />
            </div>
          </div>
        );
      };

    return (
      <div className="card">
        <div className="card-header" style={{ alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
            <h3 className="card-title">{title}</h3>
            <span style={{ color: 'var(--success)', fontWeight: 700 }}>
              ${totalUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <span style={{ color: 'var(--accent)', fontSize: '0.8rem', cursor: 'pointer' }} onClick={() => copyToClip(address)}>
            {address ? `${address.slice(0, 8)}...${address.slice(-6)} copy` : 'Not generated'}
          </span>
        </div>

        {!address ? (
          <div style={{ color: 'var(--text-secondary)', marginTop: '10px' }}>Address not initialized</div>
        ) : loading && !assets ? (
          <div style={{ marginTop: '15px' }}>Loading assets...</div>
        ) : items.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', marginTop: '10px' }}>No assets found</div>
        ) : (
          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Main Assets Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
              {mainItems.map(renderItem)}
            </div>

            {/* Small Assets Toggle */}
            {smallItems.length > 0 && (
              <div>
                <div
                  onClick={() => setExpandedSmall({ ...expandedSmall, [chainKey]: !isExpanded })}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer', padding: '8px 0' }}
                >
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  Dust Assets ({smallItems.length} items {"<"} $1.00)
                </div>
                {isExpanded && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '8px', marginTop: '8px' }}>
                    {smallItems.map(a => (
                      <div key={a.contract_address + a.symbol} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '6px', padding: '8px 12px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ fontSize: '0.8rem' }}>
                          <span style={{ fontWeight: 600 }}>{a.ui_balance.toLocaleString(undefined, { maximumFractionDigits: 4 })}</span>
                          <span style={{ color: 'var(--text-secondary)', marginLeft: '4px' }}>{a.symbol}</span>
                        </div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                          ${a.usdVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">My Assets</h1>
          <p className="page-subtitle">Unified multichain view (EVM, Solana, Sui) via Alchemy Node Layer</p>
        </div>
        <button className="btn" onClick={handleRefreshAssets} disabled={refreshing}>
          {refreshing ? <RefreshCw className="spin" size={16} /> : <RefreshCw size={16} />} Refresh Assets
        </button>
      </div>

      {renderAssetGroup("Ethereum", "ethereum", evmAddr)}
      {renderAssetGroup("Base", "base", evmAddr)}
      {renderAssetGroup("BSC", "bsc", evmAddr)}
      {renderAssetGroup("Solana", "solana", solAddr)}
      {renderAssetGroup("Sui", "sui", suiAddr)}
    </div>
  );
}

function HistoryView({ session }: any) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const fetchData = async (selectedFilter = filter) => {
    try {
      const authHeader = { 'Authorization': `Bearer ${session.token}` };
      const query = new URLSearchParams();
      query.set('limit', '100');
      if (selectedFilter !== 'all') {
        query.set('chain', selectedFilter);
      }
      const tRes = await fetch(`${session.url}/api/v1/wallet/history?${query.toString()}`, { headers: authHeader });
      const onChainTxs = await tRes.json();

      const normalizedChain = (onChainTxs || []).map((t: any, idx: number) => ({
        timestamp: t.timestamp,
        chain: normalizeHistoryChain(t.chain),
        event: t.direction === 'incoming' ? 'RECEIVED' : 'SENT',
        status: t.status,
        details: `${t.amount} ${t.symbol} | ${shortAddress(t.from, 8, 6)} -> ${shortAddress(t.to, 8, 6)}`,
        id: `tx-${t.chain}-${t.hash}-${idx}`,
        hash: t.hash,
        explorerUrl: t.explorer_url || ''
      }));

      const merged = [...normalizedChain]
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

      setItems(merged);
    } catch (e) {
      setItems([]);
    } finally { setLoading(false); }
  };

  useEffect(() => {
    setLoading(true);
    fetchData(filter);
    const inv = setInterval(() => fetchData(filter), 8000);
    return () => clearInterval(inv);
  }, [session, filter]);

  const filtered = items;
  const chains = ['all', 'ethereum', 'base', 'bsc', 'solana', 'sui'];

  const getExplorerLink = (chain: string, hash: string) => {
    const explorers: any = {
      ethereum: 'https://etherscan.io/tx/',
      base: 'https://basescan.org/tx/',
      bsc: 'https://bscscan.com/tx/',
      solana: 'https://solscan.io/tx/',
      sui: 'https://suivision.xyz/txblock/',
      polygon: 'https://polygonscan.com/tx/',
      arbitrum: 'https://arbiscan.io/tx/',
      optimism: 'https://optimistic.etherscan.io/tx/'
    };
    return explorers[chain.toLowerCase()] ? explorers[chain.toLowerCase()] + hash : '#';
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Transaction History</h1>
        <p className="page-subtitle">RPC-backed on-chain activity for the current wallet</p>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '24px' }}>
        {chains.map(c => (
          <button key={c} className={`btn ${filter === c ? 'btn-primary' : ''}`} onClick={() => setFilter(c)} style={{ padding: '6px 16px', fontSize: '0.85rem' }}>
            {c.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">On-Chain Activity</h2>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Polling active</div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filtered.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              {loading ? 'Fetching history...' : 'No records found'}
            </div>
          ) : (
            filtered.map((item: any) => (
              <div key={item.id} className="glass-block" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="badge" style={{ fontSize: '0.65rem', background: 'rgba(15, 23, 42, 0.06)', color: 'var(--text-primary)', border: '1px solid rgba(15, 23, 42, 0.08)' }}>
                      {item.chain.toUpperCase()}
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>{item.event}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {(item.status === 'success' || item.status === 'SUCCESS' || item.status === 'accepted') ? 'Success' : 'Pending'} · {item.status}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="data-value" style={{ background: 'rgba(0,0,0,0.03)', border: '1px solid rgba(0,0,0,0.05)', color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                  <a href={item.explorerUrl || getExplorerLink(item.chain, item.hash)} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>
                    {item.details} <span style={{ opacity: 0.5 }}>view</span>
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}



function AddressesView({ state }: any) {
  const whitelist = Array.isArray(state?.policy?.whitelist_to) ? state.policy.whitelist_to : [];
  const blacklist = Array.isArray(state?.policy?.blacklist_to) ? state.policy.blacklist_to : [];
  const isEmpty = whitelist.length === 0 && blacklist.length === 0;

  const renderEntries = (entries: any[], title: string) => (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{title}</h2>
      </div>
      {entries.length === 0 ? (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No address list is setting yet ..</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {entries.map((entry: any, index: number) => (
            <div key={`${title}-${entry.address}-${index}`} style={{ border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '10px', padding: '12px 14px', background: '#fff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'center' }}>
                <span style={{ fontFamily: 'monospace', color: 'var(--text-primary)', fontSize: '0.88rem' }}>{shortAddress(entry.address)}</span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '999px', padding: '3px 8px' }}>
                  {entry.chain || 'All Chains'}
                </span>
              </div>
              {entry.note ? (
                <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{entry.note}</div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <h1 className="page-title">Addresses</h1>
        <p className="page-subtitle">Whitelist and blacklist entries synced from the current policy.</p>
      </div>

      {isEmpty ? (
        <div className="card">
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>No address list is setting yet ..</div>
        </div>
      ) : (
        <div className="grid">
          {renderEntries(whitelist, 'Whitelist')}
          {renderEntries(blacklist, 'Blacklist')}
        </div>
      )}
    </div>
  );
}

function SendView({ session, state, showToast }: any) {
  const [txData, setTxData] = useState({
    chain: 'ethereum',
    to: '',
    amount: '',
    assetContract: 'native',
    suiObjectId: ''
  });
  const [assetSnapshot, setAssetSnapshot] = useState<Record<string, WalletAsset[]>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState('');
  const isEVM = txData.chain === 'ethereum' || txData.chain === 'base' || txData.chain === 'bsc';
  const senderAddress = txData.chain === 'solana'
    ? state?.addresses?.solana || ''
    : txData.chain === 'sui'
      ? state?.addresses?.sui || ''
      : state?.addresses?.ethereum || state?.addresses?.evm || '';
  const fetchAssets = async () => {
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/assets`, {
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      if (res.ok) {
        const payload = await res.json();
        setAssetSnapshot(normalizeGatewayAssets(payload));
      }
    } catch (e) { }
  };

  useEffect(() => {
    if (!session.connected) return;
    fetchAssets();
    const inv = setInterval(fetchAssets, 10000);
    return () => clearInterval(inv);
  }, [session.connected, session.token, session.url]);

  const chainAssets = [...(assetSnapshot[txData.chain] || [])].sort((a, b) => {
    if (a.contract_address === 'native') return -1;
    if (b.contract_address === 'native') return 1;
    return `${a.symbol}:${a.contract_address}`.localeCompare(`${b.symbol}:${b.contract_address}`);
  });
  if (!chainAssets.some(asset => asset.contract_address === 'native')) {
    chainAssets.unshift(getNativeAsset(txData.chain));
  }

  const selectedAsset = chainAssets.find(asset => asset.contract_address === txData.assetContract) || chainAssets[0] || getNativeAsset(txData.chain);
  const isTokenTransfer = selectedAsset.contract_address !== 'native';
  const tokenContract = isTokenTransfer ? selectedAsset.contract_address : '';
  const amountParse = parseDisplayAmountToAtomic(txData.amount, selectedAsset.decimals || 0);
  const atomicAmount = amountParse.atomic || '0';
  const builderKind = isTokenTransfer
    ? (isEVM ? 'erc20_transfer' : txData.chain === 'solana' ? 'spl_transfer' : 'sui_coin_transfer')
    : (txData.chain === 'sui' ? 'native_sui_transfer' : 'native_transfer');

  useEffect(() => {
    if (!chainAssets.some(asset => asset.contract_address === txData.assetContract)) {
      setTxData(current => ({ ...current, assetContract: chainAssets[0]?.contract_address || 'native', suiObjectId: current.chain === 'sui' ? current.suiObjectId : '' }));
    }
  }, [txData.assetContract, txData.chain, chainAssets]);

  const rawRequestPreview = {
    chain: txData.chain,
    uid: state?.uid || 'UID-WEB',
    from: senderAddress || '(wallet address unavailable)',
    to: txData.to || '',
    display_amount: txData.amount || '0',
    display_symbol: selectedAsset.symbol,
    decimals: selectedAsset.decimals,
    amount_wei: atomicAmount,
    ...(isTokenTransfer ? { token_contract: tokenContract } : {}),
    ...(txData.chain === 'sui' && !isTokenTransfer && txData.suiObjectId ? { sui_object_id: txData.suiObjectId } : {}),
  };
  const decodedIntentPreview = {
    chain: txData.chain,
    builder_kind: builderKind,
    from: senderAddress || '(wallet address unavailable)',
    to: txData.to || '(empty)',
    asset_symbol: selectedAsset.symbol,
    asset_decimals: selectedAsset.decimals,
    display_amount: txData.amount || '0',
    amount_wei: atomicAmount,
    asset_kind: isTokenTransfer ? 'token' : 'native',
    token_contract: isTokenTransfer ? tokenContract : '(native)',
    sui_object_id: txData.chain === 'sui' ? (!isTokenTransfer ? (txData.suiObjectId || '(required)') : '(auto-select from coin objects)') : '(not used)',
    broadcast: 'sandbox-managed',
  };

  const sendTx = async (e: React.FormEvent) => {
    e.preventDefault();
    if (amountParse.error) {
      showToast(amountParse.error, 'error');
      setResult(`REJECTED:\n${amountParse.error}`);
      return;
    }
    if (txData.chain === 'sui' && !isTokenTransfer && !txData.suiObjectId.trim()) {
      showToast('Sui native transfers require a Sui coin object id.', 'error');
      setResult('REJECTED:\nSui native transfers require a Sui coin object id.');
      return;
    }

    setSubmitting(true);
    setResult('');
    try {
      const payload = {
        chain: txData.chain,
        uid: state?.uid || "UID-WEB",
        to: txData.to,
        amount_wei: atomicAmount,
        ...(isTokenTransfer ? { token_contract: tokenContract } : {}),
        ...(txData.chain === 'sui' && !isTokenTransfer && txData.suiObjectId ? { sui_object_id: txData.suiObjectId } : {}),
      };

      const res = await fetch(`${session.url}/api/v1/tx/transfer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token}` },
        body: JSON.stringify(payload)
      });
      const text = await res.text();
      if (res.ok) {
        showToast('Transfer submitted through sandbox', 'success');
        let parsed = text;
        try { parsed = JSON.stringify(JSON.parse(text), null, 2) } catch (e) { }
        setResult(`SUCCESS:\n${parsed}`);
      } else {
        showToast('Transfer rejected', 'error');
        setResult(`REJECTED [${res.status}]:\n${text}`);
      }
    } catch (err) {
      showToast('Error communicating with Sandbox', 'error');
      setResult('Network Error');
    }
    setSubmitting(false);
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <h1 className="page-title">Send Crypto</h1>
        <p className="page-subtitle">Build, validate, sign, and broadcast a real transfer through your local sandbox</p>
      </div>

      <div className="card">
        <form onSubmit={sendTx} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="grid">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Network (Chain)</label>
              <select className="input-field" value={txData.chain} onChange={e => setTxData({ ...txData, chain: e.target.value, assetContract: 'native', suiObjectId: '' })}>
                <option value="ethereum">Ethereum</option>
                <option value="base">Base</option>
                <option value="bsc">BSC</option>
                <option value="solana">Solana</option>
                <option value="sui">Sui</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Recipient Address (To)</label>
              <input
                type="text"
                className="input-field"
                placeholder="Address"
                value={txData.to}
                onChange={e => setTxData({ ...txData, to: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                Amount ({selectedAsset.symbol})
              </label>
              <input
                type="text"
                className="input-field"
                placeholder={`e.g. ${selectedAsset.decimals >= 9 ? '1.25' : '1'}`}
                value={txData.amount}
                onChange={e => setTxData({ ...txData, amount: e.target.value })}
                required
              />
              <div style={{ color: amountParse.error ? 'var(--danger)' : 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '8px' }}>
                {amountParse.error || `Balance available: ${compactBalance(selectedAsset.ui_balance)} ${selectedAsset.symbol}. The gateway converts this display amount into atomic units automatically.`}
              </div>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Asset</label>
              <select
                className="input-field"
                value={selectedAsset.contract_address}
                onChange={e => setTxData({ ...txData, assetContract: e.target.value, suiObjectId: e.target.value === 'native' ? txData.suiObjectId : '' })}
              >
                {chainAssets.map(asset => (
                  <option key={`${asset.chain}:${asset.contract_address}`} value={asset.contract_address}>
                    {asset.contract_address === 'native'
                      ? `${asset.symbol} (native)`
                      : `${asset.symbol} token`}
                  </option>
                ))}
              </select>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '8px' }}>
                {isTokenTransfer
                  ? `Using ${selectedAsset.symbol} with ${selectedAsset.decimals} decimals. Contract / mint / coin type: ${tokenContract}`
                  : `Using native ${selectedAsset.symbol} with ${selectedAsset.decimals} decimals.`}
              </div>
            </div>
          </div>

          {txData.chain === 'sui' && !isTokenTransfer && (
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Sui Coin Object ID</label>
              <input
                type="text"
                className="input-field"
                placeholder="0x..."
                value={txData.suiObjectId}
                onChange={e => setTxData({ ...txData, suiObjectId: e.target.value })}
                required
              />
            </div>
          )}

          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            Enter human-readable amounts like <code>1</code> ETH, <code>0.25</code> SOL, or <code>15.5</code> USDC. The gateway normalizes them into atomic on-chain units using the selected asset decimals before calling the sandbox API.
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? <RefreshCw className="spin" size={18} /> : <Send size={18} />} Submit Managed Transfer
          </button>
        </form>
      </div>

      <div className="grid">
        <div className="card">
          <div className="card-header"><h3 className="card-title">API Request Preview</h3></div>
          <div className="pre-code">{formatPreviewJson(rawRequestPreview)}</div>
        </div>
        <div className="card">
          <div className="card-header"><h3 className="card-title">Normalized Transfer Preview</h3></div>
          <div className="pre-code">{formatPreviewJson(decodedIntentPreview)}</div>
        </div>
      </div>

      {result && (
        <div className="card" style={{ borderColor: result.includes('SUCCESS') ? 'var(--success)' : 'var(--danger)' }}>
          <div className="card-header"><h3 className="card-title">Sandbox Transfer Output</h3></div>
          <div className="pre-code" style={{ color: result.includes('SUCCESS') ? 'var(--success)' : 'var(--danger)' }}>
            {result}
          </div>
        </div>
      )}
    </div>
  );
}

function GenericSignView({ session, state, showToast }: any) {
  const [form, setForm] = useState({
    chain: 'ethereum',
    signMode: 'personal_sign',
    payloadEncoding: 'utf8',
    payloadText: '',
    typedDataText: `{
  "types": {
    "EIP712Domain": [
      { "name": "name", "type": "string" },
      { "name": "version", "type": "string" },
      { "name": "chainId", "type": "uint256" }
    ],
    "Message": [
      { "name": "contents", "type": "string" }
    ]
  },
  "primaryType": "Message",
  "domain": {
    "name": "Claw Wallet",
    "version": "1",
    "chainId": 1
  },
  "message": {
    "contents": "hello from frontend_gateway"
  }
}`,
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState('');

  const supportsTypedData = form.chain === 'ethereum' || form.chain === 'base' || form.chain === 'bsc';
  const supportsRawHash = supportsTypedData;
  const availableModes = [
    { value: 'personal_sign', label: 'personal_sign' },
    ...(supportsRawHash ? [{ value: 'raw_hash', label: 'raw_hash' }] : []),
    ...(supportsTypedData ? [{ value: 'typed_data', label: 'typed_data' }] : []),
  ];

  useEffect(() => {
    if (!availableModes.some(option => option.value === form.signMode)) {
      setForm(current => ({ ...current, signMode: availableModes[0].value }));
    }
  }, [form.chain]);

  const payloadHex = form.payloadEncoding === 'hex'
    ? normalizeHexInput(form.payloadText)
    : utf8ToHex(form.payloadText);

  let typedDataError = '';
  let typedDataJSON: any = null;
  if (form.signMode === 'typed_data') {
    try {
      typedDataJSON = JSON.parse(form.typedDataText);
    } catch {
      typedDataError = 'typed_data must be valid JSON.';
    }
  }

  const payloadError = form.signMode === 'typed_data'
    ? typedDataError
    : !payloadHex
      ? 'Payload is required.'
      : form.payloadEncoding === 'hex' && !/^[0-9a-f]*$/i.test(payloadHex)
        ? 'Hex payload must contain only 0-9 and a-f.'
        : '';

  const requestPreview = form.signMode === 'typed_data'
    ? {
        chain: form.chain,
        uid: state?.uid || '',
        sign_mode: form.signMode,
        typed_data: typedDataJSON || form.typedDataText,
      }
    : {
        chain: form.chain,
        uid: state?.uid || '',
        sign_mode: form.signMode,
        tx_payload_hex: payloadHex,
      };

  const submitSign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (payloadError) {
      showToast(payloadError, 'error');
      setResult(`REJECTED:\n${payloadError}`);
      return;
    }

    setSubmitting(true);
    setResult('');
    try {
      const res = await fetch(`${session.url}/api/v1/tx/sign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`,
        },
        body: JSON.stringify(requestPreview),
      });
      const text = await res.text();
      if (res.ok) {
        showToast('Signature generated', 'success');
        try {
          setResult(`SUCCESS:\n${JSON.stringify(JSON.parse(text), null, 2)}`);
        } catch {
          setResult(`SUCCESS:\n${text}`);
        }
      } else {
        showToast('Signing rejected', 'error');
        setResult(`REJECTED [${res.status}]:\n${text}`);
      }
    } catch {
      showToast('Error communicating with Sandbox', 'error');
      setResult('Network Error');
    }
    setSubmitting(false);
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <h1 className="page-title">Arbitrary Sign</h1>
        <p className="page-subtitle">Use the existing sandbox signing API to sign free-form text, raw hashes, or EIP-712 typed data.</p>
      </div>

      <div className="card">
        <form onSubmit={submitSign} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="grid">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Chain</label>
              <select className="input-field" value={form.chain} onChange={e => setForm({ ...form, chain: e.target.value })}>
                <option value="ethereum">Ethereum</option>
                <option value="base">Base</option>
                <option value="bsc">BSC</option>
                <option value="solana">Solana</option>
                <option value="sui">Sui</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Sign Mode</label>
              <select className="input-field" value={form.signMode} onChange={e => setForm({ ...form, signMode: e.target.value })}>
                {availableModes.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>

          {form.signMode !== 'typed_data' && (
            <>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Payload Encoding</label>
                <select className="input-field" value={form.payloadEncoding} onChange={e => setForm({ ...form, payloadEncoding: e.target.value })}>
                  <option value="utf8">UTF-8 text</option>
                  <option value="hex">Hex bytes</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  {form.signMode === 'raw_hash' ? '32-byte hash' : 'Payload'}
                </label>
                <textarea
                  className="input-field"
                  rows={8}
                  placeholder={form.payloadEncoding === 'hex' ? '0x68656c6c6f' : 'hello from frontend_gateway'}
                  value={form.payloadText}
                  onChange={e => setForm({ ...form, payloadText: e.target.value })}
                />
                <div style={{ color: payloadError ? 'var(--danger)' : 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '8px' }}>
                  {payloadError || `Normalized hex payload: ${payloadHex || '(empty)'}`}
                </div>
              </div>
            </>
          )}

          {form.signMode === 'typed_data' && (
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Typed Data JSON</label>
              <textarea
                className="input-field"
                rows={16}
                value={form.typedDataText}
                onChange={e => setForm({ ...form, typedDataText: e.target.value })}
              />
              <div style={{ color: payloadError ? 'var(--danger)' : 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '8px' }}>
                {payloadError || 'The JSON is sent as typed_data to the existing /api/v1/tx/sign endpoint.'}
              </div>
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? <RefreshCw className="spin" size={18} /> : <Shield size={18} />} Request Signature
          </button>
        </form>
      </div>

      <div className="card">
        <div className="card-header"><h3 className="card-title">API Request Preview</h3></div>
        <div className="pre-code">{formatPreviewJson(requestPreview)}</div>
      </div>

      {result && (
        <div className="card" style={{ borderColor: result.includes('SUCCESS') ? 'var(--success)' : 'var(--danger)' }}>
          <div className="card-header"><h3 className="card-title">Sandbox Signature Output</h3></div>
          <div className="pre-code" style={{ color: result.includes('SUCCESS') ? 'var(--success)' : 'var(--danger)' }}>
            {result}
          </div>
        </div>
      )}
    </div>
  );
}

function PolicyView({ state }: any) {
  const policy = state?.policy || {};
  const oracleNative: boolean = state?.oracle_native ?? false;
  const oracleTokens: boolean = state?.oracle_tokens ?? false;
  const currentTTL = typeof policy?.pin_ttl_seconds === 'number' ? policy.pin_ttl_seconds : 86400;
  const keywordBlacklist = Array.isArray(policy?.personal_sign_keyword_blacklist) ? policy.personal_sign_keyword_blacklist : [];
  const todaySpentUSD = Number(state?.today_spent_usd || 0);
  const todayTxCount = Number(state?.today_tx_count || 0);
  const todayLocalSpentUSD = Number(state?.today_local_spent_usd || 0);
  const todayLocalTxCount = Number(state?.today_local_tx_count || 0);
  const todayOnchainSpentUSD = Number(state?.today_onchain_spent_usd || 0);
  const todayOnchainTxCount = Number(state?.today_onchain_tx_count || 0);
  const todayEffectiveSpentUSD = Number(state?.today_effective_spent_usd || 0);
  const todayEffectiveTxCount = Number(state?.today_effective_tx_count || 0);

  const policyRows = [
    ['Daily USD Limit', `$${Number(policy?.daily_limit_usd || 0).toLocaleString()}`],
    ['Single USD Limit', `$${Number(policy?.max_amount_per_tx_usd || 0).toLocaleString()}`],
    ['Daily Max TXs', `${Number(policy?.daily_max_tx_count || 0)}`],
    ['PIN Residency TTL', currentTTL === 0 ? 'Unlimited' : `${currentTTL}s`],
    ['Keep Share2 Resident', policy?.keep_share2_resident ? 'Enabled' : 'Disabled'],
    ['Block High Risk Tokens', policy?.block_high_risk_tokens ? 'Enabled' : 'Disabled'],
    ['Allow Blind Sign', policy?.allow_blind_sign ? 'Enabled' : 'Disabled'],
    ['Strict Plain Text', policy?.strict_plain_text ? 'Enabled' : 'Disabled'],
    ['Unpriced Assets', policy?.unpriced_asset_policy === 'block' ? 'Block' : 'Allow'],
  ];
  const usageRows = [
    ['Tracked Spend Today', `$${todaySpentUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['Tracked TX Count', `${todayTxCount}`],
    ['Local Spend', `$${todayLocalSpentUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['Local TX Count', `${todayLocalTxCount}`],
    ['On-Chain Spend', `$${todayOnchainSpentUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['On-Chain TX Count', `${todayOnchainTxCount}`],
    ['Effective Spend', `$${todayEffectiveSpentUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['Effective TX Count', `${todayEffectiveTxCount}`],
  ];

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <h1 className="page-title">Security & Policy</h1>
        <p className="page-subtitle">Current local risk controls and oracle health for this sandbox.</p>
      </div>

      <div className="card" style={{ borderColor: 'rgba(245, 158, 11, 0.35)', background: 'linear-gradient(180deg, rgba(245, 158, 11, 0.08), rgba(255,255,255,0.92))' }}>
        <div className="card-header">
          <h3 className="card-title">Managed From Claw Wallet</h3>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.7 }}>
          To modify the risk policy, you should bind your agent wallet at{' '}
          <a href="https://www.clawwallet.cc/" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontWeight: 700 }}>
            https://www.clawwallet.cc/
          </a>
        </p>
      </div>

      <div className="grid">
        <div className="card" style={{ borderColor: oracleNative ? 'rgba(34, 197, 94, 0.28)' : 'rgba(239, 68, 68, 0.2)' }}>
          <div className="card-header">
            <h3 className="card-title">Native Oracle</h3>
            <span className={`badge ${oracleNative ? 'success' : 'danger'}`}>{oracleNative ? 'Online' : 'Offline'}</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', marginTop: '8px' }}>
            ETH, BNB, SOL and SUI native pricing for spend controls.
          </p>
        </div>

        <div className="card" style={{ borderColor: oracleTokens ? 'rgba(34, 197, 94, 0.28)' : 'rgba(239, 68, 68, 0.2)' }}>
          <div className="card-header">
            <h3 className="card-title">Token Oracle</h3>
            <span className={`badge ${oracleTokens ? 'success' : 'danger'}`}>{oracleTokens ? 'Online' : 'Offline'}</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', marginTop: '8px' }}>
            Token pricing used to enforce USD-denominated policy limits.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Current Policy Snapshot</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginTop: '18px' }}>
          {policyRows.map(([label, value]) => (
            <div key={label} style={{ border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '12px', padding: '14px 16px', background: '#fff' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.74rem', marginBottom: '6px' }}>{label}</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.98rem' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Today's Usage</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginTop: '18px' }}>
          {usageRows.map(([label, value]) => (
            <div key={label} style={{ border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '12px', padding: '14px 16px', background: '#fff' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.74rem', marginBottom: '6px' }}>{label}</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.98rem' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Personal Sign Keyword Blacklist</h3>
        </div>
        {keywordBlacklist.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No keyword blacklist is configured.</div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '16px' }}>
            {keywordBlacklist.map((item: string) => (
              <span key={item} style={{ border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '999px', padding: '6px 12px', fontSize: '0.82rem', color: 'var(--text-primary)', background: '#fff' }}>
                {item}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function SettingsView({ state, session, showToast, onRefresh }: any) {
  const [bindUid, setBindUid] = useState('');
  const gatewayStatus = normalizeGatewayStatus(state?.gateway_status || state?.status);
  const relayBindingStatus = String(state?.relay_binding_status || 'unknown').toLowerCase();
  const relayUserBound = Boolean(state?.relay_user_bound);
  const canReactivateLocally = Boolean(state?.can_reactivate_locally);
  const localPaths = state?.local_paths || {};
  const relayBindingColor = relayUserBound ? 'var(--success)' : relayBindingStatus === 'unbound' ? 'var(--warning)' : 'var(--text-secondary)';
  const sdkSnippet = `import { ethers } from "ethers";
import { ClayEthersSigner } from "@bitslab/clay-sdk";

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL!);
const signer = new ClayEthersSigner(
  {
    uid: "${state?.uid || 'CLAW_WALLET_UID'}",
    sandboxUrl: "${session.url}",
    sandboxToken: process.env.CLAY_AGENT_TOKEN || "${session.token}",
  },
  provider,
);`;

  const handleExport = async () => {
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/backup`, {
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      if (!res.ok) {
        showToast('Failed to export agent wallet backup', 'error');
        return;
      }

      const backup = await res.json();
      if (!backup.agent_token) {
        backup.agent_token = session.token;
      }
      backup.sandbox_url = session.url;

      const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `claw_backup_${state?.uid || 'wallet'}.json`;
      a.click();
      showToast('Agent wallet backup downloaded');
    } catch (e) {
      showToast('Failed to export agent wallet backup', 'error');
    }
  };
  const handleBind = async () => {
    if (!bindUid) return;
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/bind_uid`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token}` },
        body: JSON.stringify({ uid: bindUid })
      });
      if (res.ok) {
        showToast('UID bound successfully');
        onRefresh();
      } else {
        showToast('Failed to bind UID', 'error');
      }
    } catch (e) { showToast('Network error', 'error'); }
  };

  const handleRefreshSandboxStatus = async () => {
    try {
      await onRefresh();
      showToast('Sandbox status refreshed');
    } catch (e) {
      showToast('Failed to refresh sandbox status', 'error');
    }
  };

  const handleReactivateWallet = async () => {
    try {
      const res = await fetch(`${session.url}/api/v1/wallet/reactivate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      if (res.ok) {
        showToast('Local wallet reactivation triggered');
        await onRefresh();
      } else {
        const text = await res.text();
        showToast(text || 'Failed to reactivate wallet', 'error');
      }
    } catch (e) {
      showToast('Failed to reactivate wallet', 'error');
    }
  };

  const handleClearSession = async () => {
    if (!window.confirm('Clear the in-memory signer session? This does not delete local files.')) {
      return;
    }
    try {
      const res = await fetch(`${session.url}/wipe`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${session.token}` }
      });
      if (res.ok) {
        showToast('In-memory signer session cleared');
        await onRefresh();
      } else {
        showToast('Failed to clear sandbox session', 'error');
      }
    } catch (e) {
      showToast('Failed to clear sandbox session', 'error');
    }
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Sandbox Management & Integration</p>
      </div>

      <div className="grid">
        <div className="card">
          <h3 className="card-title">Instance Identity</h3>
          <div style={{ marginTop: '15px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>UID</label>
              {state?.uid ? (
                <div style={{ fontFamily: 'monospace', fontSize: '1rem' }}>{state.uid}</div>
              ) : (
                <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                  <input type="text" className="input-field" placeholder="Enter UID to bind..." value={bindUid} onChange={e => setBindUid(e.target.value)} />
                  <button className="btn btn-primary" onClick={handleBind}>Bind</button>
                </div>
              )}
            </div>
            <div>
              <label style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Agent Token</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '5px' }}>
                <div style={{ fontFamily: 'monospace', fontSize: '0.9rem', wordBreak: 'break-all', flex: 1, background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '4px' }}>
                  {session.token.slice(0, 8)}...{session.token.slice(-8)}
                </div>
                <button className="nav-item" style={{ padding: '8px', border: '1px solid var(--glass-border)' }} onClick={() => { navigator.clipboard.writeText(session.token); showToast('Token copied'); }}>
                  <Copy size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Cloud Relay</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '10px 0' }}>
            Your sandbox is tethered to the cloud relay for MPC key fragment management and security orchestration.
          </p>
          <div className="glass-block" style={{ 
            padding: '20px', 
            marginTop: '15px', 
            background: 'rgba(255, 255, 255, 0.05)', 
            border: '1px solid var(--glass-border)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>UID Binding</span>
              <span style={{ color: relayBindingColor, fontWeight: 700 }}>
                {relayUserBound ? 'Bound by user' : relayBindingStatus}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Status</span>
              <span style={{ color: gatewayStatus === 'active' ? 'var(--success)' : gatewayStatus === 'locked' ? 'var(--warning)' : 'var(--text-secondary)', fontWeight: 700 }}>
                {gatewayStatus}
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button className="btn" style={{ fontSize: '0.8rem', flex: 1 }} onClick={handleRefreshSandboxStatus}>Refresh Sandbox Status</button>
          </div>
        </div>
      </div>
      <div className="card">
        <div className="card-header">
           <h2 className="card-title">Quick Actions</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '10px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              className="btn"
              style={{ width: 'fit-content', opacity: relayUserBound || !canReactivateLocally ? 0.6 : 1, cursor: relayUserBound || !canReactivateLocally ? 'not-allowed' : 'pointer' }}
              onClick={handleReactivateWallet}
              disabled={relayUserBound || !canReactivateLocally}
            >
              Reactive Wallet
            </button>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '4px' }}>
              {relayUserBound
                ? 'Your wallet has bind by user, you should reactive your agent wallet at your dashborad https://www.clawwallet.cc/'
                : canReactivateLocally
                  ? 'Rebuild the local signer session from the persisted local identity files.'
                  : 'This sandbox cannot be reactivated locally in its current state.'}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button className="btn" style={{ width: 'fit-content' }} onClick={handleExport}>Backup Agent Wallet</button>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '4px' }}>
              Export wallet identity metadata, relay binding state, and absolute local file paths for recovery operations.
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button className="btn" style={{ width: 'fit-content', borderColor: 'var(--danger)', color: 'var(--danger)' }} onClick={handleClearSession}>Clear In-Memory Session</button>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '4px' }}>Lock the current sandbox by wiping only the in-memory signer session. Local files and identity stay intact.</div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Partner Integration Helper</h2>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '10px' }}>
          Replace private-key wallet initialization with the claw wallet compatibility signer that forwards signing requests to this local sandbox.
        </p>
        <div className="pre-code" style={{ marginTop: '16px' }}>{sdkSnippet}</div>
        <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
          <button className="btn" onClick={() => { navigator.clipboard.writeText(sdkSnippet); showToast('Ethers integration snippet copied'); }}>
            Copy Ethers Snippet
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Local Files</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px' }}>
          {Object.entries(localPaths).map(([key, value]) => (
            <div key={key} style={{ border: '1px solid rgba(15, 23, 42, 0.08)', borderRadius: '10px', padding: '12px 14px', background: '#fff' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.74rem', marginBottom: '6px' }}>{key}</div>
              <div style={{ fontFamily: 'monospace', fontSize: '0.82rem', color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                {String(value || '') || 'Unavailable'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
