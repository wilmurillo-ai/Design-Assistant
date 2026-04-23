/**
 * Virtual Path System - 虚拟路径系统
 * 灵感来源：DeerFlow 的虚拟路径映射
 */

const path = require('path');
const fs = require('fs').promises;

class VirtualPathSystem {
  constructor(baseDir) {
    this.baseDir = baseDir;
    this.virtualPaths = new Map();
    this.threadDirs = new Map();
  }

  mount(virtualPath, physicalPath) {
    this.virtualPaths.set(virtualPath, physicalPath);
    console.log(`[VirtualPathSystem] 挂载：${virtualPath} → ${physicalPath}`);
  }

  resolve(virtualPath) {
    for (const [virt, phys] of this.virtualPaths.entries()) {
      if (virtualPath.startsWith(virt)) {
        return path.join(phys, virtualPath.substring(virt.length));
      }
    }
    return path.join(this.baseDir, virtualPath);
  }

  async createThreadDir(threadId) {
    const threadBaseDir = path.join(this.baseDir, 'threads', threadId);
    const workspaceDir = path.join(threadBaseDir, 'workspace');
    const uploadsDir = path.join(threadBaseDir, 'uploads');
    const outputsDir = path.join(threadBaseDir, 'outputs');
    
    await fs.mkdir(workspaceDir, { recursive: true });
    await fs.mkdir(uploadsDir, { recursive: true });
    await fs.mkdir(outputsDir, { recursive: true });
    
    this.threadDirs.set(threadId, { workspaceDir, uploadsDir, outputsDir });
    
    return { workspace: workspaceDir, uploads: uploadsDir, outputs: outputsDir };
  }

  async deleteThreadDir(threadId) {
    const threadInfo = this.threadDirs.get(threadId);
    if (threadInfo) {
      await fs.rm(threadInfo.workspaceDir.split('/workspace')[0], { recursive: true, force: true });
      this.threadDirs.delete(threadId);
    }
  }
}

module.exports = { VirtualPathSystem };
