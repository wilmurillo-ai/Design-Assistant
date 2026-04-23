/**
 * 九章法律智能操作系统 (9Law OS)
 * 
 * 基于 OpenClaw 架构的法律AI平台
 * 整合36位法律专家 + 三大核心平台
 */

import { OpenClawSkill, OpenClawContext } from '@openclaw/core';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

// 36位专家列表
const EXPERTS_36 = [
  'zhang-corporate-law',
  'zhang-labor-law',
  'zhang-marriage-law',
  'zhang-ip-law',
  'zhang-criminal-law',
  'zhang-property-law',
  'zhang-contract-law',
  'zhang-debt-law',
  'zhang-tax-law',
  'zhang-foreign-investment',
  'zhang-administrative-law',
  'zhang-compliance-audit',
  'zhang-antitrust-law',
  'zhang-data-compliance',
  'zhang-energy-law',
  'zhang-environment-law',
  'zhang-healthcare-law',
  'zhang-gaming-law',
  'zhang-entertainment-law',
  'zhang-education-law',
  'zhang-realestate-dev-law',
  'zhang-construction-law',
  'zhang-insurance-law',
  'zhang-aviation-law',
  'zhang-food-safety-law',
  'zhang-sports-law',
  'zhang-us-law',
  'zhang-eu-law',
  'zhang-seasia-law',
  'zhang-japan-law',
  'zhang-africa-law',
  'zhang-arab-law',
  'zhang-latin-america-law',
  'zhang-russia-law',
  'zhang-ai-law',
  'zhang-international-arbitration'
];

// 路由配置类型
interface RouterConfig {
  routing: Record<string, {
    keywords: string[];
    patterns: string[];
    priority: number;
  }>;
  default: { expert: string; message: string };
}

export class NineLawOS implements OpenClawSkill {
  name = 'zhang-9law-os';
  version = '1.0.0';
  
  private routerConfig: RouterConfig | null = null;
  private context: OpenClawContext | null = null;

  constructor() {
    this.loadRouterConfig();
  }

  private loadRouterConfig(): void {
    try {
      const configPath = path.join(__dirname, '../36-experts-router.yaml');
      if (fs.existsSync(configPath)) {
        const file = fs.readFileSync(configPath, 'utf8');
        this.routerConfig = yaml.load(file) as RouterConfig;
      }
    } catch (error) {
      console.warn('⚠️ 路由配置加载失败，使用默认配置');
    }
  }

  // OpenClaw 生命周期钩子
  async onLoad(context: OpenClawContext): Promise<void> {
    this.context = context;
    console.log('🦞 九章法律智能操作系统启动中...');
    console.log(`✅ 36位法律专家技能已加载`);
    console.log(`✅ 智能路由引擎已就绪`);
    console.log('🚀 系统启动完成！');
  }

  async onUnload(): Promise<void> {
    console.log('🦞 系统关闭中...');
    console.log('👋 已安全关闭');
  }

  // ============ 核心API ============

  /**
   * 智能法律咨询 - 自动路由到最适合的专家
   */
  async consult(input: {
    question: string;
    context?: Record<string, any>;
  }): Promise<{
    expert: string;
    expertName: string;
    confidence: number;
    response: string;
  }> {
    const { expert, confidence } = this.routeExpert(input.question);
    
    // 调用匹配的专家技能
    const expertResult = await this.context?.skills.invoke(expert, {
      question: input.question,
      context: input.context
    });

    return {
      expert,
      expertName: this.getExpertName(expert),
      confidence,
      response: expertResult?.response || '专家正在分析中...'
    };
  }

