const fs = require('fs');
const path = require('path');

class HistoryTracker {
  constructor() {
    this.dataDir = path.join(process.env.HOME, '.openclaw/workspace/skills/depin-fleet-monitor/data/earnings');
    this.ensureDataDir();
  }

  ensureDataDir() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  getTodayFile() {
    const today = new Date().toISOString().split('T')[0];
    return path.join(this.dataDir, `${today}.json`);
  }

  getMonthFile() {
    const month = new Date().toISOString().slice(0, 7);
    return path.join(this.dataDir, `${month}.json`);
  }

  async saveEarnings(earnings) {
    const todayFile = this.getTodayFile();
    const monthFile = this.getMonthFile();
    
    const record = {
      timestamp: new Date().toISOString(),
      ...earnings
    };

    // Save daily record
    try {
      let dailyData = { records: [] };
      if (fs.existsSync(todayFile)) {
        dailyData = JSON.parse(fs.readFileSync(todayFile, 'utf8'));
      }
      dailyData.records.push(record);
      fs.writeFileSync(todayFile, JSON.stringify(dailyData, null, 2));
    } catch (error) {
      console.error('Failed to save daily earnings:', error.message);
    }

    // Update monthly aggregate
    try {
      let monthlyData = { days: {}, total: { usd: 0 } };
      if (fs.existsSync(monthFile)) {
        monthlyData = JSON.parse(fs.readFileSync(monthFile, 'utf8'));
      }

      const today = new Date().toISOString().split('T')[0];
      monthlyData.days[today] = {
        mastchain: earnings.mastchain,
        mysterium: earnings.mysterium,
        acurast: earnings.acurast,
        total: earnings.total
      };

      // Calculate monthly total
      monthlyData.total = {
        usd: Object.values(monthlyData.days)
          .reduce((sum, day) => sum + parseFloat(day.total?.usd || 0), 0)
          .toFixed(4)
      };

      fs.writeFileSync(monthFile, JSON.stringify(monthlyData, null, 2));
    } catch (error) {
      console.error('Failed to save monthly earnings:', error.message);
    }

    return record;
  }

  async getTodayEarnings() {
    const todayFile = this.getTodayFile();
    try {
      if (fs.existsSync(todayFile)) {
        const data = JSON.parse(fs.readFileSync(todayFile, 'utf8'));
        return data.records[data.records.length - 1] || null;
      }
    } catch (error) {
      console.error('Failed to read today earnings:', error.message);
    }
    return null;
  }

  async getMonthEarnings() {
    const monthFile = this.getMonthFile();
    try {
      if (fs.existsSync(monthFile)) {
        const data = JSON.parse(fs.readFileSync(monthFile, 'utf8'));
        return data;
      }
    } catch (error) {
      console.error('Failed to read monthly earnings:', error.message);
    }
    return null;
  }

  async getEarningsHistory(days = 7) {
    const history = [];
    const today = new Date();

    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const file = path.join(this.dataDir, `${dateStr}.json`);

      try {
        if (fs.existsSync(file)) {
          const data = JSON.parse(fs.readFileSync(file, 'utf8'));
          if (data.records && data.records.length > 0) {
            const lastRecord = data.records[data.records.length - 1];
            history.push({
              date: dateStr,
              ...lastRecord
            });
          }
        }
      } catch (error) {
        // File doesn't exist or can't be read
      }
    }

    return history.reverse();
  }

  calculateROI(investment, earnings) {
    // Calculate return on investment
    if (!investment || investment === 0) return null;

    const monthlyEarnings = parseFloat(earnings.total?.monthly || 0);
    const dailyEarnings = parseFloat(earnings.total?.daily || 0);

    return {
      monthlyROI: ((monthlyEarnings / investment) * 100).toFixed(2),
      yearlyProjection: (dailyEarnings * 365).toFixed(2),
      breakEvenDays: Math.ceil(investment / dailyEarnings),
      breakEvenMonths: (investment / monthlyEarnings).toFixed(1)
    };
  }

  formatEarningsReport(today, history, monthly) {
    let report = '💰 **EARNINGS REPORT**\n';
    report += '━━━━━━━━━━━━━━━━━━━━\n\n';

    // Today
    if (today) {
      report += `📅 **TODAY (${new Date().toLocaleDateString('nl-NL')})**\n`;
      report += `├── MastChain: ${today.mastchain?.daily_tokens || 0} ${today.mastchain?.token || 'MAST'}\n`;
      report += `├── Mysterium: ${today.mysterium?.daily_tokens || 0} ${today.mysterium?.token || 'MYST'}\n`;
      report += `├── Acurast: ${today.acurast?.daily_tokens || 0} ${today.acurast?.token || 'ACU'}\n`;
      report += `└── **Total: $${today.total?.usd || 0}**\n\n`;
    }

    // Monthly
    if (monthly) {
      report += `📊 **THIS MONTH**\n`;
      report += `└── Total: $${monthly.total?.usd || 0}\n\n`;
    }

    // 7-day history
    if (history && history.length > 0) {
      report += `📈 **7-DAY TREND**\n`;
      for (const day of history.slice(-7)) {
        const date = new Date(day.date).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' });
        report += `├── ${date}: $${day.total?.usd || 0}\n`;
      }
    }

    return report;
  }
}

module.exports = HistoryTracker;