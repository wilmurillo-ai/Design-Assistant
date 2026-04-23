/**
 * PPT Insight Generator - 专业级技术洞察演示文稿生成器
 * 
 * 设计风格：深红色主题 (#8B0000) + 白色背景
 * 特点：每页有核心观点、数据可视化、对比统计
 */

const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

// ========== 配色方案 ==========
const COLORS = {
  // 主色调 - 深红色系
  primary: '8B0000',        // 深红色 (主色)
  primaryLight: 'A52A2A',   // 亮深红
  secondary: 'C41E3A',      // 亮红色 (辅助色)
  accent: 'D4AF37',         // 金色 (强调色)
  
  // 中性色
  white: 'FFFFFF',
  black: '000000',
  darkGray: '1A1A1A',       // 文字主色
  mediumGray: '666666',     // 文字辅色
  lightGray: 'F5F5F5',      // 浅色背景
  borderGray: 'DDDDDD',     // 边框色
  
  // 功能色
  success: '2E7D32',        // 绿色 (增长/正面)
  warning: 'F57C00',        // 橙色 (警告)
  info: '1976D2'            // 蓝色 (信息)
};

// ========== 字体配置 ==========
const FONTS = {
  title: 'Arial Black',
  heading: 'Arial',
  body: 'Calibri',
  data: 'Calibri'
};

// ========== 尺寸配置 ==========
const LAYOUT = {
  slideWidth: 10,    // 16:9 比例
  slideHeight: 5.625,
  margin: 0.5,
  spacing: 0.3
};

/**
 * 创建演示文稿
 */
function createPresentation(config) {
  const pres = new PptxGenJS();
  
  // 设置演示文稿属性
  pres.layout = 'LAYOUT_16x9';
  pres.title = config.title || '技术洞察报告';
  pres.author = config.author || 'PPT Insight Generator';
  pres.company = config.company || '';
  pres.subject = config.subtitle || '';
  
  return pres;
}

/**
 * 添加封面页
 */
function addTitleSlide(pres, config) {
  const slide = pres.addSlide();
  
  // 白色背景
  slide.background = { color: COLORS.white };
  
  // 顶部深红色装饰条
  slide.addShape(pres.ShapeType.rect, {
    x: 0, y: 0, w: '100%', h: 0.4,
    fill: { color: COLORS.primary }
  });
  
  // 主标题
  slide.addText(config.title || '技术洞察报告', {
    x: LAYOUT.margin,
    y: 1.2,
    w: '90%',
    h: 1.5,
    fontSize: 52,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.title,
    align: 'left'
  });
  
  // 副标题
  if (config.subtitle) {
    slide.addText(config.subtitle, {
      x: LAYOUT.margin,
      y: 2.5,
      w: '90%',
      h: 0.8,
      fontSize: 24,
      color: COLORS.darkGray,
      fontFace: FONTS.heading,
      align: 'left'
    });
  }
  
  // 底部信息
  const bottomY = 4.5;
  
  // 底部深红色线条
  slide.addShape(pres.ShapeType.rect, {
    x: LAYOUT.margin,
    y: bottomY - 0.1,
    w: 2,
    h: 0.08,
    fill: { color: COLORS.primary }
  });
  
  // 日期
  slide.addText(config.date || new Date().toLocaleDateString('zh-CN'), {
    x: LAYOUT.margin + 2.3,
    y: bottomY,
    w: 3,
    h: 0.3,
    fontSize: 14,
    color: COLORS.mediumGray,
    fontFace: FONTS.body
  });
  
  // 作者/机构
  if (config.author) {
    slide.addText(config.author, {
      x: LAYOUT.margin,
      y: bottomY + 0.4,
      w: 6,
      h: 0.3,
      fontSize: 12,
      color: COLORS.mediumGray,
      fontFace: FONTS.body
    });
  }
  
  return slide;
}

/**
 * 添加目录页
 */
