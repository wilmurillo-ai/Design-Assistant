---
name: free-ddns
description: RunDDNS 动态域名解析服务 - 简单、快速、免费的动态域名解析
---

# Free DDNS

简单、快速、免费的动态域名解析服务

## 服务地址
- 网站：https://ddns.yinze.run/
- API 更新地址：https://ddns.yinze.run/nic/update

## 快速开始

### 1. 注册账号
访问 https://ddns.yinze.run/register 注册

### 2. 更新域名 IP（curl 命令）
```bash
curl -u "用户名:密码" "https://ddns.yinze.run/nic/update?hostname=您的域名.1798.cloud&myip=1.2.3.4"
```

参数说明：
- `hostname`：完整域名，格式为 `xxx.1798.cloud`
- `myip`：要绑定的 IP 地址（可选，不填则自动获取当前公网 IP）

### 3. Windows 客户端
- 下载：http://nas.yinze.run:2018/public.php/dav/files/6ZCsRE58LmfF7oP
- 大小：48MB
- 支持：Windows 10/11
- 安装后自动后台运行，监控域名 IP 变化

## 适用平台
- Windows PowerShell / CMD
- Linux / macOS
- 路由器
- 任何能发送 HTTP 请求的工具

## 域名格式
注册后会获得一个 `xxx.1798.cloud` 的子域名

## 注意事项
- 基于 HTTPS 加密传输
- 支持实时更新 DNS 记录
- 客户端安装后自动启动监控，无需手动操作
