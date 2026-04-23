#!/usr/bin/env node
/**
 * 批量图片压缩脚本
 * 用法：node batch-compress.js <input-dir> [options]
 */

import { compressImage } from 'rv-image-optimize/node-compress';
import { readdir, stat } from 'fs/promises';
import { join, extname } from 'path';

const IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp'];

async function batchCompress(inputDir, options = {}) {
  const {
    outputDir = inputDir,
    format = 'webp',
    quality = 80,
    maxWidth,
    maxHeight,
    recursive = true
  } = options;

  const files = await readdir(inputDir, { recursive });
  const imageFiles = files.filter(f => 
    IMAGE_EXTS.includes(extname(f).toLowerCase())
  );

  console.log(`找到 ${imageFiles.length} 张图片`);
  
  let success = 0;
  let failed = 0;

  for (const file of imageFiles) {
    const inputPath = join(inputDir, file);
    const outputPath = join(outputDir, file.replace(extname(file), `.${format}`));
    
    try {
      await compressImage({
        input: inputPath,
        output: outputPath,
        quality,
        format,
        maxWidth,
        maxHeight
      });
      console.log(`✓ ${file}`);
      success++;
    } catch (err) {
      console.error(`✗ ${file}: ${err.message}`);
      failed++;
    }
  }

  console.log(`\n完成：${success} 成功，${failed} 失败`);
}

// CLI 入口
if (process.argv[1]?.includes('batch-compress')) {
  const args = process.argv.slice(2);
  const inputDir = args[0];
  
  if (!inputDir) {
    console.log('用法：node batch-compress.js <input-dir> [--quality 80] [--format webp]');
    process.exit(1);
  }

  batchCompress(inputDir, {
    quality: parseInt(args.find(a => a.includes('--quality'))?.split('=')[1] || '80'),
    format: args.find(a => a.includes('--format'))?.split('=')[1] || 'webp'
  });
}

export { batchCompress };
