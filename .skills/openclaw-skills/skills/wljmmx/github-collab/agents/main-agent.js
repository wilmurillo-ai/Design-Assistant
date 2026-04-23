/**
 * Main Agent - 主智能体
 * 职责：接收需求、使用 gh 工具创建 GitHub 项目、拆分任务、分配给子 Agent
 */

const { execSync } = require('child_process');
const TaskManager = require('./task-manager').TaskManager;
const STPIntegrator = require('./stp-integrator').STPIntegrator;
const QQNotifier = require('./qq-notifier').QQNotifier;
const fs = require('fs');
const path = require('path');

class MainAgent {
    constructor(config = {}) {
        this.taskManager = new TaskManager();
        this.stpIntegrator = new STPIntegrator(this.taskManager);
        this.notifier = config.qqToken ? new QQNotifier(config.qqToken) : null;
        this.config = config;
        this.projectDir = null;
    }

    /**
     * 使用 gh 工具创建 GitHub 项目
     */
    createGithubRepo(projectName, description = '') {
        try {
            console.log(`[Main Agent] 使用 gh 工具创建仓库：${projectName}`);
            
            // 创建本地目录
            const repoDir = path.join(process.cwd(), projectName.toLowerCase().replace(/\s+/g, '-'));
            if (!fs.existsSync(repoDir)) {
                fs.mkdirSync(repoDir, { recursive: true });
            }
            
            this.projectDir = repoDir;
            
            // 使用 gh 命令创建远程仓库（如果 gh 已配置）
            try {
                const ghOutput = execSync(
                    `gh repo create ${projectName} --public --description "${description}" --source=${repoDir} --push`,
                    { encoding: 'utf8', stdio: 'pipe' }
                );
                console.log(`[Main Agent] GitHub 仓库创建成功：${ghOutput.trim()}`);
                return { success: true, output: ghOutput.trim() };
            } catch (ghError) {
                // gh 工具可能未配置，记录错误但不阻断流程
                console.log(`[Main Agent] gh 工具不可用（可能未配置），跳过远程仓库创建`);
                console.log(`[Main Agent] 本地目录已创建：${repoDir}`);
                return { success: false, error: 'gh tool not configured', localDir: repoDir };
            }
        } catch (error) {
            console.error(`[Main Agent] 创建 GitHub 仓库失败：${error.message}`);
            return { success: false, error: error.message };
        }
    }

    /**
     * 接收需求并处理
     * @param {string} requirement - 需求描述
     * @param {string} projectName - 项目名称
     * @param {string} githubUrl - GitHub 项目地址（可选，如果不提供则自动创建）
     */
    async receiveRequirement(requirement, projectName, githubUrl = null) {
        console.log(`[Main Agent] 接收需求：${projectName}`);
        
        // 1. 如果没有提供 GitHub URL，则使用 gh 工具创建
        if (!githubUrl) {
            const ghResult = this.createGithubRepo(projectName, requirement);
            if (ghResult.success) {
                githubUrl = ghResult.output.split('\n')[0]; // 提取仓库 URL
            } else {
                // 使用默认 URL
                githubUrl = `https://github.com/wljmmx/${projectName.toLowerCase().replace(/\s+/g, '-')}`;
            }
        }
        
        // 2. 创建项目记录
        const projectId = await this.taskManager.createProject({
            name: projectName,
            github_url: githubUrl,
            description: requirement
        });
        
        console.log(`[Main Agent] 项目已创建：${projectName} (ID: ${projectId.id})`);
        console.log(`[Main Agent] GitHub URL: ${githubUrl}`);
        
        // 3. 使用 STP 拆分任务
        const tasks = await this.stpIntegrator.decomposeProject(
            projectId.id,
            projectName,
            requirement
        );
        
        console.log(`[Main Agent] 任务拆分完成：${tasks.length} 个任务`);
        
        // 4. 分配任务给不同的 Agent
        await this.assignTasksToAgents(projectId.id, tasks);
        
        // 5. 发送通知
        if (this.notifier) {
            await this.notifier.sendProjectNotification({
                projectName,
                taskCount: tasks.length,
                tasks,
                githubUrl
            });
        }
        
        return {
            projectId: projectId.id,
            projectName,
            githubUrl,
            taskCount: tasks.length,
            tasks
        };
    }

