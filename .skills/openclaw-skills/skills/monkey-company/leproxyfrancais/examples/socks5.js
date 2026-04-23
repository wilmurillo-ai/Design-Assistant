/** Le Proxy Français — Proxy SOCKS5 (Mutualisé ou Dédié) */
const { SocksProxyAgent } = require("socks-proxy-agent");

// Mutualisé (3 crédits/Go) — changer en ded.prx.lv:1081 pour Dédié (8 crédits/Go)
const agent = new SocksProxyAgent(
  `socks5h://${process.env.LPF_API_KEY}@mut.prx.lv:1080`
);

fetch("https://ipinfo.io/ip", { agent }).then(async (res) => {
  console.log(`IP: ${await res.text()}`);
});
