#!/usr/bin/env node
/**
 * Thin FFmpeg runner with progress reporting and error capture.
 *
 * Usage:
 *   node ffmpeg_runner.js -i input.mp4 -c:v libx264 -crf 23 output.mp4
 *   FFMPEG_PATH=/usr/bin/ffmpeg node ffmpeg_runner.js -i input.mp4 output.mp3
 *
 * As a module:
 *   const { run, probe } = require('./ffmpeg_runner');
 *   await run(['-i','input.mp4','-c:v','libx264','-crf','23','out.mp4'], { onProgress });
 *   const info = await probe('input.mp4');
 */

'use strict';

const { spawn, execFile } = require('child_process');
const { promisify } = require('util');
const { resolveFfmpeg, resolveFfprobe } = require('./resolve_ffmpeg');

const execFileAsync = promisify(execFile);

/**
 * Run FFmpeg with the given args array.
 * Always prepends `-y` (overwrite) and `-hide_banner`.
 *
 * @param {string[]} args
 * @param {{ onProgress?: (time: string) => void, loglevel?: string }} options
 * @returns {Promise<void>}
 */
function run(args, { onProgress, loglevel = 'error' } = {}) {
  const ffmpegPath = resolveFfmpeg();
  const fullArgs = ['-y', '-hide_banner', '-loglevel', loglevel, ...args];

  return new Promise((resolve, reject) => {
    const proc = spawn(ffmpegPath, fullArgs, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stderr = '';

    proc.stderr.on('data', chunk => {
      const text = chunk.toString();
      stderr += text;
      if (onProgress) {
        const m = text.match(/time=(\S+)/);
        if (m) onProgress(m[1]);
      }
    });

    proc.on('close', code => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`ffmpeg exited with code ${code}\n${stderr.slice(-3000)}`));
      }
    });

    proc.on('error', err => reject(new Error(`Failed to start ffmpeg: ${err.message}`)));
  });
}

/**
 * Run FFmpeg with machine-readable progress on stdout.
 *
 * @param {string[]} args  (do not include -progress; it is injected automatically)
 * @param {{ onProgress?: (kv: Record<string,string>) => void }} options
 * @returns {Promise<void>}
 */
function runWithProgress(args, { onProgress } = {}) {
  const ffmpegPath = resolveFfmpeg();
  const fullArgs = [
    '-y', '-hide_banner', '-loglevel', 'error',
    ...args,
    '-progress', 'pipe:1',
  ];

  return new Promise((resolve, reject) => {
    const proc = spawn(ffmpegPath, fullArgs, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stderr = '';
    let stdoutBuf = '';

    proc.stdout.on('data', chunk => {
      stdoutBuf += chunk.toString();
      const lines = stdoutBuf.split('\n');
      stdoutBuf = lines.pop();
      const kv = {};
      for (const line of lines) {
        const eq = line.indexOf('=');
        if (eq !== -1) kv[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
      }
      if (Object.keys(kv).length && onProgress) onProgress(kv);
    });

    proc.stderr.on('data', chunk => { stderr += chunk; });

    proc.on('close', code => {
      if (code === 0) resolve();
      else reject(new Error(`ffmpeg exited ${code}\n${stderr.slice(-3000)}`));
    });

    proc.on('error', err => reject(new Error(`Failed to start ffmpeg: ${err.message}`)));
  });
}

/**
 * Probe a media file and return parsed JSON metadata.
 *
 * @param {string} filePath
 * @returns {Promise<{format: object, streams: object[]}>}
 */
async function probe(filePath) {
  const ffprobePath = resolveFfprobe();
  const { stdout } = await execFileAsync(ffprobePath, [
    '-v', 'error',
    '-show_format',
    '-show_streams',
    '-of', 'json',
    filePath,
  ]);
  return JSON.parse(stdout);
}

/**
 * Get duration in seconds for a media file.
 *
 * @param {string} filePath
 * @returns {Promise<number>}
 */
async function getDuration(filePath) {
  const info = await probe(filePath);
  const dur = parseFloat(info.format?.duration);
  if (isNaN(dur)) throw new Error(`Could not determine duration for: ${filePath}`);
  return dur;
}

// CLI passthrough: forward all args directly to ffmpeg
if (require.main === module) {
  const args = process.argv.slice(2);
  if (!args.length) {
    console.error('Usage: node ffmpeg_runner.js <ffmpeg args...>');
    process.exit(1);
  }
  run(args, {
    loglevel: 'info',
    onProgress: t => process.stderr.write(`\rTime: ${t}   `),
  })
    .then(() => { process.stderr.write('\n'); })
    .catch(e => { console.error(e.message); process.exit(1); });
}

module.exports = { run, runWithProgress, probe, getDuration };