function addAgendaSlide(pres, sections) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText('目录', {
    x: LAYOUT.margin,
    y: 0.4,
    w: '90%',
    h: 0.6,
    fontSize: 36,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.title
  });
  
  // 目录项
  sections.forEach((section, idx) => {
    const y = 1.4 + idx * 0.9;
    
    // 序号背景圆
    slide.addShape(pres.ShapeType.ellipse, {
      x: LAYOUT.margin,
      y: y + 0.1,
      w: 0.5,
      h: 0.5,
      fill: { color: idx === 0 ? COLORS.primary : COLORS.lightGray },
      line: { color: idx === 0 ? COLORS.white : COLORS.borderGray, width: 1 }
    });
    
    // 序号
    slide.addText(String(idx + 1), {
      x: LAYOUT.margin + 0.15,
      y: y + 0.2,
      w: 0.2,
      h: 0.3,
      fontSize: 16,
      color: idx === 0 ? COLORS.white : COLORS.mediumGray,
      bold: true,
      fontFace: FONTS.heading,
      align: 'center'
    });
    
    // 标题
    slide.addText(section.title, {
      x: LAYOUT.margin + 0.7,
      y: y + 0.15,
      w: 7,
      h: 0.4,
      fontSize: 20,
      color: COLORS.darkGray,
      bold: true,
      fontFace: FONTS.heading
    });
    
    // 描述
    if (section.description) {
      slide.addText(section.description, {
        x: LAYOUT.margin + 0.7,
        y: y + 0.55,
        w: 7,
        h: 0.3,
        fontSize: 13,
        color: COLORS.mediumGray,
        fontFace: FONTS.body
      });
    }
  });
  
  return slide;
}

/**
 * 添加核心观点页 - 单页一个核心洞察
 */
function addInsightSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText(config.title || '核心洞察', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 28,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading
  });
  
  // 核心观点框
  const boxY = 1.0;
  slide.addShape(pres.ShapeType.rect, {
    x: LAYOUT.margin,
    y: boxY,
    w: '90%',
    h: 1.5,
    fill: { color: COLORS.primary + '10' }, // 10% 透明度
    line: { color: COLORS.primary, width: 3 }
  });
  
  // 核心观点文字
  slide.addText(config.statement || '', {
    x: LAYOUT.margin + 0.4,
    y: boxY + 0.3,
    w: '86%',
    h: 1.0,
    fontSize: 22,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading,
    align: 'center'
  });
  
  // 证据/支持点
  if (config.evidence && config.evidence.length > 0) {
    const evidenceY = boxY + 1.7;
    slide.addText('关键证据', {
      x: LAYOUT.margin,
      y: evidenceY,
      w: '90%',
      h: 0.3,
      fontSize: 14,
      color: COLORS.mediumGray,
      bold: true,
      fontFace: FONTS.body
    });
    
    config.evidence.forEach((item, idx) => {
      slide.addText('• ' + item, {
        x: LAYOUT.margin + 0.3,
        y: evidenceY + 0.35 + idx * 0.4,
        w: '87%',
        h: 0.35,
        fontSize: 14,
        color: COLORS.darkGray,
        fontFace: FONTS.body
      });
    });
  }
  
  // 影响/建议
  if (config.implication) {
    const implY = config.evidence ? 3.5 : 2.8;
    slide.addShape(pres.ShapeType.rect, {
      x: LAYOUT.margin,
      y: implY,
      w: '90%',
      h: 0.9,
      fill: { color: COLORS.lightGray },
      line: { color: COLORS.borderGray, width: 1 }
    });
    
    slide.addText('💡 影响与建议：' + config.implication, {
      x: LAYOUT.margin + 0.3,
      y: implY + 0.15,
      w: '86%',
      h: 0.6,
      fontSize: 13,
      color: COLORS.darkGray,
      fontFace: FONTS.body
    });
  }
  
  return slide;
}

/**
 * 添加数据对比页 - 柱状图对比
 */
function addComparisonSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText(config.title || '数据对比', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 28,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading
  });
  
  // 副标题/说明
  if (config.subtitle) {
    slide.addText(config.subtitle, {
      x: LAYOUT.margin,
      y: 0.75,
      w: '90%',
      h: 0.25,
      fontSize: 14,
      color: COLORS.mediumGray,
      fontFace: FONTS.body
    });
  }
  
  const chartY = 1.2;
  const chartHeight = 2.5;
  const barWidth = 0.8;
  const gap = 0.4;
  const maxValue = Math.max(...config.items.map(i => i.value)) * 1.2;
  
  // 绘制柱状图
  config.items.forEach((item, idx) => {
    const x = LAYOUT.margin + 0.5 + idx * (barWidth + gap);
    const barHeight = (item.value / maxValue) * chartHeight;
    
    // 柱子
    slide.addShape(pres.ShapeType.rect, {
      x: x,
      y: chartY + chartHeight - barHeight,
      w: barWidth,
      h: barHeight,
      fill: { color: item.color || COLORS.primary },
      line: { color: item.color || COLORS.primary, width: 0 }
    });
    
    // 数值标签
    slide.addText(item.value.toLocaleString(), {
      x: x,
      y: chartY + chartHeight - barHeight - 0.3,
      w: barWidth,
      h: 0.25,
      fontSize: 14,
      color: COLORS.darkGray,
      bold: true,
      fontFace: FONTS.data,
      align: 'center'
    });
    
    // 类别标签
    slide.addText(item.name, {
      x: x,
      y: chartY + chartHeight + 0.15,
      w: barWidth,
      h: 0.3,
      fontSize: 12,
      color: COLORS.mediumGray,
      fontFace: FONTS.body,
      align: 'center'
    });
  });
  
  // Y 轴
  slide.addShape(pres.ShapeType.line, {
    x: LAYOUT.margin + 0.3,
    y: chartY,
    w: 0,
    h: chartHeight,
    line: { color: COLORS.borderGray, width: 1 }
  });
  
  // X 轴
  slide.addShape(pres.ShapeType.line, {
    x: LAYOUT.margin + 0.3,
    y: chartY + chartHeight,
    w: config.items.length * (barWidth + gap),
    h: 0,
    line: { color: COLORS.borderGray, width: 1 }
  });
  
  // 关键洞察框
  if (config.insight) {
    const insightY = chartY + chartHeight + 0.8;
    slide.addShape(pres.ShapeType.rect, {
      x: LAYOUT.margin,
      y: insightY,
      w: '90%',
      h: 0.8,
      fill: { color: COLORS.accent + '15' },
      line: { color: COLORS.accent, width: 2 }
    });
    
    slide.addText('🔍 关键洞察：' + config.insight, {
      x: LAYOUT.margin + 0.3,
      y: insightY + 0.15,
      w: '86%',
      h: 0.5,
      fontSize: 13,
      color: COLORS.darkGray,
      fontFace: FONTS.body
    });
  }
  
  return slide;
}

/**
 * 添加趋势分析页 - 折线图
 */
function addTrendSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText(config.title || '趋势分析', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 28,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading
  });
  
  const chartY = 1.2;
  const chartHeight = 2.5;
  const chartWidth = 8;
  const points = config.dataPoints || [];
  
  if (points.length < 2) {
    slide.addText('数据点不足，无法绘制趋势图', {
      x: LAYOUT.margin,
      y: chartY,
      w: '90%',
      h: 0.5,
      fontSize: 14,
      color: COLORS.mediumGray,
      fontFace: FONTS.body
    });
    return slide;
  }
  
  const maxValue = Math.max(...points.map(p => p.value)) * 1.15;
  const minX = LAYOUT.margin + 0.5;
  const stepX = (chartWidth - 1) / (points.length - 1);
  
  // 绘制网格线
  for (let i = 0; i <= 4; i++) {
    const y = chartY + (i / 4) * chartHeight;
    slide.addShape(pres.ShapeType.line, {
      x: minX,
      y: y,
      w: chartWidth - 0.5,
      h: 0,
      line: { color: COLORS.borderGray, width: 0.5, dash: 'dash' }
    });
  }
  
  // 绘制折线
  let linePoints = '';
  points.forEach((point, idx) => {
    const x = minX + idx * stepX;
    const y = chartY + chartHeight - (point.value / maxValue) * chartHeight;
    
    if (idx === 0) {
      linePoints = `${x},${y}`;
    } else {
      linePoints += ` ${x},${y}`;
    }
    
    // 数据点
    slide.addShape(pres.ShapeType.ellipse, {
      x: x - 0.08,
      y: y - 0.08,
      w: 0.16,
      h: 0.16,
      fill: { color: COLORS.primary },
      line: { color: COLORS.white, width: 2 }
    });
    
    // 数值标签
    slide.addText(point.value.toLocaleString(), {
      x: x - 0.4,
      y: y - 0.35,
      w: 0.8,
      h: 0.25,
      fontSize: 11,
      color: COLORS.primary,
      bold: true,
      fontFace: FONTS.data,
      align: 'center'
    });
    
    // X 轴标签
    slide.addText(point.label, {
      x: x - 0.4,
      y: chartY + chartHeight + 0.15,
      w: 0.8,
      h: 0.25,
      fontSize: 11,
      color: COLORS.mediumGray,
      fontFace: FONTS.body,
      align: 'center'
    });
  });
  
  // 绘制折线（使用多个短线段模拟）
  for (let i = 0; i < points.length - 1; i++) {
    const x1 = minX + i * stepX;
    const y1 = chartY + chartHeight - (points[i].value / maxValue) * chartHeight;
    const x2 = minX + (i + 1) * stepX;
    const y2 = chartY + chartHeight - (points[i + 1].value / maxValue) * chartHeight;
    
    // 计算线段长度和角度
    const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
    
    slide.addShape(pres.ShapeType.line, {
      x: x1,
      y: y1,
      w: length,
      h: 0,
      line: { color: COLORS.primary, width: 2 },
      rotate: angle
    });
  }
  
  // Y 轴
  slide.addShape(pres.ShapeType.line, {
    x: minX - 0.2,
    y: chartY,
    w: 0,
    h: chartHeight,
    line: { color: COLORS.borderGray, width: 1 }
  });
  
  // X 轴
  slide.addShape(pres.ShapeType.line, {
    x: minX - 0.2,
    y: chartY + chartHeight,
    w: chartWidth - 0.3,
    h: 0,
    line: { color: COLORS.borderGray, width: 1 }
  });
  
  // 增长率标注
  if (points.length >= 2) {
    const growth = ((points[points.length - 1].value - points[0].value) / points[0].value * 100).toFixed(1);
    const growthColor = growth > 0 ? COLORS.success : growth < 0 ? COLORS.secondary : COLORS.mediumGray;
    
    slide.addShape(pres.ShapeType.rect, {
      x: '70%',
      y: 0.3,
      w: 2.5,
      h: 0.5,
      fill: { color: growthColor + '15' },
      line: { color: growthColor, width: 1 }
    });
    
    slide.addText(`${growth > 0 ? '📈' : '📉'} 总增长率：${Math.abs(growth)}%`, {
      x: '70%',
      y: 0.35,
      w: 2.4,
      h: 0.4,
      fontSize: 13,
      color: growthColor,
      bold: true,
      fontFace: FONTS.body,
      align: 'center'
    });
  }
  
  return slide;
}

/**
 * 添加占比分析页 - 环形图
 */
function addBreakdownSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText(config.title || '占比分析', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 28,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading
  });
  
  const chartX = 2.5;
  const chartY = 1.5;
  const radius = 1.8;
  const items = config.items || [];
  
  // 计算总和
  const total = items.reduce((sum, item) => sum + item.value, 0);
  
  // 绘制环形图（使用多个 arc 形状）
  let startAngle = 0;
  
  items.forEach((item, idx) => {
    const percentage = item.value / total;
    const angle = percentage * 360;
    
    // 环形扇区（用厚边框的圆模拟）
    // 由于 pptxgenjs 不支持真正的 arc，我们用彩色矩形图例替代
  });
  
  // 绘制图例和百分比（替代环形图）
  let legendY = 1.3;
  
  items.forEach((item, idx) => {
    const percentage = ((item.value / total) * 100).toFixed(1);
    const x = LAYOUT.margin;
    
    // 颜色块
    slide.addShape(pres.ShapeType.rect, {
      x: x,
      y: legendY,
      w: 0.4,
      h: 0.4,
      fill: { color: item.color || COLORS.primary },
      line: { color: item.color || COLORS.primary, width: 0 }
    });
    
    // 类别名称
    slide.addText(item.name, {
      x: x + 0.5,
      y: legendY + 0.05,
      w: 3,
      h: 0.3,
      fontSize: 14,
      color: COLORS.darkGray,
      bold: true,
      fontFace: FONTS.body
    });
    
    // 数值
    slide.addText(item.value.toLocaleString(), {
      x: x + 4,
      y: legendY + 0.05,
      w: 1.5,
      h: 0.3,
      fontSize: 14,
      color: COLORS.mediumGray,
      fontFace: FONTS.data,
      align: 'right'
    });
    
    // 百分比（放大显示）
    slide.addText(percentage + '%', {
      x: x + 5.7,
      y: legendY + 0.02,
      w: 1.5,
      h: 0.35,
      fontSize: 18,
      color: item.color || COLORS.primary,
      bold: true,
      fontFace: FONTS.heading,
      align: 'right'
    });
    
    // 进度条背景
    slide.addShape(pres.ShapeType.rect, {
      x: x,
      y: legendY + 0.45,
      w: 7.5,
      h: 0.08,
      fill: { color: COLORS.lightGray },
      line: { color: COLORS.borderGray, width: 0 }
    });
    
    // 进度条填充
    slide.addShape(pres.ShapeType.rect, {
      x: x,
      y: legendY + 0.45,
      w: 7.5 * (percentage / 100),
      h: 0.08,
      fill: { color: item.color || COLORS.primary },
      line: { color: item.color || COLORS.primary, width: 0 }
    });
    
    legendY += 0.7;
  });
  
  // 总计
  const totalY = legendY + 0.2;
  slide.addShape(pres.ShapeType.rect, {
    x: LAYOUT.margin,
    y: totalY,
    w: 7.5,
    h: 0.5,
    fill: { color: COLORS.lightGray },
    line: { color: COLORS.borderGray, width: 1 }
  });
  
  slide.addText(`总计：${total.toLocaleString()}`, {
    x: LAYOUT.margin + 0.3,
    y: totalY + 0.1,
    w: 6.9,
    h: 0.3,
    fontSize: 14,
    color: COLORS.darkGray,
    bold: true,
    fontFace: FONTS.body,
    align: 'center'
  });
  
  // 关键洞察
  if (config.insight) {
    slide.addText('💡 ' + config.insight, {
      x: LAYOUT.margin,
      y: totalY + 0.65,
      w: '90%',
      h: 0.4,
      fontSize: 12,
      color: COLORS.mediumGray,
      italic: true,
      fontFace: FONTS.body
    });
  }
  
  return slide;
}

/**
 * 添加数据卡片页 - 关键指标展示
 */
function addMetricsSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText(config.title || '关键指标', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 28,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.heading
  });
  
  const metrics = config.metrics || [];
  const cols = Math.min(4, metrics.length);
  const rows = Math.ceil(metrics.length / cols);
  
  metrics.forEach((metric, idx) => {
    const col = idx % cols;
    const row = Math.floor(idx / cols);
    const x = LAYOUT.margin + col * (2.3);
    const y = 1.1 + row * 1.8;
    
    // 卡片背景
    slide.addShape(pres.ShapeType.roundRect, {
      x: x,
      y: y,
      w: 2.1,
      h: 1.5,
      fill: { color: COLORS.lightGray },
      line: { color: idx === 0 ? COLORS.primary : COLORS.borderGray, width: idx === 0 ? 2 : 1 },
      rectRadius: 0.15
    });
    
    // 指标名称
    slide.addText(metric.label, {
      x: x + 0.2,
      y: y + 0.15,
      w: 1.7,
      h: 0.3,
      fontSize: 12,
      color: COLORS.mediumGray,
      fontFace: FONTS.body,
      align: 'center'
    });
    
    // 主要数值（放大）
    slide.addText(metric.value, {
      x: x + 0.2,
      y: y + 0.45,
      w: 1.7,
      h: 0.5,
      fontSize: 32,
      color: idx === 0 ? COLORS.primary : COLORS.darkGray,
      bold: true,
      fontFace: FONTS.title,
      align: 'center'
    });
    
    // 变化率/单位
    if (metric.change) {
      const changeColor = metric.change.startsWith('+') ? COLORS.success : 
                         metric.change.startsWith('-') ? COLORS.secondary : COLORS.mediumGray;
      slide.addText(metric.change, {
        x: x + 0.2,
        y: y + 0.95,
        w: 1.7,
        h: 0.25,
        fontSize: 14,
        color: changeColor,
        bold: true,
        fontFace: FONTS.body,
        align: 'center'
      });
    }
    
    // 补充说明
    if (metric.description) {
      slide.addText(metric.description, {
        x: x + 0.2,
        y: y + 1.2,
        w: 1.7,
        h: 0.25,
        fontSize: 10,
        color: COLORS.mediumGray,
        fontFace: FONTS.body,
        align: 'center'
      });
    }
  });
  
  return slide;
}

