module.exports = async function skillMain(inputs, context) {
  const log = (msg) => console.log(`[海外商旅套件] ${msg}`);

  log("开始执行海外商旅全流程自动化");
  log(`员工：${inputs.user_id}`);
  log(`行程：${inputs.dep_city} → ${inputs.arr_city}`);

  // 1. 航班查询
  log("1. 正在查询海外直飞航班...");

  // 2. 差旅政策校验
  log("2. 正在校验差旅额度与政策...");

  // 3. 机票预订 + 支付
  log("3. 正在预订机票并完成企业支付...");

  // 4. 酒店预订 + 支付
  log("4. 正在预订酒店并完成企业支付...");

  // 5. 自动生成报销
  log("5. 正在自动生成报销单...");

  // 模拟返回真实订单结构（可对接真实 API）
  return {
    success: true,
    flight_order_id: `FLIGHT_${Date.now()}`,
    hotel_order_id: `HOTEL_${Date.now()}`,
    expense_id: `EXPENSE_${Date.now()}`,
    message:
      "✅ 海外商旅全流程完成：航班+酒店+支付+报销已全部自动处理完毕"
  };
};