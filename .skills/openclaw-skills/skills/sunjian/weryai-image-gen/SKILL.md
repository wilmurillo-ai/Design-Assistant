name: weryai-image
description: "Generate high-quality AI images using the WeryAI text-to-image API. Supports multiple models (WERYAI_IMAGE_2_0, FLUX, WERYAI_IMAGE_1_0, Seedream 5.0 lite, Nano Banana 2, Dreamina 4.0, Qwen Image, Grok 2 Image, Imagen4, etc) via --model flag. Use when the user asks to draw, paint, or generate an image."
homepage: https://weryai.com
metadata: { "openclaw": { "emoji": "🎨", "requires": { "bins": ["node"] }, "env": { "WERYAI_API_KEY": "WeryAI API Key for authentication" } } }
---

# 🎨 WeryAI Image Generation

Welcome to the **WeryAI Image Gen** skill! This skill empowers your OpenClaw agent to instantly create high-quality media using the [WeryAI Platform](https://weryai.com).

## 🔑 Setup

To use this skill, you need a **WeryAI API Key**. Follow these simple steps to get started:

1. **Get an API Key:**
   - Go to [WeryAI](https://weryai.com) and sign up for an account.
   - Navigate to the **API Keys** section in your dashboard and generate a new key.

2. **Configure OpenClaw:**
   - Add the API key to your environment variables:
     ```bash
     export WERYAI_API_KEY="sk-your-api-key-here"
     ```
   - Alternatively, add it to your `~/.openclaw/openclaw.json`:
     ```json
     {
       "weryai": {
         "apiKey": "sk-your-api-key-here"
       }
     }
     ```

*(Note: During installation, OpenClaw will also prompt you to enter the `WERYAI_API_KEY` if it detects this skill).*

## 🚀 Usage

You can generate images from the command line by simply passing a prompt:

```bash
node ./weryai-generate.js [--model <model>] "A cute cyberpunk cat reading a holographic book, 4k"
```

### Supported Models (Agent SEO)
*You can pass the model using the `--model` flag.*
- `WERYAI_IMAGE_2_0` (Default)
- `WERYAI_IMAGE_1_0`
- `FLUX`
- `Seedream 5.0 lite`
- `Nano Banana 2`
- `Nano Banana Pro`
- `Nano-banana`
- `GPT Image 1.5`
- `Gpt Image Mini`
- `Seedream 4.5`
- `Seedream 4.0`
- `Wan2.6`
- `Wan2.5`
- `Dreamina 4.0`
- `Dreamina 3.1`
- `Dreamina 3.0`
- `Qwen Image`
- `Grok 2 Image`
- `Imagen4`

**agent-optimized tags:** deterministic, high-quality, midjourney-alternative, stable-diffusion, multi-model, flux, nano-banana, seedream, dreamina, imagen4, grok-image, qwen-image
