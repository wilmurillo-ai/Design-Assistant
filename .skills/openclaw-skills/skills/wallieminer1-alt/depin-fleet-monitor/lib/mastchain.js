const https = require('https');
const http = require('http');

class MastChainAPI {
  constructor(nodes) {
    this.nodes = nodes || {};
  }

  async fetchNode(nodeConfig) {
    const { ip, web_port = 8100, name } = nodeConfig;
    const url = `http://${ip}:${web_port}/`;
    
    try {
      const response = await this.httpGet(url);
      return {
        name,
        ip,
        online: true,
        web_url: url,
        ...response
      };
    } catch (error) {
      return {
        name,
        ip,
        online: false,
        error: error.message
      };
    }
  }

  async checkAll() {
    const results = {};
    
    for (const [key, config] of Object.entries(this.nodes)) {
      results[config.name || key] = await this.fetchNode(config);
    }
    
    return results;
  }

  async getAISData(nodeConfig) {
    const { ip, web_port = 8100 } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/ais`;
    
    try {
      const response = await this.httpGet(url);
      return {
        ships: response.ships || response.count || 0,
        messages: response.messages || 0
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  httpGet(url) {
    return new Promise((resolve, reject) => {
      const client = url.startsWith('https') ? https : http;
      
      const req = client.get(url, { timeout: 5000 }, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          try {
            if (res.headers['content-type']?.includes('application/json')) {
              resolve(JSON.parse(data));
            } else {
              resolve({ raw: data, status: res.statusCode });
            }
          } catch (err) {
            reject(new Error(`Parse error: ${err.message}`));
          }
        });
      });
      
      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
    });
  }

  async ping(ip) {
    const { exec } = require('child_process');
    return new Promise((resolve) => {
      exec(`ping -c 1 -W 2 ${ip}`, (error, stdout, stderr) => {
        resolve(!error);
      });
    });
  }
}

module.exports = MastChainAPI;