const stocks = ['sh000651', 'sh600519', 'sh600900', 'sh300433'];
const https = require('https');

function getStockPrice(code) {
  return new Promise((resolve) => {
    const url = `https://qt.gtimg.cn/q=${code}`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const match = data.match(/="([^"]+)"/);
          if (match) {
            const parts = match[1].split('~');
            resolve({
              code: code.replace('sh',''),
              name: parts[1],
              price: parseFloat(parts[3]),
              change: parseFloat(parts[4]),
              pct: parseFloat(parts[5]),
              volume: parseInt(parts[6])
            });
          } else {
            resolve({ code: code.replace('sh',''), error: 'No data', raw: data.substring(0,100) });
          }
        } catch(e) {
          resolve({ code: code.replace('sh',''), error: e.message });
        }
      });
    }).on('error', () => resolve({ code: code.replace('sh',''), error: 'Request failed' }));
  });
}

(async () => {
  const results = await Promise.all(stocks.map(s => getStockPrice(s)));
  console.log(JSON.stringify(results, null, 2));
})();
