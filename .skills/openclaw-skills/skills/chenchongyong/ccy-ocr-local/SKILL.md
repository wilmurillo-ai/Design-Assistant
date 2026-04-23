---
name: ccy-ocr-local
description: 本地离线 OCR 技能。对本机图片做文字识别，默认不上传文件、不依赖外部 API Key。适用于截图、文档拍照、扫描件、相机图片中的中英文文本提取。
---

# ccy-ocr-local

使用本技能在 **本机离线** 对图片做 OCR 识别，优先用于：

- 从截图提取文字
- 从文档拍照/扫描件提取文字
- 从相机图片中提取中英文文本
- 需要避免上传文件到外部服务的 OCR 场景

## 何时使用

当用户需要：

- 识别本地图片里的文字
- 不想依赖云端 OCR / API Key
- 在 Jetson / Linux 本机直接跑 OCR
- 先用轻量依赖快速得到可用文本

若追求复杂版面、票据、表格结构、竖排文本或更强中文效果，优先考虑后续单独做 PaddleOCR / RapidOCR 本地技能。

## 入口

脚本入口：`scripts/local_ocr.py`

配套脚本：

- `scripts/benchmark.py`：对样例图比较 `balanced / fast / accurate` 的耗时和输出长度
- `scripts/regression.py`：对样例图生成基线输出，便于回归检查

## 这轮新增能力

- **自动方向检测**：可用 `--autorotate` 尝试方向并选择更优结果
- **更省时的自动旋转策略**：默认 `--autorotate-strategy smart`，先按宽高比做轻判，只有结果太弱才退回全方向检查
- **批量输出防重名**：批量模式输出时保留相对目录结构，避免不同子目录同名图片互相覆盖
- **JSON 输出**：可用 `--json` 输出 OCR 内容和元数据，适合自动化接入

## 依赖要求

最小依赖：

- `python3`
- `tesseract`
- Python 包：`Pillow`、`pytesseract`

可选增强：

- `opencv-python`
  - 装了则使用 OpenCV 预处理，通常准确率更稳
  - 没装也能运行，会自动退回 Pillow 流程
- Tesseract 语言包：`eng`、`chi_sim`

Windows 兼容说明：

- 若当前终端或 agent 没继承到系统 PATH，脚本会尝试自动探测常见安装位置，例如：
  - `C:/Program Files/Tesseract-OCR/tesseract.exe`
- 也可以手动指定：
  - `--tesseract-cmd "C:/Program Files/Tesseract-OCR/tesseract.exe"`
  - 或设置环境变量 `TESSERACT_CMD`

## 默认设计取向

这个技能默认在四个方向做平衡：

- **准确率**：自动纠正 EXIF 方向、灰度化、自动对比度增强、小图放大、二值化
- **速度**：默认 `balanced` 模式只做一次识别；需要时才尝试多 PSM
- **资源占用**：预处理保持轻量，不引入更重的 OCR 框架
- **减少依赖**：OpenCV 是可选项，不是硬依赖

## 参数

- `image_path`：本地图片路径；配合 `--batch` 时也可传目录
- `--lang`：OCR 语言，默认 `eng`
  - 常见值：`eng`、`chi_sim`、`chi_sim+eng`
- `--psm`：显式指定 Tesseract PSM；指定后不再自动试多个模式
- `--mode`：`balanced` / `fast` / `accurate`
  - `balanced`：默认，单次识别，资源最省
  - `fast`：自动试少量常见 PSM，兼顾速度
  - `accurate`：自动试更多 PSM，优先提高命中率
- `--format`：`text` 或 `tsv`
- `--tesseract-cmd`：显式指定 Tesseract 可执行文件路径，适合 Windows / PATH 未继承场景
- `--min-conf`：TSV 模式下过滤低置信度文本
- `--dpi`：传给 Tesseract 的逻辑 DPI，默认 `300`
- `--min-edge`：小图放大的目标长边，默认 `1800`
- `--sharpen`：启用轻量锐化，适合略糊的图
- `--no-preprocess`：关闭基础预处理
- `--out`：单图模式下将结果写入文件
- `--batch`：批量处理模式
- `--recursive`：批量模式下递归扫描子目录
- `--out-dir`：批量模式下输出目录，并生成 `manifest.json`
- `--autorotate`：自动尝试方向，适合拍照方向不稳的图片
- `--autorotate-strategy`：`smart` 或 `full`，默认 `smart`

## 输出

默认输出：

- `text`：纯文本

可选输出：

- `tsv`：带位置和置信度的结构化文本，适合后处理
- `json`：包含文本和元数据（耗时、PSM、旋转角度、模式等），适合自动化流水线
- 批量模式下可输出每张图的文本/TSV/JSON 文件和总清单 `manifest.json`
- `manifest.json` 中会记录每张图的耗时、PSM、旋转角度和输出路径

错误输出：

- 图片不存在或无法打开
- Tesseract 未安装
- 指定语言数据不存在

## 常用示例

### 最小示例

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png
```

### 中英混合识别

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png --lang chi_sim+eng
```

### 提高准确率

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png --lang chi_sim+eng --mode accurate --sharpen --autorotate
```

### 更快一点

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png --mode fast
```

### Windows 显式指定 Tesseract

```bash
python skills/ccy-ocr-local/scripts/local_ocr.py C:/path/to/image.png --tesseract-cmd "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

### 导出结构化 TSV

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png --format tsv --min-conf 40 --out /tmp/result.tsv
```

### JSON 输出

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/image.png --lang chi_sim+eng --autorotate --json
```

### 批量处理目录

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/images --batch --recursive --lang chi_sim+eng --out-dir /tmp/ocr-batch
```

### 批量 JSON 输出

```bash
python3 skills/ccy-ocr-local/scripts/local_ocr.py /path/to/images --batch --recursive --lang chi_sim+eng --autorotate --json --out-dir /tmp/ocr-batch-json
```

### 跑 benchmark

```bash
python3 skills/ccy-ocr-local/scripts/benchmark.py
```

### 跑回归样例

```bash
python3 skills/ccy-ocr-local/scripts/regression.py
```

## 使用建议

- **普通截图/UI 文本**：先用默认参数
- **中英混合材料**：`--lang chi_sim+eng`
- **拍照略糊**：加 `--sharpen`
- **拍照方向不稳**：加 `--autorotate`
- **批量自动化接入**：加 `--json` 或配合 `--out-dir`
- **想省资源**：保持 `balanced`，不要开 `accurate`
- **要后处理**：使用 `--format tsv`
- **多张图流水线处理**：使用 `--batch --out-dir`

## 已知限制

- 普通 Tesseract 对 **复杂排版、公式、表格结构、试卷版面** 支持一般
- 若系统没有安装 `chi_sim.traineddata`，中文识别会失败或效果较差
- 对严重透视变形、阴影、强反光图片，建议先做文档矫正/裁切
- 本技能是轻量本地 OCR，不追求最强中文复杂场景表现
