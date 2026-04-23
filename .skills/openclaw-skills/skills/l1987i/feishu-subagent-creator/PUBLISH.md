# 发布到 GitHub 指南

## 当前状态

✅ 本地 Git 仓库已初始化
✅ 所有文件已提交（10 个文件，2456 行代码）
⚠️ 需要完成以下步骤才能推送到 GitHub

---

## 步骤 1：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写以下信息：
   - **Repository name**: `feishu-subagent-creator`
   - **Description**: 飞书子 Agent 创建向导 Skill - 全自动配置，无需手动编辑文件
   - **Visibility**: Public 或 Private（根据你的需求）
   - ❌ **不要**勾选"Initialize this repository with a README"
   - ❌ **不要**勾选".gitignore"
   - ❌ **不要**选择 License
3. 点击「Create repository」

---

## 步骤 2：添加 SSH 公钥到 GitHub

### 2.1 复制公钥

执行以下命令复制公钥：
```bash
cat ~/.ssh/github_key.pub
```

或者直接复制以下内容：
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIADOXmMtHCaQd68nldNf/2wL/zGJZXwJMDusvG4Okamg l1987i@gmail.com
```

### 2.2 添加到 GitHub

1. 访问 https://github.com/settings/keys
2. 点击「New SSH key」
3. 填写：
   - **Title**: `OpenClaw Server`
   - **Key type**: Authentication Key
   - **Key**: 粘贴上面的公钥内容
4. 点击「Add SSH key」

---

## 步骤 3：推送代码

完成上述步骤后，执行：

```bash
cd /home/gem/workspace/agent/skills/feishu-subagent-creator
git push -u origin main
```

---

## 验证推送成功

访问 https://github.com/l1987i/feishu-subagent-creator 确认代码已上传。

---

## 使用此 Skill

### 方式 1：克隆到本地

```bash
git clone git@github.com:l1987i/feishu-subagent-creator.git
cd feishu-subagent-creator
```

### 方式 2：通过 OpenClaw 安装

（待添加安装说明）

---

## 故障排查

### 问题：Permission denied (publickey)

**原因：** SSH 密钥未正确配置

**解决方案：**
1. 确认已在 GitHub 添加公钥
2. 确认私钥文件存在：`~/.ssh/github_key`
3. 确认权限正确：`chmod 600 ~/.ssh/github_key`
4. 测试连接：`ssh -T git@github.com`

### 问题：Repository not found

**原因：** GitHub 仓库不存在

**解决方案：** 按照步骤 1 创建仓库

### 问题：Authentication failed

**原因：** 使用了 HTTPS 但没有正确的凭证

**解决方案：** 改用 SSH 方式：
```bash
git remote set-url origin git@github.com:l1987i/feishu-subagent-creator.git
git push -u origin main
```
