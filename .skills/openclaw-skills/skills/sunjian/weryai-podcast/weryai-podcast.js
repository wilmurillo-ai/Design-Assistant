#!/usr/bin/env node

const https = require('https');

const args = process.argv.slice(2);
if (args[0] === 'models') {
  console.log("Check supported models here: https://www.weryai.com/api/discovery");
  process.exit(0);
}

const key = process.env.WERYAI_API_KEY || '';
if (!key) {
  console.error("Error: WERYAI_API_KEY is not set.");
  process.exit(1);
}

let md = "WERYAI_PODCAST_1_0";
let pa = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--model' && i + 1 < args.length) {
    md = args[i + 1];
    i++;
  } else {
    pa.push(args[i]);
  }
}
const query = pa.join(' ');

if (!query) {
  console.error("Usage: node weryai-podcast.js [--model <model>] <topic>");
  process.exit(1);
}

function apiCall(url, options, body = null) {
  return new Promise((resolve, reject) => {
    const r = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { resolve(data); }
      });
    });
    r.on('error', reject);
    if (body) r.write(typeof body === 'string' ? body : JSON.stringify(body));
    r.end();
  });
}

async function run() {
  console.log("Submitting podcast text task for topic: " + query);
  
  const submitRes = await apiCall('https://api.weryai.com/growthai/v1/generation/podcast/generate/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key }
  }, {
    model: md,
    query: query,
    speakers: ["travel-girl-english", "leo-9328b6d2"],
    language: "en",
    mode: "quick"
  });

  const taskId = submitRes.data ? submitRes.data.task_id : submitRes.task_id;
  if (!taskId) {
    console.error("Task submission failed");
    process.exit(1);
  }

  console.log("Task submitted successfully. Task ID: " + taskId);
  console.log("Phase 1: Generating script...");

  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    const statusRes = await apiCall('https://api.weryai.com/growthai/v1/generation/' + taskId + '/status', {
      method: 'GET',
      headers: { 'x-api-key': key }
    });

    const cStatus = statusRes.data ? statusRes.data.content_status : statusRes.content_status;
    if (cStatus === 'text-success') {
      console.log("Script generation successful! Moving to Phase 2: Generating audio...");
      break;
    } else if (cStatus === 'text-fail') {
      console.error("Text generation failed");
      process.exit(1);
    } else {
      console.log("...");
    }
  }

  const audioSubmitRes = await apiCall('https://api.weryai.com/growthai/v1/generation/podcast/generate/' + taskId + '/audio', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key }
  }, {});
  
  if (!audioSubmitRes.success && !audioSubmitRes.data) {
    console.error("Audio trigger failed");
    process.exit(1);
  }

  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    const statusRes = await apiCall('https://api.weryai.com/growthai/v1/generation/' + taskId + '/status', {
      method: 'GET',
      headers: { 'x-api-key': key }
    });

    const cStatus = statusRes.data ? statusRes.data.content_status : statusRes.content_status;
    if (cStatus === 'audio-success') {
      console.log("Audio generation successful!");
      const data = statusRes.data || statusRes;
      const audioUrl = data.audio_url || data.audios?.[0] || data.podcast_audio_url || (data.videos && data.videos[0]);
      if (audioUrl) {
        console.log("Audio URL: " + audioUrl);
      }
      break;
    } else if (cStatus === 'audio-fail') {
      console.error("Audio generation failed");
      process.exit(1);
    } else {
      console.log("...");
    }
  }
}

run();
