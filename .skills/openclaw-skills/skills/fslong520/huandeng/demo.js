const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'CodeBuddy';
pres.title = 'pptx 技能';

// 霓虹赛博朋克配色 - v7 风格
const colors = {
  bg: '0F0F23',           // 虚空黑
  primary: '1E1E3F',      // 深海蓝
  neonBlue: '00D4FF',     // 电光蓝
  neonPurple: 'B829F7',   // 霓虹紫
  neonPink: 'FF006E',     // 霓虹粉
  neonCyan: '00F5D4',     // 霓虹青
  text: 'FFFFFF',          // 纯白
  textMuted: '8B8B9A',    // 灰紫
  glass: 'FFFFFF'          // 玻璃白
};

// ========== 第1页：封面 ==========
let slide1 = pres.addSlide();
slide1.background = { color: colors.bg };

// 背景装饰圆形
slide1.addShape(pres.ShapeType.ellipse, {
  x: -2, y: -3, w: 10, h: 10,
  fill: { color: colors.neonPurple, transparency: 85 }
});
slide1.addShape(pres.ShapeType.ellipse, {
  x: 6, y: 1, w: 6, h: 6,
  fill: { color: colors.neonBlue, transparency: 90 }
});
slide1.addShape(pres.ShapeType.ellipse, {
  x: 2, y: 4, w: 8, h: 8,
  fill: { color: colors.neonPink, transparency: 92 }
});

// 顶部霓虹线
slide1.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 0.05,
  fill: { color: colors.neonBlue }
});

// 主标题
slide1.addText('pptx', {
  x: 0.8, y: 1.2, w: 8, h: 1.2,
  fontSize: 96, color: colors.text, bold: true,
  fontFace: 'Arial Black'
});
slide1.addText('技能', {
  x: 0.8, y: 2.3, w: 5, h: 1,
  fontSize: 72, color: colors.neonBlue, bold: true,
  fontFace: 'Microsoft YaHei'
});

slide1.addText('PowerPoint Automation Toolkit', {
  x: 0.8, y: 3.4, w: 8, h: 0.5,
  fontSize: 20, color: colors.textMuted,
  fontFace: 'Microsoft YaHei'
});

// 霓虹分隔线
slide1.addShape(pres.ShapeType.rect, {
  x: 0.8, y: 4, w: 2, h: 0.05,
  fill: { color: colors.neonPink }
});

// 版本标签
slide1.addShape(pres.ShapeType.rect, {
  x: 0.8, y: 4.8, w: 1.2, h: 0.4,
  fill: { color: colors.neonPurple, transparency: 80 },
  line: { color: colors.neonPurple, width: 1 }
});
slide1.addText('v3.0', {
  x: 0.8, y: 4.8, w: 1.2, h: 0.4,
  fontSize: 14, color: colors.text, align: 'center', valign: 'middle',
  fontFace: 'Arial'
});

// ========== 第2页：核心能力 - Bento网格 ==========
let slide2 = pres.addSlide();
slide2.background = { color: colors.bg };

slide2.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 0.05,
  fill: { color: colors.neonBlue }
});

slide2.addText('核心能力', {
  x: 0.8, y: 0.5, w: 8.4, h: 0.8,
  fontSize: 40, color: colors.text, bold: true,
  fontFace: 'Microsoft YaHei'
});
slide2.addShape(pres.ShapeType.rect, {
  x: 0.8, y: 1.2, w: 1.5, h: 0.05,
  fill: { color: colors.neonPink }
});

// 4卡片 Bento 布局
const cards = [
  { num: '01', en: 'CREATE', zh: '创建', desc: '从零生成专业演示文稿', color: colors.neonBlue },
  { num: '02', en: 'EDIT', zh: '编辑', desc: '解包编辑打包修改', color: colors.neonPurple },
  { num: '03', en: 'CONVERT', zh: '转换', desc: 'HTML/CSS 转 PPT', color: colors.neonPink },
  { num: '04', en: 'VISUALIZE', zh: '可视化', desc: '数据图表自动生成', color: colors.neonCyan }
];

const cardW = 1.9;
const gap = 0.35;
const startX = 0.8;

