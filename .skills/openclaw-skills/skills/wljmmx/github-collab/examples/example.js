/**
 * GitHub Collaboration Skill - 使用示例
 */

const skill = require('./index');

(async () => {
    console.log('=== GitHub Collaboration Skill 示例 ===\n');
    
    // 1. 创建项目
    console.log('1. 创建项目...');
    const project = await skill.createProject(
        '开发一个 Todo 应用，支持增删改查功能',
        'Todo App',
        'https://github.com/wljmmx/todo-app'
    );
    
    console.log(`✅ 项目已创建：${project.projectName}`);
    console.log(`   任务数：${project.taskCount}`);
    console.log(`   项目 ID: ${project.projectId}\n`);
    
    // 2. 列出所有项目
    console.log('2. 列出所有项目...');
    const projects = await skill.listProjects();
    console.log(`✅ 共有 ${projects.length} 个项目\n`);
    
    // 3. 生成项目报告
    console.log('3. 生成项目报告...');
    const report = await skill.getProjectReport(project.projectId);
    console.log(report);
    
})();
