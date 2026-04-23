---
name: paperbanana-dashscope
description: Generate publication-quality academic diagrams from paper methodology text (DashScope/Alibaba Cloud adaptation)
license: MIT-0
dependencies:
  env:
    - OPENAI_API_KEY (DashScope API key, required)
  runtime:
    - python3
    - uv
---

# PaperBanana-DashScope

基于阿里云 DashScope API 的学术论文插图自动生成工具。从论文方法章节文本和图注出发，通过多智能体流水线（Retriever → Planner → Stylist → Visualizer → Critic）生成可直接用于投稿的学术插图。

本项目是 PaperBanana/PaperVizAgent 的 DashScope 适配版，将 VLM 替换为 qwen-vl-max，图像生成替换为 wanx2.1-t2i-turbo。

## Environment Setup

```bash
cd <repo-root>
uv pip install -r requirements.txt
```

设置 DashScope API Key（通过环境变量或 `configs/model_config.yaml`）：

```bash
export OPENAI_API_KEY="sk-your-dashscope-api-key"
```

或在 `configs/model_config.yaml` 中配置：

```yaml
api_keys:
  openai_api_key: "sk-your-dashscope-api-key"

dashscope:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_base: "https://dashscope.aliyuncs.com"
  image_gen_model_name: "wanx2.1-t2i-turbo"
```

## Usage

```bash
python skill/run.py \
  --content "METHOD_TEXT" \
  --caption "FIGURE_CAPTION" \
  --task diagram \
  --output output.png
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--content` | Yes* | | 要可视化的方法章节文本 |
| `--content-file` | Yes* | | 包含方法文本的文件路径（替代 `--content`） |
| `--caption` | Yes | | 图注或视觉意图描述 |
| `--task` | No | `diagram` | 任务类型：`diagram` 或 `plot` |
| `--output` | No | `output.png` | 输出图像文件路径 |
| `--aspect-ratio` | No | `21:9` | 宽高比：`21:9`、`16:9` 或 `3:2` |
| `--max-critic-rounds` | No | `3` | Critic 最大迭代轮数 |
| `--num-candidates` | No | `10` | 并行生成候选图数量 |
| `--retrieval-setting` | No | `auto` | 检索模式：`auto`、`manual`、`random` 或 `none` |
| `--main-model-name` | No | `qwen-vl-max` | VLM 主模型（通过 DashScope 兼容模式调用） |
| `--image-gen-model-name` | No | `wanx2.1-t2i-turbo` | 图像生成模型（通过 DashScope 原生 API 调用） |
| `--exp-mode` | No | `demo_full` | 流水线模式：`demo_full`（含 Stylist）或 `demo_planner_critic`（不含 Stylist） |

*`--content` 和 `--content-file` 二选一。

当 `--num-candidates` > 1 时，输出文件命名为 `<stem>_0.png`、`<stem>_1.png` 等。

## Output

每张保存的图像绝对路径会逐行输出到 stdout。

## Examples

### Diagram

```bash
python skill/run.py \
  --content "We propose a transformer-based encoder-decoder architecture. The encoder consists of 12 self-attention layers with residual connections. The decoder uses cross-attention to attend to encoder outputs and generates the target sequence autoregressively." \
  --caption "Figure 1: Overview of the proposed transformer architecture" \
  --task diagram \
  --output architecture.png
```

## Important Notes

- **Runtime**: 单个候选图通常需要 3-10 分钟。默认 10 个候选并行生成，总计约 10-30 分钟。
- **API calls**: 每个候选涉及多次 LLM 调用（Retriever + Planner + Stylist + Visualizer + 最多 3 轮 Critic）。
- **Image generation**: Visualizer Agent 通过 DashScope 原生异步 API 调用 wanx2.1-t2i-turbo 生成图像。
- **DashScope 适配**: VLM 调用通过 DashScope 的 OpenAI 兼容模式（qwen-vl-max），图像生成通过 DashScope 原生 API。

## About

本项目基于 **PaperVizAgent** 框架，是一个参考驱动的多智能体学术插图自动生成系统。

> **PaperBanana: Automating Academic Illustration for AI Scientists**
> Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister, Jinsung Yoon
> arXiv:2601.23265

DashScope 适配由 [TashanGKD](https://github.com/TashanGKD) 完成。