---
name: finance-ocr-pro
description: Use this skill when the user asks to OCR, transcribe, extract, or convert the contents of a scanned PDF, image, or office document into Markdown, HTML, DOCX, or Excel. This workflow sends page images and OCR prompts to a configured OpenAI-compatible VLM endpoint and requires `API_KEY`, `BASE_URL`, and `VLM_MODEL`. It is especially valuable for financial documents and other visually complex materials with dense tables, charts, graphs, and multi-part layouts. Prefer durable background jobs for long-running OCR work.
requires:
  env:
    - API_KEY
    - BASE_URL
    - VLM_MODEL
---

# Finance OCR Pro

Run this skill only after OCR intent from the user.

This skill is especially helpful for financial reports, annual reports, prospectuses, investor presentations, regulatory filings, research reports, and other documents with complicated structure, charts, graphs, tables, and mixed layout elements.

## Security And Privacy

Before running OCR, make the operating model clear:

- This skill requires three environment variables, all of which must be configured before OCR can run:
  - `API_KEY` (sensitive) -- the API key for authenticating with the VLM endpoint.
  - `BASE_URL` -- the base URL of the OpenAI-compatible VLM endpoint. All page images and OCR prompts are transmitted to this URL.
  - `VLM_MODEL` -- the vision-capable model identifier. Must support image inputs; text-only models will not work.
- OCR sends rendered page images and structured prompts to `BASE_URL`. This is the primary data-transmission path. Users must verify that the endpoint is trusted before processing sensitive documents.
- If the user wants offline or local-only OCR, `BASE_URL` must point to a local VLM service. Do not run this skill against an external endpoint with sensitive documents unless the provider is trusted.
- Never commit a populated `.env` file. Use `.env.example` as a template and keep real credentials local.

## Pre-Run Notice

After the user asks for OCR or extraction, give a short notice that includes:

- whether `BASE_URL` is local or remote
- which `VLM_MODEL` will be used
- which execution mode will be used
- where results will be written
- that page images and prompts will be transmitted to the configured endpoint

Proceed automatically unless the user asks to change those defaults.

## Defaults To Announce

- Running mode: background job by default
- Model: `VLM_MODEL`
- Threads: `1`
- Result path:
  - background: `~/.semantic-ocr/jobs/<job_id>/results/`
  - synchronous: `ocr_output/OCR_<filename>/results/`

## Setup

Use the skill-local virtual environment if present.

- macOS/Linux: `.venv/bin/python`
- Windows: `.venv/Scripts/python.exe`
- Fallback: `python`

Run:

```bash
python scripts/ocr_setup.py --check
```

If setup is incomplete, run:

```bash
python scripts/ocr_setup.py
```

## Preferred Execution

By default, start a background worker:

```bash
python scripts/ocrctl.py --json start /path/to/document.pdf
```

Then inspect progress and outputs:

```bash
python scripts/ocrctl.py --json status <job_id>
python scripts/ocrctl.py --json artifacts <job_id>
python scripts/ocrctl.py --json tail <job_id>
```

Use synchronous mode only when the user explicitly wants inline execution:

```bash
python scripts/ocr_main.py /path/to/document.pdf
```

## Notes

- Inputs: PDF, common office documents, Apple office formats, and images.
- Outputs: merged Markdown, HTML review report, DOCX, and Excel.
- OCR requires `API_KEY`, `BASE_URL`, and `VLM_MODEL` to be configured before running.
- Sensitive document pages are transmitted to the configured endpoint during OCR unless the endpoint is a local service.
- Best suited for financial documents and other visually dense materials with tables, charts, graphs, and complex page structure.
- Office-document conversion may require LibreOffice.
- OCR extraction by the VLM model may be time-consuming; check the status regularly.