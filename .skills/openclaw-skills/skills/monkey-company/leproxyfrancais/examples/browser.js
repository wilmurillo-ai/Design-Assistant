/** Le Proxy Français — Navigateur (Playwright Firefox via WebSocket) */
const { firefox } = require("playwright");

(async () => {
  const browser = await firefox.connect(
    `ws://nav.prx.lv:80/ghost?api_key=${process.env.LPF_API_KEY}`
  );
  const page = await browser.newPage();
  await page.goto("https://api.ipify.org");
  console.log(`IP: ${await page.innerText("body")}`);
  await browser.close();
})();