/**
 * 添加总结页
 */
function addSummarySlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 页面标题
  slide.addText('核心总结', {
    x: LAYOUT.margin,
    y: 0.3,
    w: '90%',
    h: 0.5,
    fontSize: 36,
    color: COLORS.primary,
    bold: true,
    fontFace: FONTS.title
  });
  
  // 总结要点
  const points = config.points || [];
  
  points.forEach((point, idx) => {
    const y = 1.3 + idx * 0.9;
    
    // 序号圆圈
    slide.addShape(pres.ShapeType.ellipse, {
      x: LAYOUT.margin,
      y: y + 0.1,
      w: 0.5,
      h: 0.5,
      fill: { color: COLORS.primary },
      line: { color: COLORS.white, width: 2 }
    });
    
    // 序号
    slide.addText(String(idx + 1), {
      x: LAYOUT.margin + 0.15,
      y: y + 0.2,
      w: 0.2,
      h: 0.3,
      fontSize: 16,
      color: COLORS.white,
      bold: true,
      fontFace: FONTS.heading,
      align: 'center'
    });
    
    // 要点内容
    slide.addText(point, {
      x: LAYOUT.margin + 0.7,
      y: y + 0.15,
      w: '82%',
      h: 0.5,
      fontSize: 16,
      color: COLORS.darkGray,
      fontFace: FONTS.body
    });
  });
  
  // 底部行动建议
  if (config.callToAction) {
    const actionY = 1.3 + points.length * 0.9 + 0.3;
    
    slide.addShape(pres.ShapeType.rect, {
      x: LAYOUT.margin,
      y: actionY,
      w: '90%',
      h: 0.9,
      fill: { color: COLORS.accent + '20' },
      line: { color: COLORS.accent, width: 2 }
    });
    
    slide.addText('🎯 行动建议：' + config.callToAction, {
      x: LAYOUT.margin + 0.4,
      y: actionY + 0.15,
      w: '86%',
      h: 0.6,
      fontSize: 14,
      color: COLORS.darkGray,
      fontFace: FONTS.body
    });
  }
  
  return slide;
}

/**
 * 添加结束页
 */
function addClosingSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.primary };
  
  // 主文字
  slide.addText('谢谢！', {
    x: LAYOUT.margin,
    y: 1.2,
    w: '90%',
    h: 1.2,
    fontSize: 64,
    color: COLORS.white,
    bold: true,
    fontFace: FONTS.title,
    align: 'center'
  });
  
  slide.addText('Q & A', {
    x: LAYOUT.margin,
    y: 2.2,
    w: '90%',
    h: 0.8,
    fontSize: 40,
    color: COLORS.white,
    bold: true,
    fontFace: FONTS.heading,
    align: 'center'
  });
  
  // 副标题
  if (config.title) {
    slide.addText(config.title, {
      x: LAYOUT.margin,
      y: 3.0,
      w: '90%',
      h: 0.4,
      fontSize: 18,
      color: COLORS.white,
      fontFace: FONTS.body,
      align: 'center'
    });
  }
  
  // 联系方式/参考资料
  const contactY = 3.8;
  
  if (config.contact || config.references) {
    slide.addShape(pres.ShapeType.rect, {
      x: 1.5,
      y: contactY,
      w: 7,
      h: 1.3,
      fill: { color: COLORS.white + '15' },
      line: { color: COLORS.white + '40', width: 1 }
    });
    
    let textY = contactY + 0.2;
    
    if (config.contact) {
      slide.addText('📧 ' + config.contact, {
        x: 1.7,
        y: textY,
        w: 6.6,
        h: 0.3,
        fontSize: 13,
        color: COLORS.white,
        fontFace: FONTS.body
      });
      textY += 0.35;
    }
    
    if (config.references && config.references.length > 0) {
      slide.addText('📚 参考资料', {
        x: 1.7,
        y: textY,
        w: 6.6,
        h: 0.25,
        fontSize: 12,
        color: COLORS.accent,
        bold: true,
        fontFace: FONTS.body
      });
      textY += 0.3;
      
      config.references.forEach((ref, idx) => {
        slide.addText('• ' + ref, {
          x: 1.7,
          y: textY + idx * 0.25,
          w: 6.6,
          h: 0.23,
          fontSize: 11,
          color: COLORS.white,
          fontFace: FONTS.body
        });
      });
    }
  }
  
  return slide;
}

/**
 * 主函数 - 生成完整演示文稿
 */
function generateInsightPPT(config) {
  console.log('🎨 开始生成技术洞察 PPT...');
  console.log(`   主题：${config.title}`);
  console.log(`   输出：${config.output || 'insight_presentation.pptx'}`);
  
  const pres = createPresentation(config);
  
  // 1. 封面页
  addTitleSlide(pres, config);
  
  // 2. 目录页
  if (config.sections && config.sections.length > 0) {
    const agendaSections = config.sections.map(s => ({
      title: s.title,
      description: s.description || ''
    }));
    addAgendaSlide(pres, agendaSections);
  }
  
  // 3. 遍历生成各节内容
  if (config.sections) {
    config.sections.forEach((section, idx) => {
      console.log(`   生成章节 ${idx + 1}/${config.sections.length}: ${section.title}`);
      
      switch (section.type) {
        case 'insight':
          addInsightSlide(pres, section);
          break;
        case 'comparison':
          addComparisonSlide(pres, section);
          break;
        case 'trend':
          addTrendSlide(pres, section);
          break;
        case 'breakdown':
          addBreakdownSlide(pres, section);
          break;
        case 'metrics':
          addMetricsSlide(pres, section);
          break;
        case 'summary':
          addSummarySlide(pres, section);
          break;
        default:
          // 默认为洞察页
          addInsightSlide(pres, section);
      }
    });
  }
  
  // 4. 总结页
  if (config.summary) {
    addSummarySlide(pres, config.summary);
  }
  
  // 5. 结束页
  addClosingSlide(pres, {
    title: config.title,
    contact: config.contact,
    references: config.references
  });
  
  // 保存文件
  const outputPath = config.output || 'insight_presentation.pptx';
  pres.writeFile({ fileName: outputPath })
    .then(fileName => {
      console.log(`✅ PPT 生成成功：${fileName}`);
      console.log(`   总页数：${pres.slides.length}`);
    })
    .catch(err => {
      console.error('❌ PPT 生成失败:', err);
      process.exit(1);
    });
}

