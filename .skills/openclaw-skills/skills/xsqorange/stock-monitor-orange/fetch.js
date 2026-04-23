const stocks = ['000651', '600519', '600900', '300433', '00992', '00981', '06888'];
const https = require('https');

function getStockPrice(code) {
  return new Promise((resolve) => {
    const isHK = code.length >= 5;
    const url = isHK 
      ? `https://qt.gtimg.cn/q=hk${code}`
      : `https://qt.gtimg.cn/q=sh${code}`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const match = data.match(/="([^"]+)"/);
          if (match) {
            const parts = match[1].split('~');
            resolve({
              code,
              name: parts[1],
              price: parseFloat(parts[3]),
              change: parseFloat(parts[4]),
              pct: parseFloat(parts[5]),
              volume: parseInt(parts[6])
            });
          } else {
            resolve({ code, error: 'No data', raw: data.substring(0,100) });
          }
        } catch(e) {
          resolve({ code, error: e.message });
        }
      });
    }).on('error', () => resolve({ code, error: 'Request failed' }));
  });
}

(async () => {
  const results = await Promise.all(stocks.map(s => getStockPrice(s)));
  console.log(JSON.stringify(results, null, 2));
})();
