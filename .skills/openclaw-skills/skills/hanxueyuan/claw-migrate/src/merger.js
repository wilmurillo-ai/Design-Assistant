#!/usr/bin/env node

/**
 * 合并引擎
 * 精细处理文件覆盖逻辑：有些覆盖，有些不覆盖
 */

const fs = require('fs');
const path = require('path');

class Merger {
  constructor(verbose = false) {
    this.verbose = verbose;
  }

  // 文件恢复策略
  // safe: 保留本地敏感配置
  // full: 完全覆盖
  // custom: 自定义选择
  getRestoreStrategy(filePath, strategy) {
    const fileName = path.basename(filePath);
    const dirName = path.dirname(filePath);

    // 敏感信息文件
    const sensitiveFiles = [
      '.env',
      '.env.local',
      '.env.example'
    ];

    // 机器特定配置
    const machineSpecific = [
      'feishu/pairing',
      'feishu/dedup',
      'telegram/sessions',
      'discord/pairing',
      'sessions'
    ];

    // 检查是否是敏感文件
    const isSensitive = sensitiveFiles.includes(fileName);
    
    // 检查是否是机器特定配置
    const isMachineSpecific = machineSpecific.some(p => filePath.includes(p));

    if (strategy === 'full') {
      // 完整恢复：全部覆盖
      return {
        action: 'overwrite',
        reason: '完整恢复模式'
      };
    }

    if (strategy === 'safe' || strategy === 'custom') {
      // 安全恢复：敏感文件和机器特定配置保留本地
      if (isSensitive) {
        return {
          action: 'skip',
          reason: '敏感文件，保留本地配置'
        };
      }

      if (isMachineSpecific) {
        return {
          action: 'skip',
          reason: '机器特定配置，保留本地'
        };
      }

      // 其他文件：覆盖或合并
      if (fileName === 'MEMORY.md' || filePath.includes('memory/')) {
        return {
          action: 'merge',
          reason: '记忆文件，智能合并'
        };
      }

      if (filePath.includes('.learnings/')) {
        return {
          action: 'append',
          reason: '学习记录，追加去重'
        };
      }

      // 默认：覆盖
      return {
        action: 'overwrite',
        reason: '通用配置，覆盖'
      };
    }

    // 默认跳过
    return {
      action: 'skip',
      reason: '未知策略'
    };
  }

  // 判断是否应该合并
  shouldMerge(category) {
    const mergeCategories = ['MEMORY', 'LEARNINGS'];
    return mergeCategories.includes(category);
  }

  // 执行合并
  merge(category, localContent, remoteContent) {
    if (category === 'MEMORY') {
      return this.mergeMemory(localContent, remoteContent);
    }
    
    if (category === 'LEARNINGS') {
      return this.mergeLearnings(localContent, remoteContent);
    }

    // 默认返回远端内容
    return remoteContent;
  }

  // 合并记忆文件
  mergeMemory(local, remote) {
    // 如果本地内容为空，直接使用远端内容
    if (!local || local.trim() === '') {
      return remote;
    }
    
    // 解析 local 和 remote 的 sections
    const localSections = this.parseMemorySections(local);
    const remoteSections = this.parseMemorySections(remote);

    // 保留本地 sections
    const merged = { ...localSections };

    // 添加远端新增的 sections
    for (const [key, value] of Object.entries(remoteSections)) {
      if (!localSections[key]) {
        merged[key] = value;
      }
    }

    // 重新生成文件内容
    return this.generateMemoryFile(merged);
  }

