/**
 * Prompt Precision - 精准模式核心引擎 V3
 * 目标：让AI精准理解用户意图，真正解决沟通问题
 */

// ============================================
// 规则库
// ============================================

const FILLERS = [
  '你好', '您好', '嗨', 'hey', 'hi', 'hello', 'yo',
  '请问', '请教', '咨询',
  '谢谢', '感谢', '麻烦', '劳驾',
  '那个', '这个', '就是', '关于',
  '能不能', '可不可以',
  '然后', '那个啥', '呃', '嗯',
  '啊', '呀', '呢', '吧', '哦',
  '因为', '所以', '但是', '不过', '而且',
  '如果', '虽然', '即使',
  '非常', '特别', '很', '挺', '太', '好',
];

const INTENT_PATTERNS = {
  debug: ['debug', '调试', 'bug', '错误', '报错', '出问题', '有问题', '不对', '不行', '失败', '异常', '有什么问题', '看看问题', '找出问题', '修复问题', '解决'],
  performance: ['慢', '性能', '优化', '快', '效率', '卡顿', '延迟', '耗时'],
  create: ['写代码', '创建', '做一个', '写一个', '帮我写', '生成', '写段', '写个', '做一个'],
  explain: ['解释', '讲讲', '什么是', '是什么', '为什么', '怎么回事', '原理', '科普', '讲一讲', '说一说'],
  modify: ['修改', '改成', '改一下', '换一下', '调整', '重构', '重写', '转换'],
  analyze: ['分析', '检查', '评估', '研究', '对比', '看看', '审查'],
  teach: ['教我', '学习', '教一下', '入门', '教', '学'],
  review: ['review', '审阅', 'review一下', 'review代码'],
};

const LANGUAGE_PATTERNS = {
  javascript: ['javascript', 'js', 'node', 'nodejs', 'ecmascript'],
  typescript: ['typescript', 'ts'],
  python: ['python', 'py', 'django', 'flask'],
  java: ['java', 'spring'],
  cpp: ['c++', 'cpp'],
  csharp: ['c#', 'csharp', '.net', 'dotnet'],
  go: ['golang', 'go语言'],
  rust: ['rust'],
  php: ['php', 'laravel'],
  ruby: ['ruby', 'rails'],
  swift: ['swift', 'ios'],
  kotlin: ['kotlin', 'android'],
  sql: ['sql', 'mysql', 'postgresql', '数据库', 'db'],
  html: ['html', '前端', '网页'],
  css: ['css', '样式', 'styling'],
  react: ['react', 'reactjs', 'jsx'],
  vue: ['vue', 'vuejs'],
  nextjs: ['nextjs', 'next.js'],
  angular: ['angular'],
  flutter: ['flutter', 'dart'],
  c: ['c语言', 'c编程'],
  r: ['r语言', 'r语言编程'],
  matlab: ['matlab'],
  shell: ['shell', 'bash', '脚本'],
};

const FOCUS_PATTERNS = {
  loop: ['循环', 'for', 'while', 'loop', '迭代'],
  function: ['函数', 'function', '方法', 'method', 'func'],
  async: ['异步', 'async', 'await', 'promise', '回调'],
  array: ['数组', 'array', 'list', '列表'],
  object: ['对象', 'object', '字典', 'map'],
  string: ['字符串', 'string', '文本'],
  error: ['错误', 'exception', '异常', '报错', 'error'],
  memory: ['内存', 'memory', '泄漏'],
  api: ['api', '接口', '请求', 'http', 'rest'],
  database: ['数据库', 'db', 'database', 'sql'],
  security: ['安全', 'security', 'xss', '注入', '加密'],
  performance: ['性能', 'performance', '优化'],
  algorithm: ['算法', '排序', '搜索', '查找', 'tree', '图'],
  ui: ['界面', 'ui', '界面', '样式', '布局'],
  test: ['测试', 'test', '单元测试'],
  deploy: ['部署', 'deploy', '上线', '发布'],
  auth: ['登录', '注册', 'auth', '权限', 'permission', 'oauth'],
  api: ['api', '接口', 'rest', 'graphql'],
};

// ============================================
// 核心函数
// ============================================

function transform(input) {
  const original = input.trim();
  
  // 1. 清理
  const cleaned = cleanInput(original);
  
  // 2. 识别意图
  const intent = detectIntent(cleaned);
  
  // 3. 识别语言
  const languages = detectLanguages(cleaned);
  
  // 4. 识别关注点
  const focus = detectFocus(cleaned);
  
  // 5. 提取关键细节（数字、参数等）
  const keyDetails = extractKeyDetails(original);
  
  // 6. 生成目标描述（更智能）
  const goal = generateGoal(cleaned, intent, languages, focus);
  
  // 7. 检查缺失信息并给出引导
  const guidance = generateGuidance(intent, goal, languages, original);
  
  // 8. 生成最终输出
  return formatOutput(intent, languages, focus, goal, keyDetails, guidance, original);
}