cards.forEach((card, i) => {
  const x = startX + i * (cardW + gap);
  const y = 1.5;
  
  // 玻璃卡片
  slide2.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: cardW, h: 2.8,
    fill: { color: colors.glass, transparency: 92 },
    line: { color: card.color, width: 1 }
  });
  
  // 顶部霓虹条
  slide2.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: cardW, h: 0.04,
    fill: { color: card.color }
  });
  
  // 编号
  slide2.addText(card.num, {
    x: x + 0.15, y: y + 0.25, w: 0.5, h: 0.4,
    fontSize: 28, color: card.color, bold: true,
    fontFace: 'Arial'
  });
  
  // 英文标签
  slide2.addText(card.en, {
    x: x + 0.15, y: y + 0.9, w: cardW - 0.3, h: 0.3,
    fontSize: 12, color: card.color, bold: true,
    fontFace: 'Arial'
  });
  
  // 中文标题
  slide2.addText(card.zh, {
    x: x + 0.15, y: y + 1.25, w: cardW - 0.3, h: 0.4,
    fontSize: 22, color: colors.text, bold: true,
    fontFace: 'Microsoft YaHei'
  });
  
  // 分隔线
  slide2.addShape(pres.ShapeType.rect, {
    x: x + 0.15, y: y + 1.8, w: cardW - 0.3, h: 0.02,
    fill: { color: '2D2D5A' }
  });
  
  // 描述
  slide2.addText(card.desc, {
    x: x + 0.15, y: y + 2.0, w: cardW - 0.3, h: 0.6,
    fontSize: 12, color: colors.textMuted,
    fontFace: 'Microsoft YaHei'
  });
});

// ========== 第3页：工作流程 - 垂直时间线 ==========
let slide3 = pres.addSlide();
slide3.background = { color: colors.bg };

slide3.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 0.05,
  fill: { color: colors.neonBlue }
});

slide3.addText('工作流程', {
  x: 0.8, y: 0.5, w: 8.4, h: 0.8,
  fontSize: 40, color: colors.text, bold: true,
  fontFace: 'Microsoft YaHei'
});
slide3.addShape(pres.ShapeType.rect, {
  x: 0.8, y: 1.2, w: 1.5, h: 0.05,
  fill: { color: colors.neonPink }
});

const steps = [
  { num: '01', en: 'HTML/CSS Design', zh: '设计', desc: '设计幻灯片布局和样式', tag: 'DESIGN', color: colors.neonBlue },
  { num: '02', en: 'Playwright Render', zh: '渲染', desc: '无头浏览器提取元素位置', tag: 'RENDER', color: colors.neonPurple },
  { num: '03', en: 'PptxGenJS Generate', zh: '生成', desc: '输出 .pptx 文件', tag: 'OUTPUT', color: colors.neonPink }
];

steps.forEach((step, i) => {
  const y = 1.5 + i * 1.2;
  
  // 连接线
  if (i < 2) {
    slide3.addShape(pres.ShapeType.line, {
      x: 1.25, y: y + 0.8, w: 0, h: 0.4,
      line: { color: colors.neonBlue, width: 2 }
    });
  }
  
  // 霓虹编号圆形
  slide3.addShape(pres.ShapeType.ellipse, {
    x: 0.8, y: y, w: 0.9, h: 0.9,
    fill: { color: step.color, transparency: 20 },
    line: { color: step.color, width: 2 }
  });
  slide3.addText(step.num, {
    x: 0.8, y: y, w: 0.9, h: 0.9,
    fontSize: 24, color: step.color, bold: true, align: 'center', valign: 'middle',
    fontFace: 'Arial'
  });
  
  // 内容卡片
  slide3.addShape(pres.ShapeType.rect, {
    x: 2, y: y, w: 7.2, h: 0.9,
    fill: { color: colors.glass, transparency: 95 },
    line: { color: step.color, width: 1 }
  });
  
  // 英文标题
  slide3.addText(step.en, {
    x: 2.2, y: y + 0.15, w: 4, h: 0.35,
    fontSize: 16, color: step.color, bold: true,
    fontFace: 'Arial'
  });
  
  // 中文标题
  slide3.addText(step.zh, {
    x: 2.2, y: y + 0.5, w: 1, h: 0.3,
    fontSize: 14, color: colors.text,
    fontFace: 'Microsoft YaHei'
  });
  
  // 描述
  slide3.addText(step.desc, {
    x: 3.3, y: y + 0.5, w: 5.5, h: 0.3,
    fontSize: 12, color: colors.textMuted,
    fontFace: 'Microsoft YaHei'
  });
  
  // 标签
  slide3.addShape(pres.ShapeType.rect, {
    x: 8, y: y + 0.25, w: 1, h: 0.4,
    fill: { color: step.color, transparency: 85 }
  });
  slide3.addText(step.tag, {
    x: 8, y: y + 0.25, w: 1, h: 0.4,
    fontSize: 10, color: step.color, align: 'center', valign: 'middle',
    fontFace: 'Arial'
  });
});

