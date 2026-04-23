# Hermes-Deploy Skills 发布记录

**技能名称**: hermes-deploy  
**版本**: 1.0.0  
**创建时间**: 2026-04-05 22:00  
**发布时间**: 2026-04-05 22:15  
**状态**: ✅ 已发布
**技能 ID**: k97fk38dtr81esbe8b62mc38x5849665

---

## 技能内容

**文件位置**: `/workspace/projects/workspace/skills/hermes-deploy/SKILL.md`

**技能描述**:
使用 OpenClaw 部署 Hermes Agent，从 0 到 1 完成安装、配置迁移和 YOLO 模式开启。

**包含内容**:
1. Hermes Agent 安装（官方脚本 + 手动克隆）
2. 从 OpenClaw 迁移配置（模型、飞书）
3. 飞书 WebSocket 配置
4. YOLO 模式开启
5. 常见问题排查

---

## 发布状态

### 本地状态
- ✅ SKILL.md 已创建
- ⏳ 等待 ClawHub 发布

### ClawHub 状态
- ✅ 已发布
- **技能 ID**: k97fk38dtr81esbe8b62mc38x5849665
- **访问**: https://clawhub.ai/skills/hermes-deploy

---

## 发布命令执行

```bash
# 登录
clawhub login --token clh_gVs0mARZTsQk5JZ0tjGBGfQeA7AG60HoHEouUgBIEUU

# 发布
cd /workspace/projects/workspace/skills/hermes-deploy
clawhub sync --dir skills/hermes-deploy

# 输出：
# ✔ OK. Published hermes-deploy@1.0.0
```

---

**记录时间**: 2026-04-05 22:15  
**最后更新**: 2026-04-05 22:15
