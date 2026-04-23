/**
 * Cart Optimizer - 凑单优化器
 * 核心算法实现
 */

class CartOptimizer {
  /**
   * 基础凑单计算
   * @param {number} currentAmount - 当前金额
   * @param {Object} rule - 优惠规则
   * @returns {Object} 凑单方案
   */
  calculate(currentAmount, rule) {
    const { threshold, discount, type = 'fixed' } = rule;
    
    // 已达到门槛
    if (currentAmount >= threshold) {
      return {
        status: 'qualified',
        currentAmount,
        threshold,
        gap: 0,
        discount: this.calculateDiscount(currentAmount, rule),
        finalAmount: currentAmount - this.calculateDiscount(currentAmount, rule),
        message: '已达到优惠门槛'
      };
    }

    // 需要凑单
    const gap = threshold - currentAmount;
    const discountAmount = this.calculateDiscount(threshold, rule);
    const savingRate = discountAmount / gap;

    return {
      status: 'need_more',
      currentAmount,
      threshold,
      gap,
      discount: discountAmount,
      finalAmount: threshold - discountAmount,
      savingRate,
      message: `还差 ¥${gap.toFixed(2)} 可享受 ¥${discountAmount.toFixed(2)} 优惠`,
      recommendation: savingRate > 0.5 
        ? '建议凑单，优惠力度较大'
        : savingRate > 0.3
        ? '可考虑凑单'
        : '凑单性价比一般'
    };
  }

  /**
   * 计算优惠金额
   */
  calculateDiscount(amount, rule) {
    const { discount, type = 'fixed', maxDiscount } = rule;
    
    switch (type) {
      case 'fixed':
        return discount;
      case 'percent':
        const pctDiscount = amount * (discount / 100);
        return maxDiscount ? Math.min(pctDiscount, maxDiscount) : pctDiscount;
      case 'tier':
        // 阶梯优惠，找到适用的档位
        return this.findTierDiscount(amount, rule.tiers);
      default:
        return 0;
    }
  }

  /**
   * 多规则对比
   */
  compareRules(currentAmount, rules) {
    const results = rules.map(rule => ({
      name: rule.name,
      ...this.calculate(currentAmount, rule)
    }));

    // 按最终支付金额排序
    results.sort((a, b) => a.finalAmount - b.finalAmount);

    const best = results[0];
    
    return {
      currentAmount,
      options: results,
      recommendation: best.status === 'qualified' 
        ? `当前已满足「${best.name}」，最终支付 ¥${best.finalAmount.toFixed(2)}`
        : `建议凑单至「${best.name}」，再购 ¥${best.gap.toFixed(2)} 可省 ¥${best.discount.toFixed(2)}`,
      bestOption: best
    };
  }

  /**
   * 从候选商品中选择最优凑单组合
   * @param {number} targetAmount - 目标金额
   * @param {Array} candidates - 候选商品 [{price, name, value}]
   * @param {Object} options - 选项
   */
  findBestCombination(targetAmount, candidates, options = {}) {
    const { tolerance = 10, maxItems = 3 } = options;
    
    // 按性价比排序
    const sorted = candidates
      .filter(c => c.price <= targetAmount + tolerance)
      .sort((a, b) => (b.value || 1) / b.price - (a.value || 1) / a.price);

    // 使用动态规划找最优组合
    const result = this.knapsack(targetAmount, sorted, maxItems);
    
    return {
      targetAmount,
      combination: result.items,
      totalPrice: result.totalPrice,
      gap: targetAmount - result.totalPrice,
      isPerfect: Math.abs(targetAmount - result.totalPrice) <= tolerance,
      alternative: this.findAlternative(targetAmount, sorted, result)
    };
  }

  /**
   * 简化版背包算法
   */
  knapsack(target, items, maxItems) {
    // 限制搜索空间，避免组合爆炸
    const limitedItems = items.slice(0, 20);
    let best = { items: [], totalPrice: 0, totalValue: 0 };

    // 枚举组合（限制数量）
    const enumerate = (start, current, count) => {
      if (count > maxItems) return;
      
      const currentPrice = current.reduce((s, i) => s + i.price, 0);
      const currentValue = current.reduce((s, i) => s + (i.value || 1), 0);
      
      // 更新最优解（最接近目标且不超过目标+容差）
      if (currentPrice <= target + 10 && currentPrice > best.totalPrice) {
        best = {
          items: [...current],
          totalPrice: currentPrice,
          totalValue: currentValue
        };
      }

      for (let i = start; i < limitedItems.length; i++) {
        current.push(limitedItems[i]);
        enumerate(i + 1, current, count + 1);
        current.pop();
      }
    };

    enumerate(0, [], 0);
    return best;
  }

  /**
   * 找备选方案
   */
  findAlternative(target, items, current) {
    // 找一个刚好超过目标的单商品方案
    const over = items.find(i => i.price >= target && i.price <= target * 1.2);
    if (over && (!current.isPerfect || current.gap > 5)) {
      return {
        type: 'single',
        item: over,
        excess: over.price - target,
        message: `或单独购买「${over.name}」¥${over.price}（多付¥${(over.price - target).toFixed(2)}）`
      };
    }
    return null;
  }

  /**
   * 阶梯优惠查找
   */
  findTierDiscount(amount, tiers) {
    // tiers: [{threshold: 200, discount: 20}, {threshold: 300, discount: 40}]
    let applicable = 0;
    for (const tier of tiers) {
      if (amount >= tier.threshold) {
        applicable = Math.max(applicable, tier.discount);
      }
    }
    return applicable;
  }

  /**
   * 生成完整凑单建议
   */
  generateAdvice(cartAmount, rules, candidates = []) {
    // 1. 对比所有优惠规则
    const comparison = this.compareRules(cartAmount, rules);
    
    // 2. 如果需要凑单，找最优组合
    let combination = null;
    if (comparison.bestOption.status === 'need_more' && candidates.length > 0) {
      combination = this.findBestCombination(
        comparison.bestOption.gap,
        candidates,
        { maxItems: 2 }
      );
    }

    return {
      summary: comparison.recommendation,
      currentCart: cartAmount,
      bestRule: comparison.bestOption,
      allOptions: comparison.options,
      combination,
      finalAdvice: this.formatAdvice(comparison, combination)
    };
  }

  formatAdvice(comparison, combination) {
    const lines = [];
    const best = comparison.bestOption;
    
    lines.push(`当前购物车: ¥${comparison.currentAmount.toFixed(2)}`);
    lines.push('');
    
    if (best.status === 'qualified') {
      lines.push(`✅ 已享受「${best.name}」优惠`);
      lines.push(`   优惠金额: ¥${best.discount.toFixed(2)}`);
      lines.push(`   最终支付: ¥${best.finalAmount.toFixed(2)}`);
    } else {
      lines.push(`💡 推荐凑单至「${best.name}」`);
      lines.push(`   需再购: ¥${best.gap.toFixed(2)}`);
      lines.push(`   可优惠: ¥${best.discount.toFixed(2)}`);
      lines.push(`   实付: ¥${best.finalAmount.toFixed(2)}`);
      
      if (combination && combination.combination.length > 0) {
        lines.push('');
        lines.push('推荐凑单品:');
        combination.combination.forEach((item, i) => {
          lines.push(`  ${i + 1}. ${item.name} ¥${item.price}`);
        });
        if (combination.gap > 0) {
          lines.push(`  （还差 ¥${combination.gap.toFixed(2)}，可再选一件小商品）`);
        }
      }
    }
    
    return lines.join('\n');
  }
}

module.exports = { CartOptimizer };
