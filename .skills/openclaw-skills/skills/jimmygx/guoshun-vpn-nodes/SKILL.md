---
name: guoshun-vpn-nodes
description: 国顺VPN节点获取技能 - 江苏国顺智能科技有限公司专用。自动搜索、测试并整理可用的V2Ray/Clash免费节点订阅链接，验证可用性，输出可导入的节点配置。功能包括：(1)搜索最新免费节点订阅 (2)验证节点可用性 (3)输出各客户端导入教程。使用场景：员工需要VPN时触发，自动获取可用节点并指导导入。
---

# 国顺VPN节点获取技能

## 功能概述

当员工需要VPN上网时，自动执行以下操作：
1. 从多个来源搜索最新的V2Ray/Clash免费节点
2. 实际测试这些订阅链接的可用性（HTTP状态码）
3. 整理出可用的订阅链接
4. 根据用户使用的客户端，提供具体的导入教程

## 输出格式

```
📡 今日可用VPN节点（2026-XX-XX）

✅ 已验证可用的订阅链接：

【电脑客户端 - Clash for Windows】
订阅地址：https://xxx
节点数量：xx个
覆盖地区：xx/xx/xx

【手机客户端 - V2RayNG / Shadowrocket】
订阅地址：https://xxx

---

📱 导入教程：

（根据客户端类型给出具体步骤）
```

## 已知可靠的订阅来源

### 2026-04-03 验证结果

| 来源 | 订阅类型 | 状态 | 节点数 | 备注 |
|-----|---------|:----:|:------:|------|
| yoyapai.com | Clash/YAML | ✅ | 78个 | 综合多协议 |
| yoyapai.com | V2Ray/TXT | ✅ | 48个 | VMess/VLESS/Trojan |
| naidounode.cczzuu.top | v2ray | ✅ | 48个 | 每日更新 |

## 节点搜索关键词

- `v2ray 免费节点 2026`
- `clash 免费订阅 2026`
- `vmess vless free node April 2026`
- `free vpn subscription 2026`

## 验证方法

使用 curl 测试订阅链接：
```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}s %{url_effective}" <订阅链接> --max-time 10
```

状态码200 = 可用

## 各客户端导入教程

### 1. Clash for Windows（电脑）
1. 下载 Clash for Windows：https://github.com/Fndroid/clash_for_windows_pkg/releases
2. 打开软件 → 点击左侧「配置」
3. 点击「新建」
4. 粘贴订阅地址（YAML格式）→ 点击下载
5. 选择节点 → 点击「代理」启用

### 2. V2RayNG（安卓）
1. 下载 V2RayNG（应用商店搜索或GitHub）
2. 打开 → 点击右上角「订阅」
3. 点击「添加订阅」
4. 粘贴订阅地址（VMess格式）
5. 点击更新，导入节点
6. 选择节点 → 点击V字图标连接

### 3. Shadowrocket（iOS）
1. App Store下载 Shadowrocket
2. 打开 → 点击右上角「+」
3. 类型选择「Subscribe」
4. 粘贴订阅地址
5. 点击完成，自动更新节点
6. 选择节点，开启VPN

### 4. Clash for Android
1. 下载 Clash for Android（GitHub）
2. 打开 → 点击「配置」
3. 点击「新建配置」或「从URL导入」
4. 粘贴订阅地址 → 确认
5. 选择节点 → 点击连接

### 5. Stash（iOS，Clash Meta）
1. App Store下载 Stash
2. 打开 → 点击左侧「配置」
3. 点击「远程」
4. 点击「添加」
5. 粘贴订阅地址 → 保存
6. 选择节点，开启VPN

## 注意事项

- 免费节点可能随时失效，建议保存多个来源
- 使用VPN时避免访问敏感网站
- 重要账户操作建议断开VPN
- 建议使用前将DNS设为8.8.8.8或114.114.114.114

## 调用方式

用户说"我要VPN"、"帮我找节点"、"需要翻墙"等时触发。
