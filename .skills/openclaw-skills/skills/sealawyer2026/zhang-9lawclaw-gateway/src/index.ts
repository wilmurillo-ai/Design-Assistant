/**
 * 9LawClaw Gateway
 * 法律智能操作系统的统一入口网关
 */

import { OpenClawSkill, OpenClawContext } from '@openclaw/core';

// 用户类型定义
export type UserType = 'individual' | 'lawyer' | 'firm' | 'enterprise' | 'government';

// 请求接口
export interface GatewayRequest {
  query: string;
  userId?: string;
  userType?: UserType;
  context?: any;
  source: 'wechat' | 'web' | 'api' | 'plugin';
}

// 响应接口
export interface GatewayResponse {
  expert: string;
  expertName: string;
  response: string;
  relatedCases?: any[];
  applicableLaws?: string[];
  suggestions?: string[];
  confidence: number;
  nextSteps?: string[];
}

// 专家路由配置
interface ExpertRoute {
  id: string;
  name: string;
  keywords: string[];
  categories: string[];
  description: string;
}

// 36位专家路由表
const EXPERT_ROUTES: ExpertRoute[] = [
  {
    id: 'zhang-corporate-law',
    name: '公司法专家',
    keywords: ['公司', '股权', '股东', '董事会', '并购', '上市', '章程', '分立', '合并'],
    categories: ['公司法', '商事'],
    description: '专注公司设立、股权设计、并购重组、融资上市'
  },
  {
    id: 'zhang-labor-law',
    name: '劳动法专家',
    keywords: ['劳动', '工资', '辞退', '工伤', '社保', '劳动合同', '试用期', '加班', '仲裁'],
    categories: ['劳动法', '社会保障'],
    description: '专注劳动合同、薪酬社保、劳动争议、裁员安置'
  },
  {
    id: 'zhang-marriage-law',
    name: '婚姻家事专家',
    keywords: ['离婚', '结婚', '抚养权', '财产分割', '继承', '遗嘱', '赡养', '家暴'],
    categories: ['婚姻家事'],
    description: '专注离婚财产、子女抚养、继承规划、婚前协议'
  },
  {
    id: 'zhang-ip-law',
    name: '知识产权专家',
    keywords: ['专利', '商标', '著作权', '版权', '侵权', '技术秘密', '知产'],
    categories: ['知识产权'],
    description: '专注专利商标、著作权、商业秘密、侵权维权'
  },
  {
    id: 'zhang-contract-law',
    name: '合同纠纷专家',
    keywords: ['合同', '违约', '履行', '解除', '条款', '协议', '定金', '违约金'],
    categories: ['合同法'],
    description: '专注合同起草、履行争议、违约责任、解除终止'
  },
  {
    id: 'zhang-property-law',
    name: '房产纠纷专家',
    keywords: ['房子', '买房', '卖房', '租房', '物业', '装修', '拆迁', '房产证'],
    categories: ['房地产'],
    description: '专注商品房买卖、房屋租赁、物业纠纷、拆迁补偿'
  },
  {
    id: 'zhang-debt-law',
    name: '债权债务专家',
    keywords: ['借钱', '欠钱', '债务', '债权', '担保', '抵押', '借条', '欠条'],
    categories: ['债权债务'],
    description: '专注民间借贷、担保追偿、债务重组、不良资产'
  },
  {
    id: 'zhang-tax-law',
    name: '税法专家',
    keywords: ['税', '增值税', '企业所得税', '个税', '税务', '发票', '偷税'],
    categories: ['税法'],
    description: '专注企业税务、税收筹划、税务争议、国际税务'
  },
  {
    id: 'zhang-criminal-law',
    name: '刑事辩护专家',
    keywords: ['犯罪', '刑法', '拘留', '逮捕', '判刑', '取保候审', '辩护人'],
    categories: ['刑事'],
    description: '专注经济犯罪、职务犯罪、暴力犯罪、刑事合规'
  },
  {
    id: 'zhang-administrative-law',
    name: '行政法专家',
    keywords: ['行政处罚', '行政许可', '行政复议', '行政诉讼', '政府'],
    categories: ['行政法'],
    description: '专注行政处罚、行政许可、行政复议、行政诉讼'
  },
  {
    id: 'zhang-compliance-audit',
    name: '合规审计专家',
    keywords: ['合规', '审计', '内控', '风险', '反舞弊', '尽职调查'],
    categories: ['合规'],
    description: '专注合规体系、专项审计、风险排查、整改建议'
  },
  {
    id: 'zhang-antitrust-law',
    name: '反垄断专家',
    keywords: ['垄断', '竞争', '经营者集中', '滥用市场支配地位'],
    categories: ['反垄断'],
    description: '专注垄断协议、滥用市场支配、经营者集中、调查应对'
  },
  {
    id: 'zhang-foreign-investment',
    name: '外商投资专家',
    keywords: ['外资', 'FDI', 'VIE', 'WOFE', '外商投资', '准入'],
    categories: ['外商投资'],
    description: '专注FDI准入、VIE架构、安全审查、退出机制'
  },
  {
    id: 'zhang-us-law',
    name: '美国法律专家',
    keywords: ['美国', 'SEC', '出口管制', '长臂管辖', 'CFIUS'],
    categories: ['涉外'],
    description: '专注跨境合规、出口管制、数据跨境、SEC合规'
  },
  {
    id: 'zhang-eu-law',
    name: '欧盟法律专家',
    keywords: ['欧盟', 'GDPR', 'AI法案', 'CE认证', '产品责任'],
    categories: ['涉外'],
    description: '专注GDPR、AI法案、市场准入、产品责任'
  },
  {
    id: 'zhang-seasia-law',
    name: '东南亚法律专家',
    keywords: ['东南亚', '东盟', 'ASEAN', '新加坡', '泰国', '越南'],
    categories: ['涉外'],
    description: '专注ASEAN市场合规与投资'
  },
  {
    id: 'zhang-japan-law',
    name: '日本法律专家',
    keywords: ['日本', '日本市场', '日本投资', '日本公司'],
    categories: ['涉外'],
    description: '专注日本市场进入与合规'
  },
  {
    id: 'zhang-africa-law',
    name: '非洲法律专家',
    keywords: ['非洲', '投资', '矿业', '基础设施', '区域贸易'],
    categories: ['涉外'],
    description: '专注非洲投资与区域贸易合规'
  },
  {
    id: 'zhang-arab-law',
    name: '阿拉伯法律专家',
    keywords: ['中东', '伊斯兰', '沙特', '阿联酋', '宗教法'],
    categories: ['涉外'],
    description: '专注伊斯兰法与现代商业合规'
  },
  {
    id: 'zhang-latin-america-law',
    name: '拉美法律专家',
    keywords: ['拉美', '巴西', '墨西哥', '智利', '南方共同市场'],
    categories: ['涉外'],
    description: '专注拉美投资与区域一体化合规'
  },
  {
    id: 'zhang-russia-law',
    name: '俄罗斯法律专家',
    keywords: ['俄罗斯', '制裁', '欧亚经济联盟', '独联体'],
    categories: ['涉外'],
    description: '专注制裁合规与欧亚经济联盟'
  },
  {
    id: 'zhang-energy-law',
    name: '能源法专家',
    keywords: ['电力', '新能源', '光伏', '风电', '油气', '碳中和'],
    categories: ['能源'],
    description: '专注电力、油气、新能源、碳中和合规'
  },
  {
    id: 'zhang-environment-law',
    name: '环保法专家',
    keywords: ['环保', '环评', '污染', '双碳', '排污', '碳排放'],
    categories: ['环保'],
    description: '专注环评审批、污染防治、双碳合规、环保督察'
  },
  {
    id: 'zhang-healthcare-law',
    name: '医疗健康专家',
    keywords: ['医院', '医疗', '医药', '医疗器械', '临床试验', '医保'],
    categories: ['医疗'],
    description: '专注医疗机构、医药企业、医疗器械、互联网医疗'
  },
  {
    id: 'zhang-gaming-law',
    name: '游戏法专家',
    keywords: ['游戏', '版号', '防沉迷', '电竞', '虚拟财产'],
    categories: ['游戏'],
    description: '专注游戏出版、运营合规、电竞赛事、出海合规'
  },
  {
    id: 'zhang-entertainment-law',
    name: '娱乐传媒专家',
    keywords: ['影视', '艺人', '版权', 'MCN', '直播', '短视频'],
    categories: ['娱乐'],
    description: '专注影视制作、艺人经纪、版权交易、MCN合规'
  },
  {
    id: 'zhang-education-law',
    name: '教育法专家',
    keywords: ['学校', '培训', '双减', '办学许可', '留学'],
    categories: ['教育'],
    description: '专注民办教育、培训机构、留学服务、双减政策'
  },
  {
    id: 'zhang-realestate-dev-law',
    name: '房地产开发专家',
    keywords: ['开发商', '拿地', '预售', '楼盘', '物业'],
    categories: ['房地产'],
    description: '专注拿地、建设、销售、物业全流程'
  },
  {
    id: 'zhang-construction-law',
    name: '建设工程专家',
    keywords: ['工程', '招标', '投标', '施工', '质量', '索赔'],
    categories: ['工程'],
    description: '专注招标投标、工程合同、质量纠纷、索赔结算'
  },
  {
    id: 'zhang-insurance-law',
    name: '保险法专家',
    keywords: ['保险', '理赔', '保单', '保险人', '被保险人'],
    categories: ['保险'],
    description: '专注保险合规、产品设计、理赔争议、资金运用'
  },
  {
    id: 'zhang-aviation-law',
    name: '航空法专家',
    keywords: ['航空', '机场', '飞机', '航班', '空难', '航权'],
    categories: ['航空'],
    description: '专注航空运输、机场运营、航空事故、飞机租赁'
  },
  {
    id: 'zhang-food-safety-law',
    name: '食品安全专家',
    keywords: ['食品', '餐饮', '生产许可', '食品安全', '保健品'],
    categories: ['食品'],
    description: '专注食品生产、流通、餐饮、标签、特殊食品'
  },
  {
    id: 'zhang-sports-law',
    name: '体育法专家',
    keywords: ['运动员', '俱乐部', '赛事', '转会', '赞助', '反兴奋剂'],
    categories: ['体育'],
    description: '专注运动员经纪、赛事运营、转会纠纷、反兴奋剂'
  },
  {
    id: 'zhang-data-compliance',
    name: '数据合规专家',
    keywords: ['数据', '个保法', '网安法', '数据出境', '隐私', 'GDPR'],
    categories: ['数据合规'],
    description: '专注数据安全、跨境传输、隐私保护、GDPR合规'
  },
  {
    id: 'zhang-ai-law',
    name: 'AI法律专家',
    keywords: ['AI', '算法', '生成式AI', '深度合成', '算法备案'],
    categories: ['AI'],
    description: '专注AI合规、算法监管、生成式AI、伦理法律'
  }
];

