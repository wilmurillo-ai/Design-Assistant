#!/usr/bin/env node

/**
 * generate-audio.js — Extract text from URL and generate MP3 audio
 *
 * Usage:
 *   node generate-audio.js <url> [output-dir]
 *
 * Output:
 *   Per-paragraph MP3 files + manifest JSON to stdout.
 *   Each paragraph gets its own MP3 file + text, so the agent can send them
 *   individually (e.g., as Telegram audio messages with text captions).
 *
 *   A combined full.mp3 is also generated for single-file use cases.
 *
 * Environment variables:
 *   CASTREADER_API_URL  — TTS API endpoint (default: http://api.castreader.ai:8123)
 *   CASTREADER_VOICE    — TTS voice (default: af_heart)
 *   CASTREADER_SPEED    — Playback speed (default: 1.5)
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const API_URL = process.env.CASTREADER_API_URL || 'http://api.castreader.ai:8123';
const API_KEY = process.env.CASTREADER_API_KEY || '';
const VOICE = process.env.CASTREADER_VOICE || 'af_heart';
const SPEED = parseFloat(process.env.CASTREADER_SPEED || '1.5');
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

/**
 * Call Castreader TTS API (captioned_speech_partly).
 * The API processes text in chunks — loop until unprocessed_text is empty.
 */
async function generateTTSForText(text, language) {
  const audioChunks = [];
  let remaining = text;

  while (remaining && remaining.trim().length > 0) {
    const body = {
      model: 'kokoro',
      input: remaining,
      voice: VOICE,
      response_format: 'mp3',
      return_timestamps: true,
      speed: SPEED,
      stream: false,
      language: language || 'en',
    };

    let data = null;
    let lastError = null;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        const headers = { 'Content-Type': 'application/json', accept: 'application/json' };
        if (API_KEY) headers['Authorization'] = `Bearer ${API_KEY}`;

        const response = await fetch(`${API_URL}/api/captioned_speech_partly`, {
          method: 'POST',
          headers,
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          const errText = await response.text().catch(() => '');
          lastError = new Error(`HTTP ${response.status}: ${errText}`);
          if (response.status >= 502 && response.status <= 504 && attempt < MAX_RETRIES) {
            await sleep(RETRY_DELAY_MS * attempt);
            continue;
          }
          throw lastError;
        }

        data = await response.json();
        break;
      } catch (err) {
        lastError = err;
        if (attempt < MAX_RETRIES && err.message?.includes('fetch')) {
          await sleep(RETRY_DELAY_MS * attempt);
          continue;
        }
        throw err;
      }
    }

    if (!data || (!data.audio && !data.audioUrl)) {
      throw lastError || new Error('No audio data received');
    }

    // Decode base64 audio
    const audioBase64 = data.audio || data.audioUrl?.replace(/^data:audio\/\w+;base64,/, '');
    if (audioBase64) {
      audioChunks.push(Buffer.from(audioBase64, 'base64'));
    }

    remaining = data.unprocessed_text || '';
  }

  return audioChunks;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  const url = process.argv[2];
  const outputDir = process.argv[3] || `/tmp/castreader-${Date.now()}`;

  if (!url) {
    console.error('Usage: node generate-audio.js <url> [output-dir]');
    process.exit(1);
  }

  // Create output directory
  fs.mkdirSync(outputDir, { recursive: true });

  // Step 1: Extract text using extract.js
  process.stderr.write(`Extracting text from ${url}...\n`);
  const extractScript = path.resolve(__dirname, 'extract.js');
  let extractResult;
  try {
    const output = execFileSync('node', [extractScript, url], {
      encoding: 'utf-8',
      timeout: 60000,
    });
    extractResult = JSON.parse(output);
  } catch (err) {
    console.error('Extraction failed:', err.message);
    process.exit(1);
  }

  if (!extractResult.success || !extractResult.paragraphs?.length) {
    console.error('No content extracted from', url);
    process.exit(1);
  }

  const totalParas = extractResult.paragraphs.length;
  process.stderr.write(
    `Extracted ${totalParas} paragraphs (${extractResult.totalCharacters} chars), language: ${extractResult.language}\n`
  );

  // Step 2: Generate TTS per paragraph, save individual MP3 files
  const paragraphs = [];
  const allAudioChunks = [];
  let paraIndex = 0;

  for (let i = 0; i < totalParas; i++) {
    const paraText = extractResult.paragraphs[i];
    if (!paraText || paraText.trim().length === 0) continue;

    paraIndex++;
    const paddedIndex = String(paraIndex).padStart(3, '0');
    const audioFile = path.join(outputDir, `${paddedIndex}.mp3`);

    process.stderr.write(`Generating audio [${paraIndex}/${totalParas}]...\n`);

    try {
      const chunks = await generateTTSForText(paraText, extractResult.language);
      const paraAudio = Buffer.concat(chunks);

      // Write individual paragraph MP3
      fs.writeFileSync(audioFile, paraAudio);

      paragraphs.push({
        index: paraIndex,
        text: paraText.trim(),
        audioFile: path.resolve(audioFile),
        fileSizeBytes: paraAudio.length,
      });

      allAudioChunks.push(...chunks);
    } catch (err) {
      process.stderr.write(`Warning: Failed paragraph ${paraIndex}: ${err.message}\n`);
      // Still include paragraph text even if audio failed
      paragraphs.push({
        index: paraIndex,
        text: paraText.trim(),
        audioFile: null,
        error: err.message,
      });
    }
  }

  if (allAudioChunks.length === 0) {
    console.error('No audio generated');
    process.exit(1);
  }

  // Step 3: Write combined full.mp3
  const fullAudioPath = path.join(outputDir, 'full.mp3');
  const combined = Buffer.concat(allAudioChunks);
  fs.writeFileSync(fullAudioPath, combined);

  // Output manifest JSON to stdout
  const manifest = {
    success: true,
    url,
    title: extractResult.title,
    language: extractResult.language,
    outputDir: path.resolve(outputDir),
    fullAudio: path.resolve(fullAudioPath),
    fullAudioSizeMB: (combined.length / 1024 / 1024).toFixed(2),
    totalParagraphs: paragraphs.length,
    paragraphs,
  };

  console.log(JSON.stringify(manifest, null, 2));
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
