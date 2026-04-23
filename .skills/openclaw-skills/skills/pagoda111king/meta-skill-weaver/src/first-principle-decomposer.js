/**
 * First Principle Decomposer - 第一性原理任务分解器
 * 版本：v1.0.0
 * 
 * 灵感来源：第一性原理思维学习（2026-03-30 23:00）
 */

class FirstPrincipleDecomposer {
  constructor(options = {}) {
    this.options = {
      maxWhyDepth: options.maxWhyDepth || 5,
      minAtomicLevel: options.minAtomicLevel || 3,
      ...options
    };
    this.assumptions = [];
    this.firstPrinciples = [];
  }

  decompose(task) {
    console.log('[FirstPrincipleDecomposer] 开始分解任务:', task);
    this.assumptions = this._identifyAssumptions(task);
    const whyAnalysis = this._fiveWhys(task);
    this.firstPrinciples = this._extractFirstPrinciples(whyAnalysis);
    const reconstructedTask = this._reconstructTask(this.firstPrinciples, task);
    const atomicTasks = this._decomposeToAtomic(reconstructedTask);
    
    return {
      originalTask: task,
      assumptions: this.assumptions,
      whyAnalysis,
      firstPrinciples: this.firstPrinciples,
      reconstructedTask,
      atomicTasks,
      metadata: {
        decomposedAt: new Date().toISOString(),
        whyDepth: whyAnalysis.depth,
        atomicTaskCount: atomicTasks.length
      }
    };
  }

  _identifyAssumptions(task) {
    const assumptions = [];
    const patterns = [
      { pattern: /必须 (.*?) 才能/, type: '必要性假设' },
      { pattern: /只有 (.*?) 才能/, type: '唯一性假设' },
      { pattern: /因为 (.*?)(,|。)/, type: '因果假设' },
      { pattern: /一直 (.*?) 所以/, type: '经验假设' },
      { pattern: /应该 (.*?) 因为/, type: '规范性假设' }
    ];
    
    patterns.forEach(({ pattern, type }) => {
      const matches = task.match(pattern);
      if (matches) {
        assumptions.push({ type, content: matches[1], questioned: false });
      }
    });
    
    if (assumptions.length === 0) {
      assumptions.push({ type: '隐含假设', content: '当前任务描述是最优解', questioned: false });
    }
    
    return assumptions;
  }

  _fiveWhys(task) {
    const analysis = [];
    let currentWhy = task;
    let depth = 0;
    
    while (depth < this.options.maxWhyDepth) {
      const why = this._askWhy(currentWhy);
      if (!why || why === currentWhy) break;
      
      analysis.push({
        level: depth + 1,
        question: `为什么${depth > 0 ? '要' : ''}${currentWhy}?`,
        answer: why
      });
      
      currentWhy = why;
      depth++;
    }
    
    return { depth, analysis };
  }

  _askWhy(statement) {
    const verbPattern = /(需要 | 要 | 必须 | 应该)(.*?)(以 | 来 | 为了 | 才能)/;
    const match = statement.match(verbPattern);
    
    if (match) {
      const action = match[2];
      const purposes = {
        '完成任务': '达成目标',
        '解决问题': '消除障碍',
        '实现功能': '满足需求',
        '优化性能': '提升效率',
        '改进质量': '增加价值'
      };
      
      for (const [key, value] of Object.entries(purposes)) {
        if (action.includes(key)) return value;
      }
      
      return `理解${action}的本质目的`;
    }
    
    return null;
  }

  _extractFirstPrinciples(whyAnalysis) {
    const principles = [];
    const lastAnalysis = whyAnalysis.analysis[whyAnalysis.analysis.length - 1];
    
    if (lastAnalysis) {
      principles.push({
        principle: lastAnalysis.answer,
        confidence: 0.8,
        source: '5Why 分析'
      });
    }
    
    principles.push(
      { principle: '任务应该分解到可执行的最小单元', confidence: 0.9, source: '任务管理最佳实践' },
      { principle: '每个子任务应该有明确的输入输出', confidence: 0.9, source: '系统工程' },
      { principle: '依赖关系应该显式声明', confidence: 0.85, source: '工作流管理' }
    );
    
    return principles;
  }

  _reconstructTask(principles, originalTask) {
    return {
      goal: this._extractGoal(originalTask),
      constraints: this._extractConstraints(originalTask),
      successCriteria: this._defineSuccessCriteria(originalTask),
      principles: principles.map(p => p.principle)
    };
  }

  _extractGoal(task) {
    const patterns = [
      /目标 [是:]?(.*?)(。|$)/,
      /为了 (.*?)(。|$)/,
      /实现 (.*?)(。|$)/
    ];
    
    for (const pattern of patterns) {
      const match = task.match(pattern);
      if (match) return match[1].trim();
    }
    
    return task;
  }

  _extractConstraints(task) {
    const constraints = [];
    const patterns = [
      { pattern: /在 (.*?) 内/, type: '时间约束' },
      { pattern: /使用 (.*?) 来/, type: '工具约束' },
      { pattern: /不超过 (.*?)(。|,)/, type: '资源约束' },
      { pattern: /必须 (.*?)(。|,)/, type: '质量约束' }
    ];
    
    patterns.forEach(({ pattern, type }) => {
      const matches = task.match(pattern);
      if (matches) {
        constraints.push({ type, content: matches[1] });
      }
    });
    
    return constraints;
  }

  _defineSuccessCriteria(task) {
    return [
      '任务目标明确且可衡量',
      '所有子任务可独立执行',
      '依赖关系清晰',
      '结果可验证'
    ];
  }

  _decomposeToAtomic(reconstructedTask) {
    const atomicTasks = [];
    const goal = reconstructedTask.goal;
    const actionWords = ['分析', '设计', '实现', '测试', '优化', '评估', '创建', '验证'];
    
    actionWords.forEach((action, index) => {
      atomicTasks.push({
        id: `atomic_${index + 1}`,
        action,
        description: `${action}${goal}`,
        dependencies: index > 0 ? [`atomic_${index}`] : [],
        estimatedEffort: 'medium',
        isAtomic: true
      });
    });
    
    return atomicTasks;
  }

  getSummary() {
    return {
      assumptionsIdentified: this.assumptions.length,
      firstPrinciplesExtracted: this.firstPrinciples.length,
      assumptions: this.assumptions.map(a => a.content),
      principles: this.firstPrinciples.map(p => p.principle)
    };
  }
}

module.exports = { FirstPrincipleDecomposer };
