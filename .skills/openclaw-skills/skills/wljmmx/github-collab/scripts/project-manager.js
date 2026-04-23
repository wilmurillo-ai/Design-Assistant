#!/usr/bin/env node

/**
 * 项目管理器
 * 支持多项目异步排队、关联仓库管理、按项目地址分类
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  dataDir: path.join(__dirname, '..', 'data'),
  queueFile: path.join(__dirname, '..', 'data', 'project-queue.json'),
  projectsFile: path.join(__dirname, '..', 'data', 'projects.json'),
  categoriesFile: path.join(__dirname, '..', 'data', 'categories.json')
};

function initDataDir() {
  if (!fs.existsSync(CONFIG.dataDir)) {
    fs.mkdirSync(CONFIG.dataDir, { recursive: true });
  }
}

function readJSON(file) {
  try {
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf8'));
    }
  } catch (error) {
    console.error(`读取文件失败：${file}`, error.message);
  }
  return null;
}

function writeJSON(file, data) {
  try {
    fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
  } catch (error) {
    console.error(`写入文件失败：${file}`, error.message);
  }
}

function getCurrentUser() {
  try {
    const user = JSON.parse(execSync('gh api user', { encoding: 'utf8' }));
    return user.login;
  } catch (error) {
    return 'wljmmx';
  }
}

function addToQueue(project) {
  const queue = readJSON(CONFIG.queueFile) || [];
  queue.push({
    id: project.id || `project-${Date.now()}`,
    ...project,
    status: 'pending',
    queuedAt: new Date().toISOString()
  });
  writeJSON(CONFIG.queueFile, queue);
  console.log(`✅ 项目已添加到队列，ID: ${project.id}`);
  return queue;
}

function processQueue() {
  const queue = readJSON(CONFIG.queueFile) || [];
  const pending = queue.filter(p => p.status === 'pending');
  
  if (pending.length === 0) {
    console.log('📭 队列为空');
    return;
  }

  console.log(`🚀 开始处理队列，共 ${pending.length} 个项目`);
  
  const batchSize = 3;
  for (let i = 0; i < pending.length; i += batchSize) {
    const batch = pending.slice(i, i + batchSize);
    const promises = batch.map(processProject);
    Promise.all(promises);
  }
}

function processProject(project) {
  console.log(`\n📦 处理项目：${project.repoName}`);
  project.status = 'processing';
  project.startedAt = new Date().toISOString();
  
  const fullRepoName = `${getCurrentUser()}/${project.repoName}`;
  
  try {
    const issues = execSync(`gh issue list --repo ${fullRepoName} --limit 10`, { encoding: 'utf8' });
    const commits = execSync(`gh pr list --repo ${fullRepoName} --limit 5`, { encoding: 'utf8' });
    
    project.status = 'completed';
    project.completedAt = new Date().toISOString();
    project.lastIssueList = issues;
    project.lastPRList = commits;
    console.log(`✅ 项目处理完成：${project.repoName}`);
  } catch (error) {
    project.status = 'failed';
    project.error = error.message;
    console.error(`❌ 项目处理失败：${project.repoName}`, error.message);
  }
  
  const queue = readJSON(CONFIG.queueFile) || [];
  const index = queue.findIndex(p => p.id === project.id);
  if (index !== -1) {
    queue[index] = project;
    writeJSON(CONFIG.queueFile, queue);
  }
}

function linkRepository(repoName, parentRepo, category) {
  const projects = readJSON(CONFIG.projectsFile) || {};
  
  if (!projects[repoName]) {
    console.error(`❌ 项目 ${repoName} 不存在`);
    return;
  }
  
  if (!projects[repoName].linkedRepos) {
    projects[repoName].linkedRepos = [];
  }
  
  projects[repoName].linkedRepos.push({
    repo: parentRepo,
    category: category || 'default',
    linkedAt: new Date().toISOString()
  });
  
  writeJSON(CONFIG.projectsFile, projects);
  console.log(`✅ 仓库 ${repoName} 已关联到 ${parentRepo} (${category || 'default'})`);
}

function listProjects(category) {
  const projects = readJSON(CONFIG.projectsFile) || {};
  
  console.log('📋 项目列表:');
  if (Object.keys(projects).length === 0) {
    console.log('  无项目');
    return;
  }
  
  Object.entries(projects).forEach(([name, project]) => {
    if (category && project.category !== category) return;
    
    console.log(`  - ${name}: ${project.description || '无描述'}`);
    console.log(`    状态：${project.status || '未初始化'}`);
    console.log(`    分类：${project.category || 'default'}`);
    if (project.linkedRepos) {
      console.log(`    关联仓库：${project.linkedRepos.map(r => `${r.repo}(${r.category})`).join(', ')}`);
    }
    if (project.lastUpdate) {
      console.log(`    最后更新：${new Date(project.lastUpdate).toLocaleString()}`);
    }
  });
}

function createCategory(name, description) {
  const categories = readJSON(CONFIG.categoriesFile) || {};
  
  categories[name] = {
    name: name,
    description: description || '',
    createdAt: new Date().toISOString(),
    projects: []
  };
  
  writeJSON(CONFIG.categoriesFile, categories);
  console.log(`✅ 分类已创建：${name}`);
}

function listCategories() {
  const categories = readJSON(CONFIG.categoriesFile) || {};
  
  console.log('📂 项目分类列表:');
  if (Object.keys(categories).length === 0) {
    console.log('  无分类');
    return;
  }
  
  Object.entries(categories).forEach(([name, category]) => {
    console.log(`  - ${name}: ${category.description || '无描述'}`);
    console.log(`    项目数：${category.projects?.length || 0}`);
  });
}

function assignToCategory(repoName, category) {
  const projects = readJSON(CONFIG.projectsFile) || {};
  const categories = readJSON(CONFIG.categoriesFile) || {};
  
  if (!projects[repoName]) {
    console.error(`❌ 项目 ${repoName} 不存在`);
    return;
  }
  
  if (!categories[category]) {
    console.error(`❌ 分类 ${category} 不存在`);
    return;
  }
  
  projects[repoName].category = category;
  writeJSON(CONFIG.projectsFile, projects);
  
  categories[category].projects = categories[category].projects || [];
  if (!categories[category].projects.includes(repoName)) {
    categories[category].projects.push(repoName);
    writeJSON(CONFIG.categoriesFile, categories);
  }
  
  console.log(`✅ 项目 ${repoName} 已分配到分类 ${category}`);
}

function getProjectProgress(repoName) {
  const fullRepoName = `${getCurrentUser()}/${repoName}`;
  
  try {
    const issues = execSync(`gh issue list --repo ${fullRepoName} --limit 20`, { encoding: 'utf8' });
    const commits = execSync(`gh pr list --repo ${fullRepoName} --limit 10`, { encoding: 'utf8' });
    
    return {
      repo: repoName,
      issues: issues,
      prs: commits,
      lastUpdate: new Date().toISOString()
    };
  } catch (error) {
    console.error(`❌ 获取项目 ${repoName} 进度失败`, error.message);
    return null;
  }
}

function dailyReport() {
  console.log('📊 生成每日进度报告...');
  const projects = readJSON(CONFIG.projectsFile) || {};
  const report = [];
  
  Object.entries(projects).forEach(([name, project]) => {
    const progress = getProjectProgress(name);
    if (progress) {
      report.push(progress);
      project.lastUpdate = progress.lastUpdate;
    }
  });
  
  writeJSON(CONFIG.projectsFile, projects);
  
  const summary = `
## 📊 每日进度报告 - ${new Date().toLocaleDateString()}

${report.map(r => `
### ${r.repo}
**Issues:**
${r.issues}
**PRs:**
${r.prs}
`).join('\n')}

---
*报告生成时间：${new Date().toISOString()}*
`;
  
  console.log(summary);
  return summary;
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  initDataDir();
  
  switch (command) {
    case 'queue':
      processQueue();
      break;
      
    case 'add':
      const project = {
        id: args[1],
        repoName: args[1] || 'default-repo',
        description: args[2] || '无描述',
        category: args[3] || 'default'
      };
      addToQueue(project);
      break;
      
    case 'link':
      linkRepository(args[1], args[2], args[3]);
      break;
      
    case 'list':
      listProjects(args[1]);
      break;
      
    case 'category':
      createCategory(args[1], args[2]);
      break;
      
    case 'categories':
      listCategories();
      break;
      
    case 'assign':
      assignToCategory(args[1], args[2]);
      break;
      
    case 'progress':
      const progress = getProjectProgress(args[1]);
      console.log(JSON.stringify(progress, null, 2));
      break;
      
    case 'report':
    default:
      dailyReport();
      break;
  }
}

main();
