# 通用约束与约定

## 1. 生产域名约束
- 仅允许生产域名：`{api_domain}`（API）、`{web_domain}`（Web）、`{auth_domain}`（鉴权）
- 禁止在发布内容中出现本地开发地址或非生产协议地址

## 2. Header 规范
所有业务接口统一携带：
- `access-token`（必传）
- `Content-Type: application/json`（POST）

## 11. 脚本语言限制
- 所有 `scripts/` 下的脚本**必须使用 Python 编写**（`.py` 后缀）。
