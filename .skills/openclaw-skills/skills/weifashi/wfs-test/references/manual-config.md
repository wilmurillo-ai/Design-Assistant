# 手动配置（仅当 setup_auth.sh 脚本失败时参考）

1. `npm i -g mcporter`
2. `mcporter config add ttpos --url https://你的域名/api/v1/ai/mcp`
3. 调用 `/api/v1/ai/login` 获取 JWT，写入 `~/.config/mcporter.json` 的 `mcpServers.ttpos.headers.Authorization`
4. `mcporter list ttpos` 验证
