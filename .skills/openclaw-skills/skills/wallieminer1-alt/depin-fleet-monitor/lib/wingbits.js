const https = require('https');
const http = require('http');

class WingBitsAPI {
  constructor(nodes) {
    this.nodes = nodes || {};
  }

  async fetchNode(nodeConfig) {
    const { ip, web_port = 8080, name, location } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/status`;
    
    try {
      const response = await this.httpGet(url);
      return {
        name,
        ip,
        location,
        online: true,
        version: response.version || 'unknown',
        uptime: response.uptime || 0,
        bandwidth: response.bandwidth || { up: 0, down: 0 },
        earnings: response.earnings || { total: 0, pending: 0 },
        web_url: `http://${ip}:${web_port}/`
      };
    } catch (error) {
      return {
        name,
        ip,
        location,
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

  async getEarnings(nodeConfig) {
    const { ip, web_port = 8080 } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/earnings`;
    
    try {
      const response = await this.httpGet(url);
      return {
        total: response.total || 0,
        pending: response.pending || 0,
        token: 'WINGS'
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
}

module.exports = WingBitsAPI;