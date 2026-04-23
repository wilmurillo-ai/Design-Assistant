/**
 * Group Buy Helper - 拼团/砍价助手
 */

const { LocalStore } = require('../../shared/storage/local-store');

class GroupBuyHelper {
  constructor() {
    this.store = new LocalStore('group-buy-helper');
    
    this.platformRules = {
      'pdd': {
        name: '拼多多',
        groupTypes: ['2 人团', '3 人团', '5 人团'],
       砍价: {
          maxHelpers: 20,
          minCutPercent: 0.01,
          maxCutPercent: 5
        }
      },
      'taobao': {
        name: '淘宝',
        groupTypes: ['聚划算', '淘抢购']
      }
    };
  }

  /**
   * 分析砍价活动
   */
  analyzeBargain(activity) {
    const { platform, targetPrice, currentPrice, helpers } = activity;

    if (typeof targetPrice !== 'number' || typeof currentPrice !== 'number') {
      return {
        success: false,
        error: '目标价格和当前价格必须为数字'
      };
    }

    if (targetPrice <= 0) {
      return {
        success: false,
        error: '目标价格必须大于 0'
      };
    }

    const remaining = Math.max(targetPrice - currentPrice, 0);
    const remainingPercent = targetPrice > 0 ? (remaining / targetPrice) * 100 : 0;

    if (remaining === 0) {
      return {
        success: true,
        remaining: 0,
        remainingPercent: '0.00',
        estimatedHelpers: 0,
        successRate: 1,
        recommendation: '已达到目标，无需继续砍价',
        strategy: ['可以截图留存结果，避免活动状态变化', '确认是否还需要在有效期内完成下单'],
        status: 'completed'
      };
    }

    // 估算还需多少人
    const avgCut = Math.max(this.estimateAvgCut(platform, helpers), 0.01);
    const estimatedHelpers = Math.max(Math.ceil(remaining / avgCut), 1);

    // 成功概率
    const successRate = this.calculateSuccessRate(platform, remainingPercent, helpers);

    return {
      success: true,
      remaining,
      remainingPercent: remainingPercent.toFixed(2),
      estimatedHelpers,
      successRate,
      recommendation: this.getBargainAdvice(platform, remainingPercent, successRate),
      strategy: this.getSuggestedStrategy(platform, remainingPercent),
      status: 'active'
    };
  }

  estimateAvgCut(platform, helpers) {
    // 简化估算：前期砍得多，后期砍得少
    if (!helpers || helpers.length === 0) return 10;
    
    const totalCut = helpers.reduce((s, h) => s + h.amount, 0);
    return totalCut / helpers.length;
  }

  calculateSuccessRate(platform, remainingPercent, helpers) {
    const maxHelpers = this.platformRules[platform]?.砍价?.maxHelpers || 20;
    const currentHelpers = helpers?.length || 0;
    
    // 基于剩余百分比和已帮助人数估算
    if (remainingPercent < 5 && currentHelpers > 10) {
      return 0.3; // 最后阶段很难
    }
    if (remainingPercent < 20 && currentHelpers < 5) {
      return 0.8; // 早期阶段容易
    }
    if (remainingPercent > 50) {
      return 0.9; // 刚开始，空间大
    }
    
    return 0.5 + (1 - remainingPercent/100) * 0.3;
  }

  getBargainAdvice(platform, remainingPercent, successRate) {
    if (successRate > 0.7) {
      return '成功率高，建议继续邀请好友助力';
    }
    if (successRate > 0.4) {
      return '有一定难度，但值得一试';
    }
    if (remainingPercent < 5) {
      return '最后阶段非常困难，建议理性决策';
    }
    return '难度较大，建议谨慎投入时间';
  }

  getSuggestedStrategy(platform, remainingPercent) {
    const strategies = [];
    
    if (remainingPercent > 50) {
      strategies.push('前期多邀请活跃好友，快速推进');
    } else if (remainingPercent > 10) {
      strategies.push('中期可以找家人助力，每人能砍不少');
    } else {
      strategies.push('最后阶段建议：1.找新用户助力 2.考虑直接购买 3.不要花钱买助力');
    }
    
    strategies.push('注意：砍价活动有套路，最后 1% 可能需要很多人');
    
    return strategies;
  }