  /**
   * 智能路由 - 根据问题匹配最佳专家
   */
  private routeExpert(question: string): { expert: string; confidence: number } {
    if (!this.routerConfig) {
      return { expert: 'zhang-corporate-law', confidence: 0.5 };
    }

    let bestExpert = this.routerConfig.default.expert;
    let bestScore = 0;

    // 关键词匹配
    for (const [expertId, config] of Object.entries(this.routerConfig.routing)) {
      let score = 0;
      
      // 关键词匹配
      for (const keyword of config.keywords) {
        if (question.includes(keyword)) {
          score += config.priority;
        }
      }
      
      // 正则模式匹配
      for (const pattern of config.patterns) {
        const regex = new RegExp(pattern, 'i');
        if (regex.test(question)) {
          score += config.priority * 1.5;
        }
      }

      if (score > bestScore) {
        bestScore = score;
        bestExpert = expertId;
      }
    }

    // 计算置信度 (0-1)
    const confidence = Math.min(bestScore / 100, 1);
    
    return { expert: bestExpert, confidence };
  }

  /**
   * 获取专家名称
   */
  private getExpertName(expertId: string): string {
    const nameMap: Record<string, string> = {
      'zhang-corporate-law': '公司法专家',
      'zhang-labor-law': '劳动法专家',
      'zhang-marriage-law': '婚姻家事专家',
      'zhang-ip-law': '知识产权专家',
      'zhang-criminal-law': '刑事辩护专家',
      'zhang-property-law': '房产纠纷专家',
      'zhang-contract-law': '合同纠纷专家',
      'zhang-debt-law': '债权债务专家',
      'zhang-tax-law': '税法专家',
      'zhang-foreign-investment': '外商投资专家',
      'zhang-administrative-law': '行政法专家',
      'zhang-compliance-audit': '合规审计专家',
      'zhang-antitrust-law': '反垄断专家',
      'zhang-data-compliance': '数据合规专家',
      'zhang-energy-law': '能源法专家',
      'zhang-environment-law': '环保法专家',
      'zhang-healthcare-law': '医疗健康专家',
      'zhang-gaming-law': '游戏法专家',
      'zhang-entertainment-law': '娱乐传媒专家',
      'zhang-education-law': '教育法专家',
      'zhang-realestate-dev-law': '房地产开发专家',
      'zhang-construction-law': '建设工程专家',
      'zhang-insurance-law': '保险法专家',
      'zhang-aviation-law': '航空法专家',
      'zhang-food-safety-law': '食品安全专家',
      'zhang-sports-law': '体育法专家',
      'zhang-us-law': '美国法律专家',
      'zhang-eu-law': '欧盟法律专家',
      'zhang-seasia-law': '东南亚法律专家',
      'zhang-japan-law': '日本法律专家',
      'zhang-africa-law': '非洲法律专家',
      'zhang-arab-law': '阿拉伯法律专家',
      'zhang-latin-america-law': '拉美法律专家',
      'zhang-russia-law': '俄罗斯法律专家',
      'zhang-ai-law': 'AI法律专家',
      'zhang-international-arbitration': '国际仲裁专家'
    };
    
    return nameMap[expertId] || expertId;
  }

  /**
   * 获取所有专家列表
   */
  async getExperts(): Promise<Array<{
    id: string;
    name: string;
    category: string;
  }>> {
    return EXPERTS_36.map(id => ({
      id,
      name: this.getExpertName(id),
      category: this.getExpertCategory(id)
    }));
  }

  /**
   * 获取专家分类
   */
  private getExpertCategory(expertId: string): string {
    const categoryMap: Record<string, string> = {
      'zhang-corporate-law': '民商事',
      'zhang-labor-law': '民商事',
      'zhang-marriage-law': '民商事',
      'zhang-ip-law': '民商事',
      'zhang-property-law': '民商事',
      'zhang-contract-law': '民商事',
      'zhang-debt-law': '民商事',
      'zhang-tax-law': '民商事',
      'zhang-criminal-law': '刑事',
      'zhang-administrative-law': '行政',
      'zhang-compliance-audit': '行政',
      'zhang-antitrust-law': '行政'
    };
    return categoryMap[expertId] || '专业';
  }

  /**
   * 获取系统状态
   */
  getStatus(): {
    version: string;
    experts: number;
    status: string;
  } {
    return {
      version: this.version,
      experts: EXPERTS_36.length,
      status: 'running'
    };
  }
}

export default NineLawOS;
