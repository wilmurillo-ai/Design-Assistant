#!/usr/bin/env node

/**
 * 向导工具模块
 * 提取备份/恢复向导的公共步骤
 */

const readline = require('readline');

/**
 * 创建 readline 接口
 * @returns {Object} readline 接口
 */
function createReadlineInterface() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

/**
 * 提问问题并获取答案
 * @param {Object} rl - readline 接口
 * @param {string} question - 问题文本
 * @returns {Promise<string>} 用户输入的答案
 */
function askQuestion(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, resolve);
  });
}

/**
 * 显示菜单
 * @param {Object} rl - readline 接口
 * @param {string} title - 菜单标题
 * @param {Array<{key: string, label: string, description: string}>} options - 菜单选项
 * @returns {Promise<string>} 用户选择的选项
 */
async function showMenu(rl, title, options) {
  console.log('\n' + '━'.repeat(50));
  console.log(title);
  console.log('━'.repeat(50) + '\n');

  options.forEach((option, index) => {
    const key = index + 1;
    console.log(`   ${key}. ${option.label}`);
    if (option.description) {
      console.log(`      ${option.description}`);
    }
    console.log();
  });

  const answer = await askQuestion(rl, '   选择：');
  return answer.trim();
}

/**
 * 确认操作
 * @param {Object} rl - readline 接口
 * @param {string} message - 确认消息
 * @returns {Promise<boolean>} 是否确认
 */
async function confirmAction(rl, message) {
  const answer = await askQuestion(rl, `   ${message} (y/n): `);
  return answer.trim().toLowerCase() === 'y';
}

/**
 * 带验证的提问
 * @param {Object} rl - readline 接口
 * @param {string} question - 问题文本
 * @param {Function} validator - 验证函数
 * @param {string} errorMsg - 错误消息
 * @param {string} defaultValue - 默认值
 * @returns {Promise<string>} 验证后的答案
 */
async function askWithValidation(rl, question, validator, errorMsg = null, defaultValue = null) {
  while (true) {
    const answer = await askQuestion(rl, question);
    const value = answer.trim() || defaultValue;
    
    if (validator(value)) {
      return value;
    }
    
    if (errorMsg) {
      console.log(`\n   ⚠️  ${errorMsg}\n`);
    }
  }
}

/**
 * 向导类 - 提供通用的向导功能
 */
class Wizard {
  constructor() {
    this.rl = createReadlineInterface();
    this.step = 0;
    this.totalSteps = 0;
    this.results = {};
  }

  /**
   * 显示步骤标题
   * @param {string} title - 步骤标题
   */
  showStepTitle(title) {
    console.log(`\n📝 ${title} - 第 ${this.step} 步 / 第 ${this.totalSteps} 步\n`);
  }

  /**
   * 提问并验证
   * @param {string} question - 问题
   * @param {Function} validator - 验证函数
   * @param {string} errorMsg - 错误消息
   * @param {string} defaultValue - 默认值
   * @returns {Promise<string>} 答案
   */
  async ask(question, validator, errorMsg = null, defaultValue = null) {
    return await askWithValidation(this.rl, question, validator, errorMsg, defaultValue);
  }

  /**
   * 显示选择菜单
   * @param {string} title - 菜单标题
   * @param {Array} options - 选项列表
   * @returns {Promise<string>} 选择的选项
   */
  async menu(title, options) {
    return await showMenu(this.rl, title, options);
  }

  /**
   * 确认操作
   * @param {string} message - 确认消息
   * @returns {Promise<boolean>} 是否确认
   */
  async confirm(message) {
    return await confirmAction(this.rl, message);
  }

  /**
   * 关闭向导
   */
  close() {
    this.rl.close();
  }
}

/**
 * 运行通用向导
 * @param {Object} options - 向导配置
 * @param {string} options.title - 向导标题
 * @param {Array} options.steps - 步骤列表
 * @param {Function} options.onComplete - 完成回调
 * @returns {Promise<Object>} 向导结果
 */
async function runWizard(options) {
  const { title, steps, onComplete } = options;
  const wizard = new Wizard();
  wizard.totalSteps = steps.length;

  try {
    console.log('\n' + '━'.repeat(50));
    console.log(`  ${title}`);
    console.log('━'.repeat(50) + '\n');

    for (let i = 0; i < steps.length; i++) {
      wizard.step = i + 1;
      const step = steps[i];
      
      wizard.showStepTitle(step.title);
      
      if (step.description) {
        console.log(step.description + '\n');
      }
      
      const result = await step.handler(wizard, wizard.results);
      wizard.results[step.key] = result;
    }

    // 确认
    if (onComplete) {
      const finalResult = await onComplete(wizard, wizard.results);
      return finalResult;
    }

    return wizard.results;
  } finally {
    wizard.close();
  }
}

module.exports = {
  askQuestion,
  showMenu,
  confirmAction,
  askWithValidation,
  Wizard,
  runWizard,
  createReadlineInterface
};