  /**
   * 拼团分析
   */
  analyzeGroupDeal(deal) {
    const { platform, originalPrice, groupPrice, requiredMembers, currentMembers, timeLeft } = deal;
    
    const savings = originalPrice - groupPrice;
    const savingsPercent = (savings / originalPrice) * 100;
    const neededMembers = requiredMembers - currentMembers;
    
    // 成团概率
    const successRate = this.calculateGroupSuccessRate(platform, neededMembers, timeLeft);
    
    return {
      originalPrice,
      groupPrice,
      savings,
      savingsPercent: savingsPercent.toFixed(1),
      neededMembers,
      timeLeft,
      successRate,
      recommendation: this.getGroupAdvice(savingsPercent, successRate, neededMembers),
      alternatives: this.findAlternatives(platform, deal)
    };
  }

  calculateGroupSuccessRate(platform, neededMembers, timeLeft) {
    // 简化估算
    const baseRate = 0.8;
    const timeFactor = timeLeft > 24 ? 1 : timeLeft / 24;
    const memberFactor = neededMembers === 0 ? 1 : 0.9 ** neededMembers;
    
    return Math.min(baseRate * timeFactor * memberFactor, 0.95);
  }

  getGroupAdvice(savingsPercent, successRate, neededMembers) {
    if (neededMembers === 0) {
      return '已成团，立即下单！';
    }
    if (savingsPercent > 30 && successRate > 0.6) {
      return '优惠力度大，成团概率高，值得参与';
    }
    if (savingsPercent > 20) {
      return '优惠不错，可以试试，不成团可退款';
    }
    return '优惠一般，根据需求决定';
  }

  findAlternatives(platform, deal) {
    // 查找同类商品的其他拼团
    return [
      {
        type: '直接购买',
        price: deal.originalPrice,
        note: '无需等待，立即发货'
      },
      {
        type: '其他拼团',
        price: deal.groupPrice * 0.95,
        note: '可能有更优惠的团'
      }
    ];
  }

  /**
   * 生成分享文案
   */
  generateShareText(type, deal) {
    if (type === 'bargain') {
      return `帮我砍一刀！${deal.itemName}
原价¥${deal.originalPrice}，已砍到¥${deal.currentPrice}
还差${((deal.targetPrice-deal.currentPrice)/deal.targetPrice*100).toFixed(1)}%就免费了！
点链接帮我砍一下：${deal.link}`;
    }
    
    if (type === 'group') {
      return `【拼团邀请】${deal.itemName}
原价¥${deal.originalPrice}，拼团价¥${deal.groupPrice}
还差${deal.neededMembers}人成团，快来一起拼！
链接：${deal.link}`;
    }
    
    return '';
  }

  /**
   * 记录活动
   */
  trackActivity(activity) {
    const activities = this.store.get('activities', []);
    activities.push({
      ...activity,
      id: `act_${Date.now()}`,
      createdAt: new Date().toISOString(),
      status: 'active'
    });
    this.store.set('activities', activities);
    return activity;
  }

  /**
   * 检查活动状态
   */
  checkActivities() {
    const activities = this.store.get('activities', []);
    const now = new Date();
    
    const results = activities.map(act => {
      const expiry = new Date(act.expiry);
      const isExpired = now > expiry;
      
      if (isExpired && act.status === 'active') {
        act.status = 'expired';
      }
      
      return {
        ...act,
        isExpired,
        timeLeft: isExpired ? 0 : Math.floor((expiry - now) / (1000 * 60 * 60))
      };
    });
    
    this.store.set('activities', results);
    
    return {
      total: results.length,
      active: results.filter(r => r.status === 'active').length,
      expired: results.filter(r => r.status === 'expired').length,
      succeeded: results.filter(r => r.status === 'succeeded').length,
      list: results
    };
  }
}

module.exports = { GroupBuyHelper };
