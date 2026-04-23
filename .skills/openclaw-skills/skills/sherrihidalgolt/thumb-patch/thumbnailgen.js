#!/usr/bin/env node
import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

// --- CLI args ---
const args = process.argv.slice(2);
let topic     = null;
let size      = "landscape";
let style     = null;
let tokenFlag = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--size"  && args[i + 1]) { size      = args[++i]; continue; }
  if (args[i] === "--style" && args[i + 1]) { style     = args[++i]; continue; }
  if (args[i] === "--token" && args[i + 1]) { tokenFlag = args[++i]; continue; }
  if (!args[i].startsWith("--") && topic === null) topic = args[i];
}

// --- Style presets (niche-specific visual guidance) ---
const STYLE_PRESETS = {
  gaming:   "intense gaming aesthetic, neon accent lights, dramatic motion energy, dark moody background, glowing screen reflections, controller or character detail",
  tutorial: "clean educational composition, bright even studio lighting, friendly approachable mood, organized step-indicator feel, professional presenter",
  vlog:     "lifestyle travel photography, warm golden-hour light, natural candid atmosphere, vibrant outdoor or travel location, joyful authentic expression",
  food:     "mouth-watering food photography, extreme macro texture and steam detail, warm restaurant ambiance, rich saturated appetizing colors, shallow depth of field",
  tech:     "sleek technology product shot, cool blue-white palette, minimalist dark background, futuristic circuit or device detail, premium hardware aesthetic",
  fitness:  "high-energy athletic composition, strong muscular definition, gym or outdoor power setting, dynamic action pose, bold motivational intensity",
  music:    "dramatic concert atmosphere, vivid stage lighting beams, energetic performer expression, rich color gel lighting, emotional live-show feel",
  horror:   "dark cinematic thriller, deep dramatic shadows, single sharp rim light, unsettling composition, high-contrast chiaroscuro, eerie atmospheric tension",
};

// --- Base quality (applies to every thumbnail) ---
const BASE =
  "professional YouTube thumbnail, 16:9 landscape format, " +
  "ultra-high contrast vivid saturated colors, dramatic cinematic three-point lighting, " +
  "photorealistic ultra-detailed render, bold graphic composition, " +
  "strong visual hierarchy with single clear focal subject, " +
  "rim lighting separating subject from background, " +
  "clean left-third area reserved for text overlay, " +
  "highly polished maximum-CTR social media aesthetic";

// --- Prompt builder ---
function buildPrompt(userTopic, styleKey) {
  const hint = STYLE_PRESETS[styleKey] || "";
  if (!userTopic) {
    return hint
      ? `${BASE}, ${hint}`
      : `${BASE}, expressive presenter with bold reaction, vibrant dynamic background with depth`;
  }
  return [
    `YouTube thumbnail for: "${userTopic}"`,
    BASE,
    hint || "compelling subject expression and body language that matches the topic mood",
    "composition optimized for maximum click-through rate",
  ].join(" | ");
}

const prompt = buildPrompt(topic, style);

// --- Token resolution ---
function readEnvFile(filePath) {
  try {
    const content = readFileSync(filePath, "utf8");
    const match = content.match(/NETA_TOKEN=(.+)/);
    return match ? match[1].trim() : null;
  } catch {
    return null;
  }
}

const TOKEN =
  tokenFlag ||
  process.env.NETA_TOKEN ||
  readEnvFile(join(homedir(), ".openclaw/workspace/.env")) ||
  readEnvFile(join(homedir(), "developer/clawhouse/.env"));

if (!TOKEN) {
  console.error("Error: NETA_TOKEN not found. Provide via --token, NETA_TOKEN env var, ~/.openclaw/workspace/.env, or ~/developer/clawhouse/.env");
  process.exit(1);
}

// --- Size map ---
const SIZES = {
  square:    { width: 1024, height: 1024 },
  portrait:  { width: 832,  height: 1216 },
  landscape: { width: 1216, height: 832  },
  tall:      { width: 704,  height: 1408 },
};

const { width, height } = SIZES[size] || SIZES.landscape;

// --- Headers ---
const HEADERS = {
  "x-token": TOKEN,
  "x-platform": "nieta-app/web",
  "content-type": "application/json",
};

// --- Make image ---
async function makeImage() {
  const body = {
    storyId: "DO_NOT_USE",
    jobType: "universal",
    rawPrompt: [{ type: "freetext", value: prompt, weight: 1 }],
    width,
    height,
    meta: { entrance: "PICTURE,VERSE" },
  };

  const res = await fetch("https://api.talesofai.cn/v3/make_image", {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`make_image failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  let task_uuid;
  if (typeof data === "string") {
    task_uuid = data;
  } else {
    task_uuid = data.task_uuid;
  }

  if (!task_uuid) {
    throw new Error(`No task_uuid in response: ${JSON.stringify(data)}`);
  }

  return task_uuid;
}

// --- Poll task ---
async function pollTask(task_uuid) {
  const url = `https://api.talesofai.cn/v1/artifact/task/${task_uuid}`;
  const MAX_ATTEMPTS = 90;
  const DELAY_MS = 2000;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const res = await fetch(url, { headers: HEADERS });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`poll failed (${res.status}): ${text}`);
    }

    const data = await res.json();
    const status = data.task_status;

    if (status === "PENDING" || status === "MODERATION") {
      await new Promise((r) => setTimeout(r, DELAY_MS));
      continue;
    }

    // Done
    const imageUrl =
      data?.artifacts?.[0]?.url || data?.result_image_url;

    if (!imageUrl) {
      throw new Error(`Task done but no image URL found: ${JSON.stringify(data)}`);
    }

    console.log(imageUrl);
    return;
  }

  throw new Error(`Timed out after ${MAX_ATTEMPTS} attempts`);
}

// --- Main ---
(async () => {
  try {
    const task_uuid = await makeImage();
    await pollTask(task_uuid);
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  }
})();
