# ATXSwap 技能

ATX 在 BSC 链上的统一技能包。同一份 `SKILL.md` 同时兼容 **Claude / Cursor /
Codex CLI**（skills.sh 运行时）和 **OpenClaw / ClawHub**，无需为不同客户端维护
多份目录。

[**English**](./README.md)

- **GitHub**: https://github.com/agentswapx/skills
- **SDK (npm)**: [`atxswap-sdk`](https://www.npmjs.com/package/atxswap-sdk)
- **SDK 源码 / 文档**: [agentswapx/atxswap-sdk](https://github.com/agentswapx/atxswap-sdk)

## 能力范围

- 创建或导入当前技能实例使用的单个钱包
- 查询 ATX 价格、余额、LP 仓位和 ERC20 代币信息
- 在 PancakeSwap V3 上买卖 ATX/USDT
- 添加流动性、减仓、收手续费、销毁空仓位 NFT
- 转账 BNB、ATX、USDT 或任意 ERC20 代币

## 目录结构

```text
atxswap/
├── SKILL.md
├── README.md
├── README.zh.md
├── PUBLISH.md
├── CHANGELOG.md
├── .clawhubignore
├── .gitignore
├── package.json
└── scripts/
    ├── _helpers.js
    ├── wallet.js
    ├── query.js
    ├── swap.js
    ├── liquidity.js
    └── transfer.js
```

## 安装

### OpenClaw / ClawHub 一键安装

```bash
openclaw skills install atxswap
# 或
clawhub install atxswap
```

### 手动 / skills.sh 运行时

```bash
git clone https://github.com/agentswapx/skills.git
cd skills/atxswap && npm install
```

可选设置 BSC RPC：

```bash
export BSC_RPC_URL="https://bsc-rpc.publicnode.com"
```

## 常用命令

```bash
cd skills/atxswap && node scripts/wallet.js list
cd skills/atxswap && node scripts/query.js price
cd skills/atxswap && node scripts/query.js quote buy 1
```

在支持 `${SKILL_DIR}` 注入的运行时中，建议使用 `cd "${SKILL_DIR}"`，以便技能
能在客户端管理的任意安装目录下正常运行。

## 安全规则

1. 不要在聊天输出中暴露私钥或密码。
2. 所有写操作前，必须先预览价格、报价、余额或仓位。
3. 交换、转账、流动性操作前，必须等待用户明确确认。
4. 所有写操作都按主网真实资产处理。
