const MastChain = require('./lib/mastchain');
const Mysterium = require('./lib/mysterium');
const Acurast = require('./lib/acurast');
const WingBits = require('./lib/wingbits');
const NeutroneX = require('./lib/neutronex');
const Earnings = require('./lib/earnings');
const AlertManager = require('./lib/alerts');
const HistoryTracker = require('./lib/history');
const fs = require('fs');
const path = require('path');

// Fleet config
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw/workspace/config/fleet-config.json');

class DePINFleetMonitor {
  constructor() {
    this.config = this.loadConfig();
    this.mastchain = new MastChain(this.config.mastchain);
    this.mysterium = new Mysterium(this.config.mysterium);
    this.acurast = new Acurast(this.config.acurast);
    this.wingbits = new WingBits(this.config.wingbits);
    this.neutronex = new NeutroneX(this.config.neutronex);
    this.earnings = new Earnings();
    this.alerts = new AlertManager();
    this.history = new HistoryTracker();
  }

  loadConfig() {
    try {
      if (fs.existsSync(CONFIG_PATH)) {
        return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      }
    } catch (err) {
      console.error('Error loading fleet config:', err.message);
    }
    return this.getDefaultConfig();
  }

  getDefaultConfig() {
    return {
      mastchain: {
        node1: { ip: 'YOUR_MASTCHAIN_IP', name: 'MastChain1', location: 'Location1', web_port: 8100 },
        node2: { ip: 'YOUR_MASTCHAIN2_IP', name: 'MastChain2', location: 'Location2', web_port: 8100 }
      },
      mysterium: {
        node1: { ip: 'YOUR_MYSTERIUM_IP', name: 'Mysterium #1', location: 'Location1', web_port: 4449 },
        node2: { ip: 'YOUR_MYSTERIUM2_IP', name: 'Mysterium #2', location: 'Location2', web_port: 4449 }
      },
      acurast: {
        wallet: 'YOUR_ACURAST_WALLET',
        devices: 0
      },
      wingbits: {
        enabled: false // Set to true when WingBits nodes are added
      },
      neutronex: {
        wallet: 'YOUR_NEUTRONEX_WALLET',
        devices: 0
      }
    };
  }

  async checkAll() {
    const results = {
      mastchain: await this.mastchain.checkAll(),
      mysterium: await this.mysterium.checkAll(),
      acurast: await this.acurast.checkStatus(),
      timestamp: new Date().toISOString()
    };

    // Add WingBits if enabled
    if (this.config.wingbits?.enabled) {
      results.wingbits = await this.wingbits.checkAll();
    }

    // Add NeutroneX if configured
    if (this.config.neutronex) {
      results.neutronex = await this.neutronex.checkStatus();
    }

    const health = this.calculateHealth(results);
    
    // Check for alerts
    const alerts = this.alerts.checkFleetHealth({ ...results, health });
    
    // Save earnings history
    const earnings = await this.earnings.calculate(results);
    await this.history.saveEarnings(earnings);

    return { ...results, health, alerts };
  }

  calculateHealth(results) {
    let total = 0;
    let online = 0;

    // MastChain
    for (const node of Object.values(results.mastchain)) {
      total++;
      if (node.online) online++;
    }

    // Mysterium
    for (const node of Object.values(results.mysterium)) {
      total++;
      if (node.online) online++;
    }

    // Acurast
    total += results.acurast.total || 0;
    online += results.acurast.online || 0;

    // WingBits
    if (results.wingbits) {
      for (const node of Object.values(results.wingbits)) {
        total++;
        if (node.online) online++;
      }
    }

    // NeutroneX
    if (results.neutronex) {
      total += results.neutronex.total || 0;
      online += results.neutronex.online || 0;
    }

    return {
      total,
      online,
      percentage: total > 0 ? Math.round((online / total) * 100) : 0
    };
  }

  async getEarnings() {
    const status = await this.checkAll();
    return this.earnings.calculate(status);
  }

