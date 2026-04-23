class EarningsCalculator {
  constructor() {
    this.prices = {
      MAST: 0.01,  // USD per MAST (approximate)
      MYST: 0.02,  // USD per MYST (approximate)
      ACU: 0.005,  // USD per ACU (approximate)
      WINGS: 0.01, // USD per WINGS (approximate)
      NEX: 0.03    // USD per NEX (approximate)
    };
  }

  async calculate(fleetStatus) {
    const earnings = {
      mastchain: await this.calculateMastChain(fleetStatus.mastchain),
      mysterium: await this.calculateMysterium(fleetStatus.mysterium),
      acurast: await this.calculateAcurast(fleetStatus.acurast),
      total: { usd: 0, daily: 0, monthly: 0 }
    };

    // Calculate totals
    const mastchainUSD = parseFloat(earnings.mastchain.usd) || 0;
    const mysteriumUSD = parseFloat(earnings.mysterium.usd) || 0;
    const acurastUSD = parseFloat(earnings.acurast.usd) || 0;
    
    earnings.total.usd = (mastchainUSD + mysteriumUSD + acurastUSD).toFixed(4);
    earnings.total.daily = earnings.total.usd;
    earnings.total.monthly = (parseFloat(earnings.total.usd) * 30).toFixed(2);

    return earnings;
  }

  async calculateMastChain(nodes) {
    const onlineNodes = Object.values(nodes).filter(n => n.online).length;
    const totalNodes = Object.keys(nodes).length;
    
    // Approximate earnings: ~0.25 MAST per node per day
    const dailyTokens = onlineNodes * 0.25;
    const usd = dailyTokens * this.prices.MAST;

    return {
      nodes: `${onlineNodes}/${totalNodes}`,
      daily_tokens: dailyTokens.toFixed(2),
      token: 'MAST',
      usd: usd.toFixed(4),
      monthly: (usd * 30).toFixed(2)
    };
  }

  async calculateMysterium(nodes) {
    const onlineNodes = Object.values(nodes).filter(n => n.online).length;
    const totalNodes = Object.keys(nodes).length;
    
    // Approximate earnings: ~0.1 MYST per node per day
    const dailyTokens = onlineNodes * 0.1;
    const usd = dailyTokens * this.prices.MYST;

    return {
      nodes: `${onlineNodes}/${totalNodes}`,
      daily_tokens: dailyTokens.toFixed(2),
      token: 'MYST',
      usd: usd.toFixed(4),
      monthly: (usd * 30).toFixed(2)
    };
  }

  async calculateAcurast(status) {
    const onlineDevices = status.online || 0;
    const totalDevices = status.total || 0;
    
    // Approximate earnings: ~1 ACU per device per day
    const dailyTokens = onlineDevices * 1;
    const usd = dailyTokens * this.prices.ACU;

    return {
      devices: `${onlineDevices}/${totalDevices}`,
      daily_tokens: dailyTokens.toFixed(0),
      token: 'ACU',
      usd: usd.toFixed(4),
      monthly: (usd * 30).toFixed(2)
    };
  }

  async calculateWingBits(nodes) {
    const onlineNodes = Object.values(nodes).filter(n => n.online).length;
    const totalNodes = Object.keys(nodes).length;
    
    // Approximate earnings: ~0.5 WINGS per node per day
    const dailyTokens = onlineNodes * 0.5;
    const usd = dailyTokens * this.prices.WINGS;

    return {
      nodes: `${onlineNodes}/${totalNodes}`,
      daily_tokens: dailyTokens.toFixed(2),
      token: 'WINGS',
      usd: usd.toFixed(4),
      monthly: (usd * 30).toFixed(2)
    };
  }

  async calculateNeutroneX(status) {
    const onlineDevices = status.online || 0;
    const totalDevices = status.total || 0;
    
    // Approximate earnings: ~0.3 NEX per device per day
    const dailyTokens = onlineDevices * 0.3;
    const usd = dailyTokens * this.prices.NEX;

    return {
      devices: `${onlineDevices}/${totalDevices}`,
      daily_tokens: dailyTokens.toFixed(2),
      token: 'NEX',
      usd: usd.toFixed(4),
      monthly: (usd * 30).toFixed(2)
    };
  }

  updatePrices(newPrices) {
    this.prices = { ...this.prices, ...newPrices };
  }
}

module.exports = EarningsCalculator;