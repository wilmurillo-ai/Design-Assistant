# 护肤管家 (Skincare Manager)

你的私人护肤管理助手，帮你建立科学护肤 routine，追踪产品使用效果。

## 🚀 快速开始

### 安装

```bash
cd ~/.openclaw/workspace/skills/skincare-manager
./install.sh
```

### 使用

```bash
# 1. 肤质测试
./scripts/skin-test.js

# 2. 查询成分
./scripts/query-ingredient.js "烟酰胺"

# 3. 添加护肤流程
./scripts/add-routine.js --time morning --product "氨基酸洁面" --step 1

# 4. 查看流程
./scripts/list-routine.js

# 5. 添加产品
./scripts/add-product.js "SK-II 神仙水" --expiry 2027-12-31

# 6. 查看到期提醒
./scripts/check-expiry.js
```

## 📖 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## ⚠️ 免责声明

本技能提供的所有内容均整理自公开资料，仅供信息参考，不构成专业建议。

- 不替代皮肤科医生诊断或治疗
- 个体差异大，效果因人而异
- 如有不适请咨询专业人士

## 📊 数据来源

- ⭐⭐⭐⭐⭐ 国家药监局化妆品数据库
- ⭐⭐⭐⭐ 化妆品化学教材
- ⭐⭐⭐ COSDNA 成分数据库
- ⭐⭐ 专业人士分享
- ⭐ 用户经验分享

所有信息均标注来源和权威等级。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT-0 License

---

_不做专家，只做负责任的"信息搬运工" 🧴_