  formatReport(results) {
    let report = '📊 **DePIN Fleet Monitor**\n';
    report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    // MastChain
    report += '🏭 **MASTCHAIN**\n';
    for (const [name, node] of Object.entries(results.mastchain)) {
      const status = node.online ? '✅' : '❌';
      const info = node.messages || node.ships ? `(${node.messages || node.ships} ${node.messages ? 'messages' : 'ships'})` : '';
      report += `├── ${name}: ${status} ${info}\n`;
    }
    report += '\n';

    // Mysterium
    report += '🔒 **MYSTERIUM**\n';
    for (const [name, node] of Object.entries(results.mysterium)) {
      const status = node.online ? '✅' : '❌';
      const location = node.location || '';
      report += `├── ${name}: ${status} (${location})\n`;
    }
    report += '\n';

    // Acurast
    report += '📱 **ACURAST**\n';
    const acurastStatus = results.acurast.online > 0 ? '✅' : '❌';
    report += `├── Devices: ${results.acurast.online}/${results.acurast.total} ${acurastStatus}\n`;
    if (results.acurast.wallet) {
      report += `└── Wallet: ${results.acurast.wallet.slice(0, 10)}...${results.acurast.wallet.slice(-6)}\n`;
    }
    report += '\n';

    // WingBits (if enabled)
    if (results.wingbits) {
      report += '🌐 **WINGBITS**\n';
      for (const [name, node] of Object.entries(results.wingbits)) {
        const status = node.online ? '✅' : '❌';
        report += `├── ${name}: ${status}\n`;
      }
      report += '\n';
    }

    // NeutroneX (if configured)
    if (results.neutronex) {
      report += '⚡ **NEUTRONEX**\n';
      const nxStatus = results.neutronex.online > 0 ? '✅' : '❌';
      report += `├── Devices: ${results.neutronex.online}/${results.neutronex.total} ${nxStatus}\n`;
      if (results.neutronex.wallet) {
        report += `└── Wallet: ${results.neutronex.wallet.slice(0, 10)}...${results.neutronex.wallet.slice(-6)}\n`;
      }
      report += '\n';
    }

    // Health
    report += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    report += `**Fleet Health:** ${results.health.online}/${results.health.total} (${results.health.percentage}%)\n`;

    // Alerts
    if (results.alerts && results.alerts.length > 0) {
      report += '\n⚠️ **ALERTS**\n';
      for (const alert of results.alerts) {
        const icon = alert.level === 'critical' ? '🔴' : '⚠️';
        report += `${icon} ${alert.message}\n`;
      }
    }

    return report;
  }
}

// Export for OpenClaw skill
module.exports = {
  name: 'depin-fleet-monitor',
  description: 'Monitor all DePIN nodes (MastChain, Mysterium, WingBits, Acurast)',
  version: '1.0.0',
  
  // Skill handler
  handler: async (context) => {
    const monitor = new DePINFleetMonitor();
    
    // Parse command
    const message = context.message.toLowerCase();
    
    if (message.includes('earnings') || message.includes('verdien')) {
      const earnings = await monitor.getEarnings();
      return { text: `💰 Earnings Report:\n${JSON.stringify(earnings, null, 2)}` };
    }
    
    if (message.includes('mastchain')) {
      const status = await monitor.mastchain.checkAll();
      return { text: `🏭 MastChain Status:\n${JSON.stringify(status, null, 2)}` };
    }
    
    if (message.includes('mysterium')) {
      const status = await monitor.mysterium.checkAll();
      return { text: `🔒 Mysterium Status:\n${JSON.stringify(status, null, 2)}` };
    }
    
    if (message.includes('acurast')) {
      const status = await monitor.acurast.checkStatus();
      return { text: `📱 Acurast Status:\n${JSON.stringify(status, null, 2)}` };
    }
    
    // Default: check all
    const results = await monitor.checkAll();
    return { text: monitor.formatReport(results) };
  },

  // Export class for direct use
  DePINFleetMonitor
};