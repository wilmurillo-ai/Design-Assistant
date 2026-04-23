#!/usr/bin/env node
const { CartOptimizer } = require('./index');

const optimizer = new CartOptimizer();

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'calc':
    case '计算': {
      const [amount, threshold, discount] = args.slice(1).map(Number);
      if (!amount || !threshold) {
        console.log('用法: cart-optimizer calc <当前金额> <门槛> <优惠>');
        process.exit(1);
      }
      const result = optimizer.calculate(amount, { threshold, discount });
      console.log(result.message);
      if (result.status === 'need_more') {
        console.log(`建议: ${result.recommendation}`);
      }
      break;
    }

    case 'compare':
    case '对比': {
      const amount = Number(args[1]);
      // 解析规则: 200:20,300:40
      const rulesStr = args[2];
      if (!amount || !rulesStr) {
        console.log('用法: cart-optimizer compare <金额> "200:20,300:40"');
        process.exit(1);
      }
      
      const rules = rulesStr.split(',').map((r, i) => {
        const [t, d] = r.split(':');
        return { name: `满${t}减${d}`, threshold: Number(t), discount: Number(d) };
      });
      
      const result = optimizer.compareRules(amount, rules);
      console.log(result.recommendation);
      console.log('\n所有选项:');
      result.options.forEach(opt => {
        console.log(`  ${opt.name}: ${opt.status === 'qualified' ? '✅' : `差¥${opt.gap.toFixed(0)}`} 实付¥${opt.finalAmount.toFixed(2)}`);
      });
      break;
    }

    default:
      console.log(`
凑单优化器 - Cart Optimizer

用法:
  cart-optimizer calc <当前金额> <门槛> <优惠>    计算凑单
  cart-optimizer compare <金额> "规则1,规则2"      对比多规则

示例:
  cart-optimizer calc 250 300 30
  cart-optimizer compare 250 "200:20,300:40,400:60"
      `);
  }
}

main();
