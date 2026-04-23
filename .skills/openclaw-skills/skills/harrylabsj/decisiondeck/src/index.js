const fs = require('fs');

class DecisionDeck {
  readInput(input = {}) {
    if (input.file) {
      return fs.readFileSync(input.file, 'utf-8');
    }
    if (typeof input.text === 'string' && input.text.trim()) {
      return input.text;
    }
    throw new Error('No input found. Use --file or --text.');
  }

  normalizeText(text) {
    return String(text || '').replace(/\r\n/g, '\n').trim();
  }

  unique(items) {
    const seen = new Set();
    const output = [];
    for (const item of items) {
      const value = String(item || '').trim();
      if (!value || seen.has(value)) {
        continue;
      }
      seen.add(value);
      output.push(value);
    }
    return output;
  }

  shorten(text, maxLength = 72) {
    const value = String(text || '').trim().replace(/\s+/g, ' ');
    if (value.length <= maxLength) {
      return value;
    }
    return `${value.slice(0, maxLength - 3)}...`;
  }

  cleanLine(line) {
    return String(line || '')
      .replace(/^\s*[-*•\d.)]+\s*/, '')
      .replace(/[。；;]+$/, '')
      .trim();
  }

  collectLines(text) {
    const normalized = this.normalizeText(text);
    const segments = normalized.match(/[^。\n！？?!；;]+[。\n！？?!；;]?/g) || [];
    return this.unique(
      segments
        .map((segment) => this.cleanLine(segment))
        .filter((segment) => segment.length >= 2)
    );
  }

  extractOptionMentions(line) {
    const patterns = [
      /(方案\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(选项\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(方向\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(路径\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(版本\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(策略\s*[A-Z0-9一二三四五六七八九十]+)/gi,
      /(Option\s*[A-Z0-9]+)/gi,
      /(Plan\s*[A-Z0-9]+)/gi
    ];

    const matches = [];
    for (const pattern of patterns) {
      const found = String(line || '').match(pattern) || [];
      for (const item of found) {
        matches.push(item.replace(/\s+/g, ' ').trim());
      }
    }
    return this.unique(matches);
  }

  classifyLine(line) {
    return {
      line,
      options: this.extractOptionMentions(line),
      evidence: /用户|客户|访谈|调研|数据显示|数据|日志|报告|文档|memo|观察|反馈|信号|指标|来源|证据|research|interview|survey|metric|signal|evidence|source/i.test(line),
      conflict: /但是|然而|另一份|另一组|不同|不一致|分歧|冲突|相左|保守|乐观|反对|矛盾|相反|争议|意见不同|另一份.*认为|另一组.*认为|however|while|disagree|conflict/i.test(line),
      agreement: /一致|共识|共同|都提到|都认为|都指出|都支持|consensus|agree/i.test(line),
      unknown: /[?？]|待确认|未知|不清楚|不确定|证据不足|还没验证|需要确认|需要验证|假设|不足|unclear|unknown|assumption|insufficient/i.test(line),
      constraint: /资源|预算|时间|截止|排期|依赖|合规|法务|团队|窗口|风险|成本|复杂|blocked|deadline|budget|constraint|approval|dependency|resource/i.test(line),
      recommendation: /建议|优先|推荐|应该|先做|先走|更适合|更稳|最快|go|no-go|defer|limited go/i.test(line),
      action: /^(先|安排|确认|起草|发送|整理|验证|测试|启动|联系|输出|准备|推进|补齐|访谈|调研|对齐|决策|review|draft|email|plan|decide)/i.test(line)
        || /安排|验证|测试|启动|输出|准备|推进|补齐|访谈|调研|对齐|起草|整理|确认/.test(line)
    };
  }

  distill(text, options = {}) {
    const lines = this.collectLines(text);
    const evidence = [];
    const conflicts = [];
    const agreements = [];
    const unknowns = [];
    const constraints = [];
    const recommendations = [];
    const actions = [];
    const facts = [];

    for (const line of lines) {
      const flags = this.classifyLine(line);

      if (flags.evidence) {
        evidence.push(line);
      }
      if (flags.conflict) {
        conflicts.push(line);
      }
      if (flags.agreement) {
        agreements.push(line);
      }
      if (flags.unknown) {
        unknowns.push(line);
      }
      if (flags.constraint) {
        constraints.push(line);
      }
      if (flags.recommendation) {
        recommendations.push(line);
      }
      if (flags.action) {
        actions.push(line);
      }
      if (
        !flags.evidence &&
        !flags.conflict &&
        !flags.agreement &&
        !flags.unknown &&
        !flags.constraint &&
        !flags.recommendation &&
        !flags.action
      ) {
        facts.push(line);
      }
    }

    const explicitOptions = Array.isArray(options.options) ? options.options : [];
    const inlineOptions = this.unique(lines.flatMap((line) => this.extractOptionMentions(line)));
    const optionList = this.unique([...explicitOptions, ...inlineOptions]);

    const scoredOptions = optionList
      .map((option) => this.scoreOption(option, lines, recommendations, constraints))
      .sort((a, b) => b.score - a.score || a.option.length - b.option.length);

    return {
      lines,
      facts: this.unique(facts),
      evidence: this.unique(evidence),
      conflicts: this.unique(conflicts),
      agreements: this.unique(agreements),
      unknowns: this.unique(unknowns),
      constraints: this.unique(constraints),
      recommendations: this.unique(recommendations),
      actions: this.unique(actions),
      options: scoredOptions
    };
  }

  scoreOption(option, lines, recommendations, constraints) {
    const target = String(option || '').toLowerCase();
    const relatedLines = lines.filter((line) => line.toLowerCase().includes(target));
    let score = relatedLines.length;

    for (const line of relatedLines) {
      if (/优先|推荐|建议|更适合|更稳|最快|先做|本周能验证|低风险|更贴近|省事|直接/i.test(line)) {
        score += 3;
      }
      if (/成本高|实现更重|上线更慢|风险|高风险|复杂|依赖|不确定|阻塞|贵|延后|不建议|不要|难/i.test(line)) {
        score -= 3;
      }
      if (/证据主要来自|只有 1 个|只有一个|证据不足|待确认|未知|不清楚/i.test(line)) {
        score -= 2;
      }
    }

    if (recommendations.some((line) => line.includes(option))) {
      score += 3;
    }
    if (constraints.some((line) => line.includes(option))) {
      score -= 1;
    }

    return {
      option,
      score,
      relatedLines: relatedLines.slice(0, 3)
    };
  }

  inferDecision(distilled, decisionOverride) {
    if (decisionOverride) {
      return String(decisionOverride).trim();
    }

    const questionLine = distilled.lines.find((line) => /是否|要不要|该不该|应该|怎么选|选择|决定|go\s*\/\s*no-go|go\/no-go/i.test(line));
    if (questionLine) {
      return this.shorten(questionLine, 88);
    }

    if (distilled.options.length >= 2) {
      return `在 ${distilled.options.map((item) => item.option).join(' / ')} 之间做出选择`;
    }

    const anchor = distilled.evidence[0] || distilled.facts[0] || distilled.actions[0] || '把现有材料压缩成可决策结论';
    return this.shorten(anchor, 88);
  }

  inferAudience(audienceOverride) {
    return audienceOverride ? String(audienceOverride).trim() : '老板、客户或项目 owner';
  }

  summarizeOption(optionScore) {
    const headline = optionScore.relatedLines[0]
      ? this.shorten(optionScore.relatedLines[0], 58)
      : `${optionScore.option} 是当前材料里的一个可行路径`;
    return `${optionScore.option}: ${headline}`;
  }

  buildEvidenceSupport(distilled) {
    return this.unique([
      ...distilled.evidence.slice(0, 3),
      ...distilled.constraints.slice(0, 1),
      ...distilled.facts.slice(0, 1)
    ]).slice(0, 5);
  }

  buildConflictSummary(distilled) {
    if (distilled.conflicts.length > 0) {
      return distilled.conflicts.slice(0, 3);
    }

    if (distilled.options.length >= 2) {
      const top = distilled.options[0];
      const next = distilled.options[1];
      return [`分歧主要在 ${top.option} 和 ${next.option} 的优先级，以及速度、投入、确定性之间的取舍`];
    }

    return ['当前材料没有明显正面冲突，但仍要留意证据薄弱处'];
  }

  buildMissingInfo(distilled) {
    if (distilled.unknowns.length > 0) {
      return distilled.unknowns.slice(0, 3);
    }

    if (distilled.conflicts.length > 0) {
      return distilled.conflicts.slice(0, 2).map((line) => `需要补证：${line}`);
    }

    if (distilled.options.length >= 2 && distilled.options[0].score - distilled.options[1].score <= 1) {
      return ['前两条路径拉不开明显差距，需要一个更强的用户或业务信号'];
    }

    return ['当前信息已经足够支持一个方向性判断'];
  }

  chooseRecommendation(distilled) {
    if (distilled.options.length > 0) {
      const winner = distilled.options[0];
      return {
        label: winner.option,
        sentence: `建议先走 ${winner.option}`,
        support: winner.relatedLines.length > 0 ? winner.relatedLines : distilled.recommendations.slice(0, 2)
      };
    }

    if (distilled.recommendations.length > 0) {
      return {
        label: this.shorten(distilled.recommendations[0], 36),
        sentence: distilled.recommendations[0],
        support: distilled.recommendations.slice(0, 2)
      };
    }

    if (distilled.actions.length > 0) {
      return {
        label: this.shorten(distilled.actions[0], 36),
        sentence: `建议先推动：${distilled.actions[0]}`,
        support: distilled.actions.slice(0, 2)
      };
    }

    return {
      label: '先做一页简报',
      sentence: '建议先把现有材料压缩成一页决策简报，再进入拍板讨论',
      support: this.buildEvidenceSupport(distilled)
    };
  }

  inferConfidence(distilled) {
    const unknownPenalty = distilled.unknowns.length;
    const conflictPenalty = distilled.conflicts.length > 0 ? 1 : 0;
    const optionMargin = distilled.options.length >= 2 ? distilled.options[0].score - distilled.options[1].score : 2;

    if (optionMargin >= 3 && unknownPenalty === 0 && conflictPenalty === 0) {
      return 'high';
    }
    if (unknownPenalty >= 2 || (distilled.options.length >= 2 && optionMargin <= 1)) {
      return 'directional';
    }
    return 'medium';
  }

  buildNextStep(distilled, recommendation) {
    const actionWithWinner = distilled.actions.find((line) => recommendation.label && line.includes(recommendation.label));
    if (actionWithWinner) {
      return actionWithWinner;
    }
    if (distilled.actions.length > 0) {
      return distilled.actions[0];
    }
    if (distilled.unknowns.length > 0) {
      return `先确认：${this.shorten(distilled.unknowns[0], 60)}`;
    }
    if (recommendation.label) {
      return `把 ${recommendation.label} 压成一页 brief，拿去和关键决策人对齐`;
    }
    return '把当前判断整理成一页简报并发起决策讨论';
  }

  brief(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    const recommendation = this.chooseRecommendation(distilled);

    return {
      mode: 'brief',
      decision: this.inferDecision(distilled, options.decision),
      audience: this.inferAudience(options.audience),
      recommendation: recommendation.sentence,
      confidence: this.inferConfidence(distilled),
      optionsOnTable: distilled.options.length > 0
        ? distilled.options.slice(0, 3).map((item) => this.summarizeOption(item))
        : ['当前材料里没有明确列出多条方案，建议先把可选路径写清楚'],
      evidenceSupports: this.buildEvidenceSupport(distilled),
      conflicts: this.buildConflictSummary(distilled),
      unclear: this.buildMissingInfo(distilled),
      nextStep: this.buildNextStep(distilled, recommendation),
      distilled
    };
  }

  compare(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    if (distilled.options.length < 2) {
      throw new Error('Compare mode requires at least two explicit or inferred options.');
    }

    const winner = distilled.options[0];
    const runnerUp = distilled.options[1];

    return {
      mode: 'compare',
      decision: this.inferDecision(distilled, options.decision),
      ranking: distilled.options.map((item) => ({
        option: item.option,
        score: item.score,
        summary: this.summarizeOption(item)
      })),
      recommendedOption: winner.option,
      whyTopOptionLeads: winner.relatedLines.length > 0 ? winner.relatedLines : this.buildEvidenceSupport(distilled),
      tradeoffs: runnerUp
        ? [`选择 ${winner.option}，意味着先不走 ${runnerUp.option}，换取更高确定性或更快验证速度`]
        : ['当前主要是在一条路径上收敛执行'],
      reverseConditions: this.buildMissingInfo(distilled).slice(0, 2),
      distilled
    };
  }

  conflicts(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    const recommendation = this.chooseRecommendation(distilled);

    return {
      mode: 'conflicts',
      decision: this.inferDecision(distilled, options.decision),
      agreement: distilled.agreements.length > 0 ? distilled.agreements.slice(0, 3) : this.buildEvidenceSupport(distilled).slice(0, 2),
      conflicts: this.buildConflictSummary(distilled),
      whyItMatters: this.buildConflictSummary(distilled).map((item) => `它会影响优先级、投入节奏，或推荐路径：${this.shorten(item, 72)}`),
      whatCanStillBeDecided: recommendation.sentence,
      nextStep: this.buildNextStep(distilled, recommendation),
      distilled
    };
  }

  kickoff(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    const recommendation = this.chooseRecommendation(distilled);
    const projectGoal = distilled.evidence[0] || distilled.facts[0] || this.inferDecision(distilled, options.decision);

    return {
      mode: 'kickoff',
      audience: this.inferAudience(options.audience),
      projectGoal: this.shorten(projectGoal, 88),
      problemOrOpportunity: this.buildEvidenceSupport(distilled).slice(0, 3),
      optionsConsidered: distilled.options.length > 0
        ? distilled.options.slice(0, 3).map((item) => this.summarizeOption(item))
        : ['建议先把项目的 2-3 条候选路径写成可比较选项'],
      recommendedStartingScope: recommendation.sentence,
      constraints: distilled.constraints.length > 0 ? distilled.constraints.slice(0, 3) : ['当前材料没有明确硬约束，需要 kickoff 前补齐'],
      openQuestions: this.buildMissingInfo(distilled),
      nextStep: this.buildNextStep(distilled, recommendation),
      distilled
    };
  }

  gaps(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    const recommendation = this.chooseRecommendation(distilled);
    const missing = this.buildMissingInfo(distilled);

    return {
      mode: 'gaps',
      recommendationStillSupported: recommendation.sentence,
      missingEvidence: missing,
      whyItMatters: missing.map((item) => `如果这点变了，推荐方向或投入节奏也可能要变：${this.shorten(item, 72)}`),
      fastestResolution: missing.map((item) => `用一次短确认、补证或访谈来解决：${this.shorten(item, 64)}`),
      beforeThat: distilled.actions.length > 0 ? distilled.actions.slice(0, 2) : [this.buildNextStep(distilled, recommendation)],
      distilled
    };
  }

  analyze(input, options = {}) {
    const distilled = this.distill(this.readInput(input), options);
    return {
      decision: this.inferDecision(distilled, options.decision),
      audience: this.inferAudience(options.audience),
      confidence: this.inferConfidence(distilled),
      distilled
    };
  }

  renderList(items, emptyText = '无') {
    if (!items || items.length === 0) {
      return `- ${emptyText}`;
    }
    return items.map((item) => `- ${item}`).join('\n');
  }

  render(result) {
    switch (result.mode) {
      case 'brief':
        return [
          'Decision In One Line',
          result.decision,
          '',
          'Recommendation',
          `${result.recommendation} (confidence: ${result.confidence})`,
          '',
          'Options On The Table',
          this.renderList(result.optionsOnTable),
          '',
          'What The Evidence Supports',
          this.renderList(result.evidenceSupports),
          '',
          'Where The Materials Conflict',
          this.renderList(result.conflicts),
          '',
          'What Is Still Unclear',
          this.renderList(result.unclear),
          '',
          'Next Step',
          this.renderList([result.nextStep])
        ].join('\n');
      case 'compare':
        return [
          'Decision',
          result.decision,
          '',
          'Option Ranking',
          this.renderList(result.ranking.map((item) => `${item.option} (score: ${item.score}) - ${item.summary}`)),
          '',
          'Why The Top Option Leads',
          this.renderList(result.whyTopOptionLeads),
          '',
          'Tradeoffs',
          this.renderList(result.tradeoffs),
          '',
          'What Would Reverse The Call',
          this.renderList(result.reverseConditions)
        ].join('\n');
      case 'conflicts':
        return [
          'Decision At Stake',
          result.decision,
          '',
          'Where There Is Agreement',
          this.renderList(result.agreement),
          '',
          'Where The Conflict Is',
          this.renderList(result.conflicts),
          '',
          'Why It Matters',
          this.renderList(result.whyItMatters),
          '',
          'What Can Still Be Decided Now',
          this.renderList([result.whatCanStillBeDecided]),
          '',
          'Next Step',
          this.renderList([result.nextStep])
        ].join('\n');
      case 'kickoff':
        return [
          'Project Goal',
          result.projectGoal,
          '',
          'Problem Or Opportunity',
          this.renderList(result.problemOrOpportunity),
          '',
          'Options Considered',
          this.renderList(result.optionsConsidered),
          '',
          'Recommended Starting Scope',
          this.renderList([result.recommendedStartingScope]),
          '',
          'Constraints',
          this.renderList(result.constraints),
          '',
          'Open Questions',
          this.renderList(result.openQuestions),
          '',
          'Next Step',
          this.renderList([result.nextStep])
        ].join('\n');
      case 'gaps':
        return [
          'Recommendation Still Supported',
          result.recommendationStillSupported,
          '',
          'What Is Missing',
          this.renderList(result.missingEvidence),
          '',
          'Why It Matters',
          this.renderList(result.whyItMatters),
          '',
          'Fastest Way To Resolve It',
          this.renderList(result.fastestResolution),
          '',
          'What To Do Before That',
          this.renderList(result.beforeThat)
        ].join('\n');
      default:
        return JSON.stringify(result, null, 2);
    }
  }
}

module.exports = DecisionDeck;