function cleanInput(input) {
  let result = input.trim();
  
  for (let filler of FILLERS) {
    let pattern = new RegExp(`[，,、。.\\s]*${escapeRegex(filler)}[，,、。.\\s]*`, 'gi');
    result = result.replace(pattern, ' ');
  }
  
  result = result.replace(/\s+/g, ' ').trim();
  return result;
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function detectIntent(text) {
  let lower = text.toLowerCase();
  
  for (let [intent, keywords] of Object.entries(INTENT_PATTERNS)) {
    for (let keyword of keywords) {
      if (lower.includes(keyword)) {
        return getIntentLabel(intent);
      }
    }
  }
  
  return '一般请求';
}

function getIntentLabel(intent) {
  const labels = {
    debug: '代码调试',
    performance: '性能优化',
    create: '代码创建',
    explain: '概念解释',
    modify: '代码修改',
    analyze: '分析检查',
    teach: '学习指导',
    review: '代码审阅',
  };
  return labels[intent] || '一般请求';
}

function detectLanguages(text) {
  let lower = text.toLowerCase();
  let detected = [];
  
  for (let [lang, keywords] of Object.entries(LANGUAGE_PATTERNS)) {
    for (let keyword of keywords) {
      if (lower.includes(keyword)) {
        detected.push(getLanguageLabel(lang));
        break;
      }
    }
  }
  
  return [...new Set(detected)];
}

function getLanguageLabel(lang) {
  const labels = {
    javascript: 'JavaScript', typescript: 'TypeScript', python: 'Python',
    java: 'Java', cpp: 'C++', csharp: 'C#', go: 'Go', rust: 'Rust',
    php: 'PHP', ruby: 'Ruby', swift: 'Swift', kotlin: 'Kotlin',
    sql: 'SQL', html: 'HTML', css: 'CSS', react: 'React', vue: 'Vue',
    nextjs: 'Next.js', angular: 'Angular', flutter: 'Flutter/Dart',
    c: 'C', r: 'R', matlab: 'MATLAB', shell: 'Shell/Bash',
  };
  return labels[lang] || lang;
}

function detectFocus(text) {
  let lower = text.toLowerCase();
  let detected = [];
  
  for (let [focus, keywords] of Object.entries(FOCUS_PATTERNS)) {
    for (let keyword of keywords) {
      if (lower.includes(keyword)) {
        detected.push(getFocusLabel(focus));
        break;
      }
    }
  }
  
  return [...new Set(detected)];
}

function getFocusLabel(focus) {
  const labels = {
    loop: '循环结构', function: '函数/方法', async: '异步编程',
    array: '数组/列表', object: '对象/字典', string: '字符串处理',
    error: '错误处理', memory: '内存管理', api: 'API接口',
    database: '数据库', security: '安全性', performance: '性能问题',
    algorithm: '算法', ui: '界面/样式', test: '测试',
    deploy: '部署/发布', auth: '登录/权限',
  };
  return labels[focus] || focus;
}

function extractKeyDetails(text) {
  const patterns = [
    { match: /\d+行/gi, label: '行数' },
    { match: /\d+个/gi, label: '数量' },
    { match: /\d+秒/gi, label: '秒' },
    { match: /\d+分钟/gi, label: '分钟' },
    { match: /\d+小时/gi, label: '小时' },
    { match: /\d+MB/gi, label: 'MB' },
    { match: /\d+GB/gi, label: 'GB' },
    { match: /v\d+/gi, label: '版本' },
    { match: /第\d+/gi, label: '序号' },
    { match: /\d+%/gi, label: '百分比' },
  ];
  
  let details = [];
  for (let { match, label } of patterns) {
    let m = text.match(match);
    if (m) details.push(...m);
  }
  return [...new Set(details)];
}

function generateGoal(text, intent, languages, focus) {
  // 尝试从原句中提取最核心的目标
  let goal = text;
  
  // 移除意图词
  for (let kws of Object.values(INTENT_PATTERNS)) {
    for (let kw of kws) {
      goal = goal.replace(new RegExp(escapeRegex(kw), 'gi'), '');
    }
  }
  
  // 移除语言词
  for (let kws of Object.values(LANGUAGE_PATTERNS)) {
    for (let kw of kws) {
      goal = goal.replace(new RegExp(escapeRegex(kw), 'gi'), '');
    }
  }
  
  // 移除无意义开头词
  const removePrefix = ['帮我', '帮我', '这段', '这个', '那个', '请', '能不能', '麻烦', '的'];
  for (let prefix of removePrefix) {
    if (goal.startsWith(prefix)) {
      goal = goal.slice(prefix.length).trim();
    }
  }
  
  // 移除无意义结尾词
  const removeSuffix = ['一下', '谢谢', '好吗', '帮我', '差'];
  for (let suffix of removeSuffix) {
    if (goal.endsWith(suffix)) {
      goal = goal.slice(0, -suffix.length).trim();
    }
  }
  
  // 清理残留的无意义字符
  goal = goal.replace(/^的+/, '').replace(/的+$/, '').trim();
  goal = goal.replace(/\s+/g, ' ').trim();
  
  // 清理
  goal = goal.replace(/[,，.。!！?？]+/g, ' ').replace(/\s+/g, ' ').trim();
  
  // 如果太长，截取关键部分（保留前40字符）
  if (goal.length > 50) {
    goal = goal.slice(0, 50).trim();
    // 尝试在词语边界截断
    const cutPositions = [goal.lastIndexOf(' '), goal.lastIndexOf('的')];
    for (let pos of cutPositions) {
      if (pos > 20) {
        goal = goal.slice(0, pos).trim();
        break;
      }
    }
  }
  
  // 如果太短或无意义，使用默认目标
  if (goal.length < 3 || /^\d+$/.test(goal) || ['代码', '这段', '这个'].includes(goal)) {
    return getDefaultGoal(intent, languages, focus);
  }
  
  return goal;
}

function getDefaultGoal(intent, languages, focus) {
  const defaults = {
    '代码调试': '定位并修复代码问题',
    '性能优化': '分析性能瓶颈并优化',
    '代码创建': languages.length ? `用${languages[0]}实现功能` : '实现所需功能',
    '概念解释': '解释核心概念和原理',
    '代码修改': '按要求修改代码',
    '分析检查': '分析检查并给出建议',
    '学习指导': '帮助理解学习',
    '代码审阅': '代码审查和改进建议',
    '一般请求': '解决用户问题',
  };
  return defaults[intent] || '完成用户请求';
}

function generateGuidance(intent, goal, languages, original) {
  let guidance = {
    questions: [],
    suggestions: [],
  };
  
  if (intent === '代码调试') {
    guidance.questions.push('代码的具体内容是什么？');
    if (!original.includes('错误') && !original.includes('报错')) {
      guidance.questions.push('有没有具体的错误信息？');
    }
    guidance.questions.push('运行环境和配置是什么？');
  }
  
  if (intent === '性能优化') {
    guidance.questions.push('当前性能指标是什么（如响应时间、执行时间）？');
    guidance.questions.push('目标性能指标是多少？');
  }
  
  if (intent === '代码创建') {
    guidance.questions.push('具体的功能需求是什么？');
    guidance.questions.push('有参考资料或示例吗？');
    if (languages.length === 0) {
      guidance.questions.push('使用什么编程语言？');
    }
  }
  
  if (intent === '概念解释') {
    guidance.questions.push('对哪个具体方面有疑问？');
    guidance.questions.push('有什么背景知识吗？');
  }
  
  if (intent === '代码审阅') {
    guidance.questions.push('代码的完整内容是什么？');
    guidance.questions.push('重点关注哪方面（性能、安全、可读性）？');
  }
  
  // 生成建议
  if (guidance.questions.length > 0) {
    guidance.suggestions.push('提供以上信息可以获得更精准的帮助');
  }
  
  return guidance;
}

function formatOutput(intent, languages, focus, goal, keyDetails, guidance, original) {
  let lines = [];
  
  // 头部
  lines.push('## 🎯 精准化指令');
  lines.push('');
  
  // 核心信息
  lines.push(`**📌 意图：** ${intent}`);
  
  if (languages.length > 0) {
    lines.push(`**💻 语言：** ${languages.join(', ')}`);
  }
  
  if (focus.length > 0) {
    lines.push(`**🎯 关注点：** ${focus.join(', ')}`);
  }
  
  if (keyDetails.length > 0) {
    lines.push(`**📊 约束条件：** ${keyDetails.join(', ')}`);
  }
  
  lines.push(`**🎯 目标：** ${goal}`);
  
  // 引导信息
  if (guidance.questions.length > 0) {
    lines.push('');
    lines.push('**💡 为了更精准地帮助你，请提供：**');
    for (let q of guidance.questions) {
      lines.push(`- ${q}`);
    }
  }
  
  // 原始消息
  lines.push('');
  lines.push('---');
  lines.push(`**📝 原始消息：** ${original}`);
  
  return {
    success: true,
    structured: lines.join('\n'),
    metadata: { intent, languages, focus, goal, keyDetails },
    original,
    guidance,
  };
}

// ============================================
// CLI
// ============================================

function main() {
  let input = process.argv.slice(2).join(' ');
  
  if (!input) {
    console.log('用法: node precision-engine.js <消息>');
    console.log('示例: node precision-engine.js "Python的for循环为什么运行慢"');
    process.exit(0);
  }
  
  if (input === '--test') {
    runTests();
    process.exit(0);
  }
  
  let result = transform(input);
  console.log(result.structured);
}

function runTests() {
  console.log('🧪 V3 测试\n');
  
  const tests = [
    'Python的for循环为什么运行慢',
    '帮我看看代码有什么问题',
    'React的useEffect是什么',
    '帮我写一个登录功能',
    '这段Java代码性能很差帮我优化',
    '帮我debug这段代码',
  ];
  
  for (let test of tests) {
    console.log(`\n📝 输入: ${test}`);
    console.log('─'.repeat(50));
    let result = transform(test);
    console.log(result.structured);
  }
}

module.exports = { transform };

if (require.main === module) {
  main();
}
