const fs = require('fs');
const path = require('path');

class AlertManager {
  constructor() {
    this.alertsFile = path.join(process.env.HOME, '.openclaw/workspace/skills/depin-fleet-monitor/data/alerts.json');
    this.historyFile = path.join(process.env.HOME, '.openclaw/workspace/skills/depin-fleet-monitor/data/alerts-history.json');
    this.thresholds = {
      nodeOffline: { warning: 5, critical: 15 }, // minutes
      fleetHealth: { warning: 80, critical: 50 }, // percentage
      earningsDrop: { warning: 50, critical: 90 }, // percentage drop
      highTemp: { warning: 55, critical: 60 }, // celsius
      lowMemory: { warning: 85, critical: 95 } // percentage
    };
    this.loadAlerts();
  }

  loadAlerts() {
    try {
      if (fs.existsSync(this.alertsFile)) {
        this.alerts = JSON.parse(fs.readFileSync(this.alertsFile, 'utf8'));
      } else {
        this.alerts = { active: [], history: [] };
      }
    } catch (error) {
      this.alerts = { active: [], history: [] };
    }
  }

  saveAlerts() {
    try {
      const dir = path.dirname(this.alertsFile);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.alertsFile, JSON.stringify(this.alerts, null, 2));
    } catch (error) {
      console.error('Failed to save alerts:', error.message);
    }
  }

  checkFleetHealth(fleetStatus) {
    const alerts = [];
    const health = fleetStatus.health;

    // Check fleet health percentage
    if (health.percentage < this.thresholds.fleetHealth.critical) {
      alerts.push(this.createAlert('critical', 'fleet', 
        `Fleet health critical: ${health.online}/${health.total} (${health.percentage}%)`));
    } else if (health.percentage < this.thresholds.fleetHealth.warning) {
      alerts.push(this.createAlert('warning', 'fleet', 
        `Fleet health low: ${health.online}/${health.total} (${health.percentage}%)`));
    }

    // Check individual nodes
    for (const [name, node] of Object.entries(fleetStatus.mastchain || {})) {
      if (!node.online) {
        alerts.push(this.createAlert('critical', 'node', `${name} (MastChain) is offline`));
      }
    }

    for (const [name, node] of Object.entries(fleetStatus.mysterium || {})) {
      if (!node.online) {
        alerts.push(this.createAlert('critical', 'node', `${name} (Mysterium) is offline`));
      }
    }

    if (fleetStatus.acurast) {
      const acurastHealth = (fleetStatus.acurast.online / fleetStatus.acurast.total) * 100;
      if (acurastHealth < this.thresholds.fleetHealth.warning) {
        alerts.push(this.createAlert('warning', 'acurast', 
          `Acurast devices low: ${fleetStatus.acurast.online}/${fleetStatus.acurast.total}`));
      }
    }

    return alerts;
  }

  createAlert(level, type, message) {
    return {
      id: `${type}-${Date.now()}`,
      level,
      type,
      message,
      timestamp: new Date().toISOString(),
      acknowledged: false
    };
  }

  addAlert(alert) {
    // Check if similar alert already exists
    const existing = this.alerts.active.find(a => 
      a.type === alert.type && a.message === alert.message && !a.acknowledged
    );

    if (!existing) {
      this.alerts.active.push(alert);
      this.saveAlerts();
      return alert;
    }
    return null;
  }

  acknowledgeAlert(alertId) {
    const alert = this.alerts.active.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      this.alerts.history.push({
        ...alert,
        acknowledgedAt: new Date().toISOString()
      });
      this.alerts.active = this.alerts.active.filter(a => a.id !== alertId);
      this.saveAlerts();
      return true;
    }
    return false;
  }

  getActiveAlerts() {
    return this.alerts.active.filter(a => !a.acknowledged);
  }

  getAlertHistory(limit = 50) {
    return this.alerts.history.slice(-limit);
  }

  clearAlerts() {
    this.alerts.active = [];
    this.saveAlerts();
  }

  // Telegram notification (requires message tool integration)
  formatForTelegram(alerts) {
    if (alerts.length === 0) {
      return '✅ Geen actieve alerts';
    }

    let message = '⚠️ **DEPIN FLEET ALERTS**\n';
    message += '━━━━━━━━━━━━━━━━━━━━\n\n';

    const critical = alerts.filter(a => a.level === 'critical');
    const warning = alerts.filter(a => a.level === 'warning');

    if (critical.length > 0) {
      message += '🔴 **CRITICAL**\n';
      for (const alert of critical) {
        message += `• ${alert.message}\n`;
      }
      message += '\n';
    }

    if (warning.length > 0) {
      message += '⚠️ **WARNING**\n';
      for (const alert of warning) {
        message += `• ${alert.message}\n`;
      }
    }

    message += `\n_${new Date().toLocaleString('nl-NL')}_`;
    return message;
  }
}

module.exports = AlertManager;