  // 合并学习记录
  mergeLearnings(local, remote) {
    // 按日期去重，追加远端新增的记录
    const localLines = local.split('\n');
    const remoteLines = remote.split('\n');

    // 提取本地已有日期
    const localDates = new Set();
    for (const line of localLines) {
      const dateMatch = line.match(/^##?\s*(\d{4}-\d{2}-\d{2})/);
      if (dateMatch) {
        localDates.add(dateMatch[1]);
      }
    }

    // 追加远端新增日期
    const newLines = [...localLines];
    let inNewSection = false;
    let currentSection = [];
    let currentSectionDate = null;

    for (const line of remoteLines) {
      const dateMatch = line.match(/^##?\s*(\d{4}-\d{2}-\d{2})/);
      
      if (dateMatch) {
        // 新日期开始，先处理之前的 section
        if (currentSection.length > 0 && currentSectionDate && !localDates.has(currentSectionDate)) {
          // 添加之前的 section
          if (newLines.length > 0 && newLines[newLines.length - 1] !== '') {
            newLines.push('');
          }
          newLines.push(...currentSection);
        }
        
        currentSection = [line];
        currentSectionDate = dateMatch[1];
        inNewSection = true;
      } else if (inNewSection) {
        currentSection.push(line);
      }
    }

    // 处理最后一个 section
    if (currentSection.length > 0 && currentSectionDate && !localDates.has(currentSectionDate)) {
      if (newLines.length > 0 && newLines[newLines.length - 1] !== '') {
        newLines.push('');
      }
      newLines.push(...currentSection);
    }

    return newLines.join('\n');
  }

  // 解析记忆文件的 sections
  parseMemorySections(content) {
    const sections = {};
    const lines = content.split('\n');
    let currentSection = null;
    let currentContent = [];

    for (const line of lines) {
      const sectionMatch = line.match(/^##\s*(.+)/);
      
      if (sectionMatch) {
        // 保存之前的 section
        if (currentSection) {
          sections[currentSection] = currentContent.join('\n');
        }
        
        currentSection = sectionMatch[1].trim();
        currentContent = [];
      } else if (currentSection) {
        currentContent.push(line);
      }
    }

    // 保存最后一个 section
    if (currentSection) {
      sections[currentSection] = currentContent.join('\n');
    }

    return sections;
  }

  // 生成记忆文件
  generateMemoryFile(sections) {
    const lines = ['# MEMORY.md\n'];
    
    for (const [section, content] of Object.entries(sections)) {
      lines.push(`## ${section}`);
      lines.push(content);
      lines.push('');
    }

    return lines.join('\n');
  }

  // 获取策略名称
  getStrategyName(category) {
    const { MERGE_STRATEGIES } = require('./config');
    
    for (const [strategy, categories] of Object.entries(MERGE_STRATEGIES)) {
      if (categories.includes(category)) {
        return strategy;
      }
    }
    
    return 'SKIP'; // 默认策略
  }

  // 生成恢复预览
  generateRestorePreview(files, strategy) {
    const preview = {
      overwrite: [],
      merge: [],
      append: [],
      skip: []
    };

    for (const file of files) {
      const strategyDetail = this.getRestoreStrategy(file.path, strategy);
      
      switch (strategyDetail.action) {
        case 'overwrite':
          preview.overwrite.push(file.path);
          break;
        case 'merge':
          preview.merge.push(file.path);
          break;
        case 'append':
          preview.append.push(file.path);
          break;
        case 'skip':
          preview.skip.push(file.path);
          break;
      }
    }

    return preview;
  }

  // 打印恢复预览
  printRestorePreview(preview) {
    console.log('\n📊 预览恢复内容\n');
    console.log('   将恢复以下文件：\n');

    for (const file of preview.overwrite) {
      console.log(`   ✓ ${file} (覆盖)`);
    }

    for (const file of preview.merge) {
      console.log(`   ✓ ${file} (合并)`);
    }

    for (const file of preview.append) {
      console.log(`   ✓ ${file} (追加)`);
    }

    for (const file of preview.skip) {
      console.log(`   ⏭️ ${file} (保留本地)`);
    }

    console.log(`\n   共 ${preview.overwrite.length + preview.merge.length + preview.append.length + preview.skip.length} 个文件`);
    console.log(`   覆盖：${preview.overwrite.length} 个`);
    console.log(`   合并：${preview.merge.length} 个`);
    console.log(`   追加：${preview.append.length} 个`);
    console.log(`   跳过：${preview.skip.length} 个\n`);
  }
}

module.exports = { Merger };