// ========== 第4页：关键约束 - 霓虹卡片网格 ==========
let slide4 = pres.addSlide();
slide4.background = { color: colors.bg };

slide4.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 0.05,
  fill: { color: colors.neonBlue }
});

slide4.addText('关键约束', {
  x: 0.8, y: 0.5, w: 8.4, h: 0.8,
  fontSize: 40, color: colors.text, bold: true,
  fontFace: 'Microsoft YaHei'
});
slide4.addShape(pres.ShapeType.rect, {
  x: 0.8, y: 1.2, w: 1.5, h: 0.05,
  fill: { color: colors.neonPink }
});

const constraints = [
  { label: 'SIZE', text: '720pt × 405pt', color: colors.neonBlue },
  { label: 'MARGIN', text: '≥ 36pt', color: colors.neonPurple },
  { label: 'CSS', text: 'No Gradient', color: colors.neonPink },
  { label: 'BORDER', text: 'Text No Border', color: colors.neonCyan },
  { label: 'COORD', text: 'inch = pt / 72', color: colors.neonBlue },
  { label: 'WIDTH', text: 'Total < 720pt', color: colors.neonPurple }
];

const cW = 2.6;
const cGapX = 0.35;
const cGapY = 0.35;

constraints.forEach((c, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.8 + col * (cW + cGapX);
  const y = 1.5 + row * (1.4 + cGapY);
  
  // 霓虹边框卡片
  slide4.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: cW, h: 1.4,
    fill: { color: colors.glass, transparency: 95 },
    line: { color: c.color, width: 1 }
  });
  
  // 顶部霓虹条
  slide4.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: cW, h: 0.04,
    fill: { color: c.color }
  });
  
  // 英文标签
  slide4.addText(c.label, {
    x: x + 0.2, y: y + 0.2, w: 2.3, h: 0.3,
    fontSize: 14, color: c.color, bold: true,
    fontFace: 'Arial'
  });
  
  // 内容
  slide4.addText(c.text, {
    x: x + 0.2, y: y + 0.6, w: 2.3, h: 0.6,
    fontSize: 14, color: colors.text,
    fontFace: 'Microsoft YaHei'
  });
});

// ========== 第5页：结尾 - 霓虹大字 ==========
let slide5 = pres.addSlide();
slide5.background = { color: colors.bg };

// 背景装饰
slide5.addShape(pres.ShapeType.ellipse, {
  x: -1.5, y: 3, w: 5, h: 5,
  fill: { color: colors.neonPurple, transparency: 90 }
});
slide5.addShape(pres.ShapeType.ellipse, {
  x: 8, y: -1, w: 4, h: 4,
  fill: { color: colors.neonBlue, transparency: 92 }
});

slide5.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 0.05,
  fill: { color: colors.neonBlue }
});

slide5.addText('开始使用', {
  x: 0, y: 1.6, w: 10, h: 1,
  fontSize: 64, color: colors.text, bold: true, align: 'center',
  fontFace: 'Microsoft YaHei'
});
slide5.addText('pptx', {
  x: 0, y: 2.5, w: 10, h: 1,
  fontSize: 72, color: colors.neonBlue, bold: true, align: 'center',
  fontFace: 'Arial Black'
});

slide5.addShape(pres.ShapeType.rect, {
  x: 3.5, y: 3.5, w: 3, h: 0.05,
  fill: { color: colors.neonPink }
});

slide5.addText('Create Professional Presentations', {
  x: 0, y: 3.7, w: 10, h: 0.5,
  fontSize: 16, color: colors.textMuted, align: 'center',
  fontFace: 'Microsoft YaHei'
});

// 保存
pres.writeFile({ fileName: 'pptx技能演示.pptx' })
  .then(() => console.log('PPT 演示文件生成成功！'))
  .catch(err => console.error('生成失败:', err));
