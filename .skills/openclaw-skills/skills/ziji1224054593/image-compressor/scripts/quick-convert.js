#!/usr/bin/env node
/**
 * 快速格式转换脚本
 * 用法：node quick-convert.js <input> --format <webp|avif|jpeg|png>
 */

import { compressImage } from 'rv-image-optimize/node-compress';
import { basename, extname } from 'path';

async function quickConvert(input, format) {
  const name = basename(input, extname(input));
  const output = `${name}.${format}`;
  
  console.log(`转换：${input} → ${output}`);
  
  await compressImage({
    input,
    output,
    format,
    quality: 85
  });
  
  console.log('✓ 完成');
}

// CLI 入口
if (process.argv[1]?.includes('quick-convert')) {
  const args = process.argv.slice(2);
  const input = args[0];
  const format = args.find(a => a.includes('--format'))?.split('=')[1];
  
  if (!input || !format) {
    console.log('用法：node quick-convert.js <input> --format <webp|avif|jpeg|png>');
    process.exit(1);
  }

  quickConvert(input, format);
}

export { quickConvert };