// 意图识别关键词
const INTENT_KEYWORDS: Record<string, string[]> = {
  'case_search': ['案例', '判例', '判决', '法院', '胜诉', '败诉', '类似'],
  'law_query': ['法条', '法规', '法律', '第几条', '规定', '依据'],
  'doc_generate': ['文书', '合同', '协议', '起诉状', '律师函', '生成'],
  'contract_review': ['审查', '审合同', '看合同', '风险', '条款'],
  'consultation': ['咨询', '怎么办', '建议', '问题', '帮忙']
};

export default class NineLawClawGateway implements OpenClawSkill {
  name = 'zhang-9lawclaw-gateway';
  version = '0.5.0';
  description = '9LawClaw法律智能操作系统统一入口网关';

  private context?: OpenClawContext;

  async onLoad(context: OpenClawContext): Promise<void> {
    this.context = context;
    console.log('🦞 9LawClaw Gateway 已启动');
    console.log(`📊 已加载 ${EXPERT_ROUTES.length} 位专家`);
  }

  async onUnload(): Promise<void> {
    console.log('👋 9LawClaw Gateway 已关闭');
  }

  /**
   * 核心路由方法
   * 接收用户请求，返回匹配的专家响应
   */
  async route(request: GatewayRequest): Promise<GatewayResponse> {
    const { query, userType = 'individual' } = request;

    // 1. 意图识别
    const intent = this.identifyIntent(query);
    console.log(`🔍 意图识别: ${intent}`);

    // 2. 专家匹配
    const matchedExpert = this.matchExpert(query, userType);
    console.log(`🎯 匹配专家: ${matchedExpert.name} (${matchedExpert.id})`);

    // 3. 调用专家技能
    const response = await this.invokeExpert(matchedExpert.id, query, userType);

    // 4. 返回结构化结果
    return {
      expert: matchedExpert.id,
      expertName: matchedExpert.name,
      response: response.text,
      relatedCases: response.cases,
      applicableLaws: response.laws,
      suggestions: response.suggestions,
      confidence: response.confidence,
      nextSteps: response.nextSteps
    };
  }

