# QQ Video Watermark Remover

智能 QQ 视频水印去除工具 - 自动识别并去除"豆包 AI 生成"水印

## 功能特点

- ✨ **智能识别**: 多算法投票机制自动检测水印位置
- 🎯 **精确定位**: 支持用户自定义水印位置和时间段
- 🔊 **音频保留**: 使用 FFmpeg 保留原始音频轨道
- 🚀 **批量处理**: 支持批量处理多个视频文件
- 💎 **高质量**: CRF 18 高质量编码，最小化视频损伤
- 🛡️ **安全处理**: 只处理指定区域，不损伤其他画面

## 安装

```bash
# 使用 ClawHub 安装
clawhub install qq-watermark-remover
```

## 使用方法

### 单个视频处理

```bash
python final_perfect.py <输入视频路径> [输出视频路径]
```

**示例:**
```bash
python final_perfect.py /path/to/video.mp4 /path/to/output.mp4
```

### 批量处理

```bash
python batch_final.py
```

**配置:**
修改脚本中的 `VIDEO_DIR` 和 `OUTPUT_DIR` 路径

### 自定义水印位置

编辑 `final_perfect.py` 中的 `user_regions` 配置:

```python
self.user_regions = [
    {"start_sec": 0, "end_sec": 4, "x": 510, "y": 1170, "w": 180, "h": 70, "name": "右下"},
    {"start_sec": 3, "end_sec": 7, "x": 20, "y": 600, "w": 170, "h": 60, "name": "左中"},
    {"start_sec": 6, "end_sec": 10, "x": 510, "y": 20, "w": 180, "h": 70, "name": "右上"},
]
```

**参数说明:**
- `start_sec`: 开始时间（秒）
- `end_sec`: 结束时间（秒）
- `x`, `y`: 水印区域左上角坐标
- `w`, `h`: 水印区域宽度和高度
- `name`: 区域名称（用于日志输出）

## 技术原理

### 智能识别算法

1. **OTSU 阈值**: 自动二值化检测亮色/暗色文字
2. **自适应阈值**: 局部自适应检测不同光照条件
3. **Canny 边缘**: 边缘检测识别文字轮廓
4. **投票机制**: 至少 2 种方法确认才判定为水印

### 修复算法

- **Telea Inpainting**: 快速边缘保持修复
- **Distance Transform Blending**: 距离变换渐变混合，无痕迹

### 音频处理

使用 FFmpeg 双输入映射:
- 输入 1: 处理后的视频流
- 输入 2: 原始视频音频流
- 输出：合并后的视频

## 依赖

```txt
opencv-python>=4.8.0
numpy>=1.24.0
tqdm>=4.65.0
```

**系统要求:**
- Python 3.8+
- FFmpeg (用于视频编码和音频处理)
- macOS / Linux / Windows

## 项目结构

```
qq-watermark-remover/
├── final_perfect.py          # 主程序 - 最终完美版
├── batch_final.py            # 批量处理脚本
├── requirements.txt          # Python 依赖
├── README.md                 # 本文档
├── examples/                 # 示例配置文件
└── tests/                    # 测试用例
```

## 配置示例

### 典型 QQ 视频水印配置

```python
# 豆包 AI 生成水印（10 秒视频）
self.user_regions = [
    # 0-4 秒：右下角
    {"start_sec": 0, "end_sec": 4, "x": 510, "y": 1170, "w": 180, "h": 70},
    # 3-7 秒：左侧中间
    {"start_sec": 3, "end_sec": 7, "x": 20, "y": 600, "w": 170, "h": 60},
    # 6-10 秒：右上角
    {"start_sec": 6, "end_sec": 10, "x": 510, "y": 20, "w": 180, "h": 70},
]
```

### 其他平台水印配置

**抖音水印:**
```python
self.user_regions = [
    {"start_sec": 0, "end_sec": 999, "x": 50, "y": 50, "w": 150, "h": 50},
]
```

**B 站水印:**
```python
self.user_regions = [
    {"start_sec": 0, "end_sec": 999, "x": 10, "y": 10, "w": 100, "h": 40},
]
```

## 性能参考

| 视频规格 | 处理速度 | 输出质量 |
|---------|---------|---------|
| 720x1280, 10 秒 | ~8 秒 | CRF 18 |
| 1080x1920, 30 秒 | ~25 秒 | CRF 18 |
| 1920x1080, 60 秒 | ~50 秒 | CRF 18 |

**注:** 实际速度取决于 CPU 性能和视频内容复杂度

## 常见问题

### Q: 水印去除不干净？
A: 调整 `user_regions` 中的坐标和大小，确保完全覆盖水印区域

### Q: 视频模糊或有痕迹？
A: 增加 `inpaint_and_blend` 中的 `blend_width` 参数（默认 15）

### Q: 音频丢失？
A: 确保安装了 FFmpeg，并检查原始视频是否有音频轨道

### Q: 处理速度慢？
A: 降低 FFmpeg preset 参数（如改为 `medium` 或 `fast`）

## 更新日志

### v1.0.0 (2026-03-15)
- ✨ 初始版本发布
- 🎯 支持用户自定义水印位置和时间
- 🧠 智能识别增强（投票机制）
- 🔊 完整音频保留
- 📦 ClawHub 发布

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请提交 Issue 或联系作者。

---

**开发时间**: 2026-03-15  
**版本**: 1.0.0  
**作者**: mac 小虫子 · 严谨专业版
