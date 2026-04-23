#!/usr/bin/env node

/**
 * claw-migrate - OpenClaw GitHub 配置迁移工具
 * 从 GitHub 私有仓库拉取配置到本地 OpenClaw 实例
 * 
 * 重构后：简化的命令分发器
 */

const readline = require('readline');

const { executeCommand, checkConfigExists, commandRequiresConfig } = require('./commands');
const { executeMigration } = require('./migration');
const { configExists } = require('./config-loader');
const { printHeader, printError, printInfo } = require('./logger');
const { getOpenClawEnv } = require('./openclaw-env');
const { SetupWizard } = require('./setup');

// 命令行参数解析
function parseArgs(args) {
  const options = {
    repo: null,
    branch: 'main',
    path: '',
    type: 'all',
    dryRun: false,
    noBackup: false,
    verbose: false,
    token: process.env.GITHUB_TOKEN || null,
    command: null,
    action: null,
    edit: false,
    reset: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--repo' || arg === '-r') {
      options.repo = args[++i];
    } else if (arg === '--branch' || arg === '-b') {
      options.branch = args[++i];
    } else if (arg === '--path' || arg === '-p') {
      options.path = args[++i];
    } else if (arg === '--type' || arg === '-t') {
      options.type = args[++i];
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--no-backup') {
      options.noBackup = true;
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    } else if (arg === '--token') {
      options.token = args[++i];
    } else if (arg === '--setup') {
      options.command = 'setup';
    } else if (arg === '--backup') {
      options.command = 'backup';
    } else if (arg === '--restore') {
      options.command = 'restore';
    } else if (arg === '--config') {
      options.command = 'config';
    } else if (arg === '--edit') {
      options.edit = true;
    } else if (arg === '--reset') {
      options.reset = true;
    } else if (arg === '--status') {
      options.command = 'config';
      options.status = true;
    } else if (arg === '--scheduler') {
      options.command = 'scheduler';
    } else if (arg === '--start') {
      options.action = 'start';
    } else if (arg === '--stop') {
      options.action = 'stop';
    } else if (arg === '--logs') {
      options.action = 'logs';
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return options;
}

function printHelp() {
  console.log(`
OpenClaw GitHub 配置迁移工具

用法:
  openclaw skill run claw-migrate [命令] [选项]

命令:
  setup       启动配置向导
  backup      执行备份
  restore     恢复配置
  config      查看配置 (--edit 修改，--reset 重置)
  status      查看状态
  scheduler   定时任务管理 (--start/--stop/--logs)

选项:
  --repo, -r <repo>        GitHub 仓库（格式：owner/repo）
  --branch, -b <branch>    分支名（默认：main）
  --path, -p <path>        仓库内的路径（默认：根目录）
  --type, -t <type>        迁移类型：all, config, memory, learnings, skills（默认：all）
  --dry-run                预览模式，不实际写入文件
  --no-backup              不创建备份
  --verbose, -v            详细输出
  --token <token>          GitHub Token（可选，优先使用 GITHUB_TOKEN 环境变量）
  --edit                   修改配置
  --reset                  重置配置
  --start                  启动定时任务
  --stop                   停止定时任务
  --logs                   查看日志
  --help, -h               显示帮助信息

示例:
  openclaw skill run claw-migrate setup
  openclaw skill run claw-migrate backup
  openclaw skill run claw-migrate restore
  openclaw skill run claw-migrate config --edit
  openclaw skill run claw-migrate scheduler --start
  openclaw skill run claw-migrate --repo <owner>/<repo>
  openclaw skill run claw-migrate --repo <owner>/<repo> --type skills --dry-run
`);
}

// 交互式获取 GitHub Token
async function promptForToken() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    console.log('\n⚠️  未检测到 GITHUB_TOKEN 环境变量');
    console.log('   请输入您的 GitHub Personal Access Token:');
    console.log('   （Token 仅用于本次会话，不会被保存）\n');
    
    rl.question('GitHub Token: ', (token) => {
      rl.close();
      resolve(token.trim());
    });
  });
}

// 检查是否需要显示安装后向导
async function checkPostInstall() {
  return !configExists();
}

// 运行安装后向导
async function runPostInstallWizard() {
  const wizard = new SetupWizard();
  const choice = await wizard.showMainMenu();
  
  if (choice === 1) {
    const { executeSetup } = require('./commands/setup');
    await executeSetup();
  } else if (choice === 2) {
    const { executeSetup } = require('./commands/setup');
    await executeSetup();
  }
  
  wizard.close();
}

// 主函数
async function main() {
  printHeader('OpenClaw GitHub 配置迁移工具');

  const args = process.argv.slice(2);
  const options = parseArgs(args);

  // 初始化 OpenClaw 环境
  const ocEnv = await getOpenClawEnv();
  
  if (options.verbose) {
    ocEnv.printConfig();
  }

  // 检查是否是安装后首次运行
  const isFirstRun = await checkPostInstall();
  
  if (isFirstRun && !options.command) {
    await runPostInstallWizard();
    return;
  }

  // 检查配置
  if (options.command && commandRequiresConfig(options.command)) {
    const hasConfig = await checkConfigExists();
    if (!hasConfig) {
      printError('❌ 错误：未找到配置文件');
      console.log('   请先运行：openclaw skill run claw-migrate setup');
      process.exit(1);
    }
  }

  // 根据命令执行
  if (options.command) {
    await executeCommand(options.command, options);
    return;
  }

  // 默认：执行迁移（pull 模式）
  await executeMigration(options);
}

// 运行
main().catch(err => {
  printError(`❌ 未捕获的错误：${err.message}`);
  process.exit(1);
});
