const stocks = [
  {code: 'sz000651', name: '000651'},
  {code: 'sh600519', name: '600519'},
  {code: 'sh600900', name: '600900'},
  {code: 'sz300433', name: '300433'},
  {code: 'hk00992', name: '00992'},
  {code: 'hk00981', name: '00981'},
  {code: 'hk06888', name: '06888'}
];
const https = require('https');

function getStockPrice(item) {
  return new Promise((resolve) => {
    const url = `https://qt.gtimg.cn/q=${item.code}`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const match = data.match(/="([^"]+)"/);
          if (match) {
            const parts = match[1].split('~');
            const isHK = item.code.startsWith('hk');
            resolve({
              code: item.name,
              name: parts[1],
              price: parseFloat(parts[3]),
              change: parseFloat(parts[4]),
              pct: parseFloat(parts[5]),
              volume: parseInt(parts[6])
            });
          } else {
            resolve({ code: item.name, error: 'No data' });
          }
        } catch(e) {
          resolve({ code: item.name, error: e.message });
        }
      });
    }).on('error', () => resolve({ code: item.name, error: 'Request failed' }));
  });
}

(async () => {
  const results = await Promise.all(stocks.map(s => getStockPrice(s)));
  console.log(JSON.stringify(results, null, 2));
})();