// ========== 命令行接口 ==========
if (require.main === module) {
  const args = process.argv.slice(2);
  
  // 解析命令行参数
  const config = {
    title: '技术洞察报告',
    subtitle: '',
    author: 'PPT Insight Generator',
    date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' }),
    output: 'insight_presentation.pptx',
    sections: [],
    summary: null,
    contact: '',
    references: []
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--topic' && args[i + 1]) {
      config.title = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      config.output = args[++i];
    } else if (args[i] === '--content' && args[i + 1]) {
      try {
        const contentConfig = JSON.parse(args[++i]);
        Object.assign(config, contentConfig);
      } catch (e) {
        console.error('无效的 JSON 内容配置');
        process.exit(1);
      }
    } else if (args[i] === '--help' || args[i] === '-h') {
      console.log(`
PPT Insight Generator - 专业级技术洞察演示文稿生成器

用法:
  node generate_insight_ppt.js [选项]

选项:
  --topic <主题>       PPT 主题名称
  --output <文件名>    输出文件名 (默认：insight_presentation.pptx)
  --content <JSON>     JSON 格式的内容配置
  --help, -h          显示帮助信息

示例:
  node generate_insight_ppt.js --topic "AI 基础设施" --output "ai_report.pptx"
  
  node generate_insight_ppt.js --content '{"title":"示例","sections":[...]}'

配色方案:
  主色：深红色 (#8B0000)
  背景：白色 (#FFFFFF)
  强调：金色 (#D4AF37)
      `);
      process.exit(0);
    }
  }
  
  // 如果没有提供内容，使用示例内容
  if (config.sections.length === 0) {
    config.sections = [
      {
        type: 'insight',
        title: '技术趋势洞察',
        statement: 'AI 基础设施正在从集中式向分布式架构演进',
        evidence: [
          '单 GPU 已无法满足大模型推理需求',
          '多节点分布式推理成为主流方案',
          '分离式架构可提升 50% 吞吐量'
        ],
        implication: '企业需要重新评估现有基础设施，为分布式架构做准备'
      },
      {
        type: 'metrics',
        title: '关键性能指标',
        metrics: [
          { label: '吞吐量提升', value: '50x', change: '+4800%', description: 'vs 传统架构' },
          { label: '成本降低', value: '35%', change: '-35%', description: '单位推理成本' },
          { label: '延迟优化', value: '2.3x', change: '+130%', description: 'P99 延迟' },
          { label: '资源利用率', value: '85%', change: '+45%', description: 'GPU 利用率' }
        ]
      },
      {
        type: 'comparison',
        title: '架构对比分析',
        subtitle: '传统架构 vs 分布式架构性能对比',
        items: [
          { name: '传统架构', value: 100, color: COLORS.mediumGray },
          { name: '分布式架构', value: 500, color: COLORS.primary },
          { name: '优化后', value: 650, color: COLORS.accent }
        ],
        insight: '分布式架构带来 5 倍性能提升，优化后可达 6.5 倍'
      },
      {
        type: 'trend',
        title: '市场增长趋势',
        dataPoints: [
          { label: '2023', value: 45 },
          { label: '2024', value: 68 },
          { label: '2025', value: 92 },
          { label: '2026E', value: 135 }
        ]
      },
      {
        type: 'breakdown',
        title: '成本结构分析',
        items: [
          { name: 'GPU 计算', value: 450, color: COLORS.primary },
          { name: '内存存储', value: 180, color: COLORS.secondary },
          { name: '网络传输', value: 120, color: COLORS.accent },
          { name: '运维管理', value: 90, color: COLORS.info }
        ],
        insight: '计算资源占主导，优化 GPU 利用率是降本关键'
      },
      {
        type: 'insight',
        title: '战略建议',
        statement: '分三阶段推进基础设施升级',
        evidence: [
          '第一阶段：评估现有系统瓶颈',
          '第二阶段：试点分布式架构',
          '第三阶段：全面迁移和优化'
        ],
        implication: '预计 12-18 个月完成转型，投资回报率可达 300%'
      }
    ];
    
    config.summary = {
      points: [
        '分布式架构是 AI 基础设施的必然趋势',
        '性能提升 5-6 倍，成本降低 35%',
        '建议分三阶段推进，12-18 个月完成转型'
      ],
      callToAction: '立即启动基础设施评估，制定详细的迁移路线图'
    };
    
    config.references = [
      'NVIDIA Dynamo Technical Report 2026',
      'AI Infrastructure Benchmark Study',
      'Industry Analysis Report Q1 2026'
    ];
  }
  
  generateInsightPPT(config);
}

module.exports = {
  generateInsightPPT,
  addTitleSlide,
  addInsightSlide,
  addComparisonSlide,
  addTrendSlide,
  addBreakdownSlide,
  addMetricsSlide,
  COLORS,
  FONTS
};
