# Claude Code 官方文档地图（精简）

来源根索引：`https://code.claude.com/docs/llms.txt`

## 基础

- Overview: https://code.claude.com/docs/en/overview.md
- Quickstart: https://code.claude.com/docs/en/quickstart.md
- How it works: https://code.claude.com/docs/en/how-claude-code-works.md
- Best practices: https://code.claude.com/docs/en/best-practices.md

## 日常必查

- CLI reference: https://code.claude.com/docs/en/cli-reference.md
- Settings: https://code.claude.com/docs/en/settings.md
- Permissions: https://code.claude.com/docs/en/permissions.md
- Model config: https://code.claude.com/docs/en/model-config.md
- Troubleshooting: https://code.claude.com/docs/en/troubleshooting.md

## 扩展能力

- Skills: https://code.claude.com/docs/en/skills.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Hooks guide: https://code.claude.com/docs/en/hooks-guide.md
- MCP: https://code.claude.com/docs/en/mcp.md
- Sub-agents: https://code.claude.com/docs/en/sub-agents.md
- Plugins: https://code.claude.com/docs/en/plugins.md
- Plugins reference: https://code.claude.com/docs/en/plugins-reference.md

## 快速结论

1. 配置冲突优先级：Managed > CLI > Local > Project > User。
2. 权限规则顺序：deny > ask > allow。
3. MCP 优先 HTTP；SSE 属于兼容路径。
4. 复杂任务建议走 subagent/agent team，减少主会话上下文压力。
5. 高质量结果依赖“可验证目标”（测试、命令输出、截图对比）。
