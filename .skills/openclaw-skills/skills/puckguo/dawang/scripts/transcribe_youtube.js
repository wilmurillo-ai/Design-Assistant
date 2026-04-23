#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { URL } = require('url');

// Configuration
const VIDEO_URL = process.argv[2] || 'https://www.youtube.com/watch?v=_uXnyhrqmsU';
const OUTPUT_FILE = process.argv[3] || 'transcript.txt';
const AUDIO_FILE = 'temp_audio.mp3';

// Check if we have OpenAI API key
const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) {
  console.error('Error: OPENAI_API_KEY environment variable is not set');
  console.error('Please set it with: export OPENAI_API_KEY=your_key_here');
  process.exit(1);
}

async function downloadAndTranscribe(videoUrl) {
  console.log('📥 Downloading audio from YouTube...');
  
  try {
    // Download audio only using yt-dlp
    execSync(`yt-dlp -x --audio-format mp3 -o "${AUDIO_FILE}" "${videoUrl}"`, {
      stdio: 'inherit'
    });
    
    console.log('🎤 Transcribing with OpenAI Whisper API...');
    
    // Read the audio file
    const audioData = fs.readFileSync(AUDIO_FILE);
    
    // Create form-data manually for multipart/form-data
    const boundary = '----FormBoundary' + Math.random().toString(36).substring(2);
    
    // Build multipart body
    const fileName = AUDIO_FILE;
    const fileSize = audioData.length;
    
    // Read whole file into buffer for multipart
    const parts = [];
    
    // Add file field
    parts.push(Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="file"; filename="${fileName}"\r\n` +
      `Content-Type: audio/mpeg\r\n\r\n`
    ));
    parts.push(audioData);
    parts.push(Buffer.from('\r\n'));
    
    // Add model field
    parts.push(Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="model"\r\n\r\n` +
      `whisper-1\r\n`
    ));
    
    // Add response_format field
    parts.push(Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="response_format"\r\n\r\n` +
      `verbose_json\r\n`
    ));
    
    // Add timestamp_granularities field
    parts.push(Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="timestamp_granularities[]"\r\n\r\n` +
      `word\r\n`
    ));
    
    parts.push(Buffer.from(`--${boundary}--\r\n`));
    
    const body = Buffer.concat(parts);
    
    // Make request to OpenAI API
    const apiUrl = new URL('https://api.openai.com/v1/audio/transcriptions');
    
    const options = {
      hostname: apiUrl.hostname,
      port: 443,
      path: apiUrl.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length
      }
    };
    
    const result = await new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${data}`));
          }
        });
      });
      req.on('error', reject);
      req.write(body);
      req.end();
    });
    
    console.log('✅ Transcription complete!');
    console.log('\n--- Full Transcript ---\n');
    console.log(result.text);
    
    // Save to file
    fs.writeFileSync(OUTPUT_FILE, result.text);
    console.log(`\n📁 Saved to ${OUTPUT_FILE}`);
    
    // If we have word timestamps, create captions
    if (result.words && result.words.length > 0) {
      console.log('\n📝 Creating caption file...');
      
      const captionFile = OUTPUT_FILE.replace('.txt', '.vtt');
      // Simple VTT format
      let vtt = 'WEBVTT\n\n';
      result.words.forEach((w, i) => {
        const start = formatVTTTime(w.start * 1000);
        const end = formatVTTTime(w.end * 1000);
        vtt += `${i + 1}\n${start} --> ${end}\n${w.word}\n\n`;
      });
      
      fs.writeFileSync(captionFile, vtt);
      console.log(`📁 Captions saved to ${captionFile}`);
    }
    
    // Also create a summary with timing info
    if (result.segments) {
      console.log('\n📊 Segments with timing:');
      result.segments.forEach((seg, i) => {
        const startSec = Math.floor(seg.start);
        const startMin = Math.floor(startSec / 60);
        const startSecRem = startSec % 60;
        console.log(`[${startMin}:${startSecRem.toString().padStart(2, '0')}] ${seg.text.substring(0, 80)}...`);
      });
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    if (error.stack) console.error(error.stack);
  } finally {
    // Cleanup
    if (fs.existsSync(AUDIO_FILE)) {
      fs.unlinkSync(AUDIO_FILE);
      console.log('\n🧹 Cleaned up temporary files');
    }
  }
}

function formatVTTTime(ms) {
  const hours = Math.floor(ms / 3600000);
  const minutes = Math.floor((ms % 3600000) / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const milliseconds = Math.floor(ms % 1000);
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
}

downloadAndTranscribe(VIDEO_URL);
