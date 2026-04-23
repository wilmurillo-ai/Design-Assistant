# 中医舌像分析技能安装指南

## 产品信息
- **名称**: 中医舌像分析
- **版本**: 1.0.0
- **作者**: 中医AI团队
- **价格**: 6.0 元人民币
- **创建时间**: 2026-03-29T12:29:54.059936

## 系统要求
- **操作系统**: Windows, Linux, macOS
- **内存**: 最少 512 MB
- **磁盘空间**: 最少 100 MB
- **Python版本**: >=3.8

## 安装步骤

### 方法1: 通过ClawHub安装（推荐）
```bash
# 从ClawHub安装
npx clawhub@latest install 中医舌像分析

# 或使用包名
npx clawhub@latest install tcm-tongue-analyzer
```

### 方法2: 手动安装
1. 下载.skill包文件
2. 解压到OpenClaw技能目录:
   ```bash
   # Windows
   mkdir "%USERPROFILE%\.openclaw\skills\中医舌像分析"
   
   # Linux/macOS
   mkdir -p ~/.openclaw/skills/中医舌像分析
   ```
3. 将解压后的文件复制到技能目录
4. 重启OpenClaw或刷新技能列表

## 使用方法

### 基本命令
```bash
# 分析单张舌象照片
tcm-tongue analyze --image "舌象照片路径"

# 批量分析
tcm-tongue batch --folder "舌象照片文件夹"

# 生成详细报告
tcm-tongue report --image "照片路径" --output "报告文件"
```

### 参数说明
- `--image`: 舌象照片路径（支持JPG、PNG格式）
- `--format`: 输出格式（text/json/html）
- `--detail`: 详细程度（basic/standard/detailed）
- `--compare`: 对比分析多张照片

## 功能验证

安装完成后，运行测试验证功能：
```bash
# 进入技能目录
cd ~/.openclaw/skills/中医舌像分析/scripts

# 运行测试
python test_tongue_analyzer.py
```

所有测试应该通过，输出包含：
1. 舌象特征分析
2. 中医辨证结果
3. 治疗建议（组方+穴位）
4. 生活调理建议

## 文件清单

本技能包包含以下文件：
```
SKILL.md                                    4.1 KB
references\tongue_diagnosis_guide.md        5.4 KB
scripts\test_tongue_analyzer.py             7.7 KB
scripts\tongue_analyzer.py                  9.3 KB

```

## 技术支持

如有问题或建议，请联系：
- 邮箱: support@tcm-tongue.com
- 网站: https://tcm-tongue.clawhub.ai
- 文档: 参考技能目录中的references/目录

## 更新日志

### v1.0.0
- 初始版本发布
- 基础舌色分类功能
- 简单辨证建议
- 批量处理功能

## 免责声明

本工具为中医诊断辅助工具，不能替代专业医师诊断。临床决策请咨询执业中医师。

---

**购买即表示您同意以上条款**
