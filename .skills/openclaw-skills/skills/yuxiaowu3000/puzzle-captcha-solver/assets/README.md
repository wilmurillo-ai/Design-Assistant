# 演示截图 / Demo Screenshots

本目录用于存放技能使用演示的截图和 GIF 动图。

---

## 📸 如何录制演示

### 方法 1：手动截图

```bash
# 1. 打开目标页面
agent-browser open "https://search.damai.cn/search.htm?keyword=测试"

# 2. 等待验证码出现
agent-browser wait 3000

# 3. 截图
agent-browser screenshot --full captcha-demo.png

# 4. 识别
python3 scripts/recognize_puzzle.py \
  --screenshot captcha-demo.png \
  --output result.json \
  --debug

# 5. 查看调试图片
ls debug_captcha/
# original.png  - 原图
# marked.png    - 标记检测结果的图
```

### 方法 2：录制 GIF

使用屏幕录制工具（如 LICEcap、ScreenToGif）：

1. 打开录制工具
2. 框选验证码区域
3. 执行识别脚本
4. 停止录制
5. 保存为 `demo-recognition.gif`

---

## 📷 建议的演示内容

### 1. 识别流程演示

展示从截图到识别结果的完整过程：
- 原始验证码截图
- 检测到的验证码区域（绿色框）
- 检测到的滑块位置（红色框）
- 识别结果 JSON

**文件名：** `demo-recognition.gif`

---

### 2. 成功验证演示

展示完整的验证流程：
- 打开页面
- 出现验证码
- 自动识别
- 自动拖动
- 验证成功

**文件名：** `demo-success.gif`

---

### 3. 失败案例演示

展示识别失败的情况和调试方法：
- 识别失败的结果
- 使用 debug 模式查看原因
- 调整参数后重新识别

**文件名：** `demo-failure-debug.gif`

---

### 4. 多网站对比演示

展示不同网站的验证码和识别效果：
- 大麦网（粉色箭头）
- 淘宝（蓝色拼图）
- 京东（蓝色渐变）
- 抖音（彩色拼图）

**文件名：** `demo-websites-comparison.png`

---

## 🎨 截图标注建议

使用图片编辑工具添加标注：

1. **箭头** - 指示关键区域
2. **文字说明** - 解释每个步骤
3. **高亮框** - 标记检测结果
4. **成功/失败标记** - ✅ / ❌

推荐工具：
- macOS: Preview、Sketch
- Windows: Paint.NET、Snipaste
- Linux: GIMP、Flameshot

---

## 📋 当前缺少演示素材

**待录制：**

- [ ] 大麦网识别演示 GIF
- [ ] 淘宝识别演示 GIF
- [ ] 京东识别演示 GIF
- [ ] 识别成功完整流程 GIF
- [ ] Debug 模式演示 GIF
- [ ] 多网站对比图

**欢迎贡献！**

如果你录制了演示素材，欢迎提交到 ClawHub 帮助改进文档~

---

## 🔗 相关链接

- [技能文档](../SKILL.md)
- [使用示例](../SKILL.md#使用示例)
- [故障排除](../SKILL.md#故障排除)