  /**
   * 意图识别
   */
  private identifyIntent(query: string): string {
    const lowerQuery = query.toLowerCase();
    
    for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
      if (keywords.some(kw => lowerQuery.includes(kw))) {
        return intent;
      }
    }
    
    return 'consultation'; // 默认咨询
  }

  /**
   * 专家匹配算法
   */
  private matchExpert(query: string, userType: UserType): ExpertRoute {
    const lowerQuery = query.toLowerCase();
    let bestMatch: ExpertRoute | null = null;
    let bestScore = 0;

    for (const expert of EXPERT_ROUTES) {
      let score = 0;
      
      // 关键词匹配
      for (const keyword of expert.keywords) {
        if (lowerQuery.includes(keyword.toLowerCase())) {
          score += 10;
          // 完整词匹配加分
          if (lowerQuery.includes(keyword)) {
            score += 5;
          }
        }
      }

      // 用户类型加权
      if (userType === 'enterprise' && expert.categories.includes('公司法')) {
        score += 3;
      }
      if (userType === 'lawyer' && expert.categories.includes('诉讼')) {
        score += 3;
      }

      if (score > bestScore) {
        bestScore = score;
        bestMatch = expert;
      }
    }

    // 如果没有匹配，返回公司法专家作为兜底
    return bestMatch || EXPERT_ROUTES[0];
  }

  /**
   * 调用专家技能
   */
  private async invokeExpert(
    expertId: string, 
    query: string, 
    userType: UserType
  ): Promise<any> {
    // 实际实现中，这里会调用OpenClaw的技能系统
    // 现在返回模拟数据
    
    const expert = EXPERT_ROUTES.find(e => e.id === expertId);
    
    return {
      text: `【${expert?.name}】您好！我是您的专业法律顾问。\n\n关于您的问题："${query}"\n\n${expert?.description}\n\n让我为您进行详细分析...`,
      cases: [
        { title: '典型案例1', id: 'CASE-001' },
        { title: '典型案例2', id: 'CASE-002' }
      ],
      laws: ['相关法规第X条', '相关法规第Y条'],
      suggestions: ['建议1', '建议2', '建议3'],
      confidence: 0.92,
      nextSteps: ['继续追问', '查看案例', '生成文书']
    };
  }

  /**
   * 获取所有专家列表
   */
  getExperts(): ExpertRoute[] {
    return EXPERT_ROUTES;
  }

  /**
   * 获取专家详情
   */
  getExpertDetail(expertId: string): ExpertRoute | null {
    return EXPERT_ROUTES.find(e => e.id === expertId) || null;
  }

  /**
   * 获取系统状态
   */
  getStatus() {
    return {
      version: this.version,
      experts: EXPERT_ROUTES.length,
      uptime: process.uptime(),
      status: 'running'
    };
  }
}

// 导出
export { EXPERT_ROUTES, INTENT_KEYWORDS };