    /**
     * 将任务分配给不同的 Agent
     */
    async assignTasksToAgents(projectId, tasks) {
        const agents = [
            { name: 'dev-agent', type: 'developer', tasks: [] },
            { name: 'test-agent', type: 'tester', tasks: [] },
            { name: 'review-agent', type: 'reviewer', tasks: [] }
        ];
        
        // 根据任务类型分配给不同 Agent
        for (const task of tasks) {
            let targetAgent;
            
            if (task.name.toLowerCase().includes('test') || task.name.toLowerCase().includes('测试')) {
                targetAgent = agents[1]; // test-agent
            } else if (task.name.toLowerCase().includes('review') || task.name.toLowerCase().includes('评审')) {
                targetAgent = agents[2]; // review-agent
            } else {
                targetAgent = agents[0]; // dev-agent（默认）
            }
            
            targetAgent.tasks.push(task);
        }
        
        // 分配任务
        for (const agent of agents) {
            if (agent.tasks.length > 0) {
                console.log(`[Main Agent] 分配 ${agent.tasks.length} 个任务给 ${agent.name}`);
                
                for (const task of agent.tasks) {
                    // 创建任务记录
                    const createdTask = await this.taskManager.createTask({
                        project_id: projectId,
                        name: task.name,
                        description: task.description || '',
                        priority: task.priority || 0,
                        metadata: task.metadata || {}
                    });
                    
                    // 分配给 Agent（添加到 Agent 任务队列）
                    await this.taskManager.assignTaskToAgent(createdTask.id, agent.name);
                    
                    console.log(`  - 任务 ${createdTask.id}: ${task.name} -> ${agent.name}`);
                }
            }
        }
        
        return agents;
    }

    /**
     * 获取项目进度报告
     * @param {number} projectId - 项目 ID
     */
    async getProjectReport(projectId) {
        const report = await this.taskManager.generateProgressReport(projectId);
        console.log(`[Main Agent] 生成项目报告：${projectId}`);
        return report;
    }

    /**
     * 列出所有项目
     */
    async listProjects() {
        const projects = await this.taskManager.getAllProjects();
        console.log(`[Main Agent] 项目列表：${projects.length} 个项目`);
        return projects;
    }

    /**
     * 获取待处理任务概览
     */
    async getPendingTasks() {
        const tasks = await this.taskManager.getTasksByStatus('pending');
        console.log(`[Main Agent] 待处理任务：${tasks.length} 个`);
        return tasks;
    }

    /**
     * 获取 Agent 状态
     */
    async getAgentStatus() {
        const agents = await this.taskManager.getActiveAgents();
        console.log(`[Main Agent] 活跃 Agent: ${agents.length} 个`);
        return agents;
    }
}

// CLI 入口
if (require.main === module) {
    const mainAgent = new MainAgent({
        qqToken: process.env.QQ_TOKEN
    });

    // 示例：接收需求
    (async () => {
        const result = await mainAgent.receiveRequirement(
            '开发一个 Todo 应用，支持增删改查功能，使用 React + Node.js',
            'Todo App',
            null // 不提供 URL，让系统自动创建
        );
        
        console.log('\n=== 需求处理完成 ===');
        console.log(`项目：${result.projectName}`);
        console.log(`GitHub: ${result.githubUrl}`);
        console.log(`任务数：${result.taskCount}`);
        
        // 生成报告
        const report = await mainAgent.getProjectReport(result.projectId);
        console.log('\n=== 项目报告 ===');
        console.log(report);
    })();
}

module.exports = { MainAgent };