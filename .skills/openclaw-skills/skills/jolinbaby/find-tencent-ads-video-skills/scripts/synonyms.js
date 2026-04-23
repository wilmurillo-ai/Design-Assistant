#!/usr/bin/env node

/**
 * 同义词扩展模块
 * 用于在搜索结果不足时自动扩展搜索关键词
 */

// 关键词同义词映射表
const SYNONYMS = {
  '防晒衣': ['防晒', '防晒衫', '防晒服', '冰袖', '遮阳帽', '遮阳伞', '防晒袖套'],
  '美妆': ['化妆品', '护肤品', '彩妆', '口红', '粉底', '眉笔'],
  '零食': ['小吃', '坚果', '饼干', '糖果', '巧克力', '薯片'],
  '奶粉': ['婴儿奶粉', '儿童奶粉', '驼奶粉', '牛奶'],
  '汽车': ['行车记录仪', '车载支架', '汽车用品', '车衣'],
  '血压计': ['血压仪', '电子血压计', '家用血压仪', '测血压'],
  '手机': ['手机壳', '充电器', '数据线', '手机膜'],
  '服装': ['衣服', '裙子', 'T恤', '裤子', '外套'],
  '食品': ['美食', '特产', '有机食品', '健康食品'],
  '数码': ['电子产品', '电脑', '平板', '耳机']
};

/**
 * 获取关键词的同义词列表
 */
function getSynonyms(keyword) {
  // 精确匹配
  if (SYNONYMS[keyword]) {
    return SYNONYMS[keyword];
  }
  
  // 模糊匹配：检查关键词是否包含某个key
  for (const [key, values] of Object.entries(SYNONYMS)) {
    if (keyword.includes(key) || key.includes(keyword)) {
      return values;
    }
  }
  
  // 返回通用扩展词
  return getGeneral扩展(keyword);
}

/**
 * 获取通用扩展词
 */
function getGeneral扩展(keyword) {
  // 根据关键词最后一个字进行简单扩展
  const lastChar = keyword.slice(-1);
  const extensions = {
    '衣': ['衫', '服', '裤', '裙', '外套'],
    '鞋': ['袜', '垫'],
    '帽': ['伞', '巾', '袖'],
    '妆': ['品', '护肤', '美容'],
    '食': ['品', '饮料', '零食'],
    '品': ['商品', '好物']
  };
  
  if (extensions[lastChar]) {
    return extensions[lastChar].map(ext => keyword + ext);
  }
  
  return [];
}

/**
 * 扩展搜索关键词
 */
function expandKeyword(keyword) {
  const synonyms = getSynonyms(keyword);
  return [keyword, ...synonyms];
}

module.exports = {
  SYNONYMS,
  getSynonyms,
  expandKeyword
};
