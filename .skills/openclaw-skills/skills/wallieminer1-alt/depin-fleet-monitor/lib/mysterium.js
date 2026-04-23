const https = require('https');
const http = require('http');

class MysteriumAPI {
  constructor(nodes) {
    this.nodes = nodes || {};
  }

  async fetchNode(nodeConfig) {
    const { ip, web_port = 4449, name, location } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/v2/node`;
    
    try {
      const response = await this.httpGet(url);
      return {
        name,
        ip,
        location,
        online: true,
        identity: response.identity || null,
        proposals: response.proposals || 0,
        nat_type: response.nat_type || 'unknown',
        version: response.version || 'unknown',
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

  async getIdentity(nodeConfig) {
    const { ip, web_port = 4449 } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/v2/identity`;
    
    try {
      const response = await this.httpGet(url);
      return {
        address: response.address || response.identity,
        registered: response.registered || false,
        stake: response.stake || 0
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  async getEarnings(nodeConfig) {
    const { ip, web_port = 4449 } = nodeConfig;
    const url = `http://${ip}:${web_port}/api/v2/earnings`;
    
    try {
      const response = await this.httpGet(url);
      return {
        total: response.total || 0,
        today: response.today || 0,
        pending: response.pending || 0
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

module.exports = MysteriumAPI;