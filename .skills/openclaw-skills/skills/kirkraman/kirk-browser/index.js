const SKILLBOSS_API_KEY = process.env.SKILLBOSS_API_KEY;
const API_BASE = 'https://api.heybossai.com/v1';

async function pilot(body) {
  const r = await fetch(`${API_BASE}/pilot`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${SKILLBOSS_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return r.json();
}

async function readUrl(url) {
  try {
    const result = await pilot({ type: 'scraper', inputs: { url } });
    return result.result.data.markdown;
  } catch (error) {
    console.error(`Error reading URL: ${error.message}`);
    return `Error: Could not render the page. ${error.message}`;
  }
}

// Basic command-line handler
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const url = args[1];

  if (command === 'read' && url) {
    const content = await readUrl(url);
    console.log(content);
  } else {
    console.log('Usage: node index.js read <url>');
  }
}

main();
