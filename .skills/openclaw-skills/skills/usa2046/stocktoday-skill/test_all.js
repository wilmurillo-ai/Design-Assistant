#!/usr/bin/env node

const tools = [
  // 基础数据
  "stock_basic", "trade_cal", "namechange", "hs_const",
  "stock_company", "stk_managers", "stk_rewards", "new_share", "bak_basic",
  "stk_account", "stk_ah_comparison",
  // ST股票
  "stock_st", "st",
  // 行情数据
  "daily", "weekly", "monthly", "pro_bar", "adj_factor", "daily_basic",
  "stk_limit", "suspend_d", "hsgt_top10", "ggt_top10", "ggt_daily", "ggt_monthly", "bak_daily",
  // 财务数据
  "income", "balancesheet", "cashflow", "forecast", "express", "dividend",
  "fina_indicator", "fina_audit", "fina_mainbz", "disclosure_date",
  // 参考数据
  "top10_holders", "top10_floatholders", "pledge_stat", "pledge_detail",
  "repurchase", "concept", "concept_detail", "share_float", "block_trade",
  "stk_holdernumber", "stk_holdertrade", "ci_index_member",
  // 特色数据
  "report_rc", "cyq_perf", "cyq_chips", "stk_factor", "stk_factor_pro",
  "ccass_hold", "ccass_hold_detail", "hk_hold", "stk_auction_o", "stk_auction_c",
  "stk_nineturn", "stk_surv", "broker_recommend",
  // 两融
  "margin", "margin_detail", "margin_secs", "slb_sec", "slb_len", "slb_sec_detail", "slb_len_mm",
  // 资金流向
  "moneyflow", "moneyflow_ths", "moneyflow_cnt_ths", "moneyflow_dc",
  "moneyflow_ind_ths", "moneyflow_ind_dc", "moneyflow_mkt_dc", "moneyflow_hsgt",
  // 打板专题
  "kpl_concept", "kpl_concept_cons", "kpl_list", "top_list", "top_inst",
  "limit_list_ths", "limit_list_d", "limit_step", "limit_cpt_list",
  "ths_index", "ths_member", "dc_index", "dc_member", "stk_auction",
  "hm_list", "hm_detail", "ths_hot", "dc_hot",
  // 指数
  "index_basic", "index_daily", "index_weekly", "index_monthly", "index_weight",
  "index_dailybasic", "index_classify", "index_member", "index_member_all",
  "daily_info", "sz_daily_info", "ths_daily", "ci_daily", "sw_daily", "index_global", "idx_factor_pro",
  "gz_index", "wz_index", "tdx_index", "tdx_daily", "dc_daily",
  // 基金
  "fund_basic", "fund_company", "fund_manager", "fund_share", "fund_nav",
  "fund_div", "fund_portfolio", "fund_daily", "fund_adj", "fund_factor_pro",
  "fund_sales_ratio", "fund_sales_vol", "etf_basic", "etf_index", "etf_share_size",
  // 期货
  "fut_basic", "fut_daily", "fut_weekly_monthly", "fut_wsr",
  "fut_settle", "fut_holding", "fut_mapping", "fut_weekly_detail", "ft_limit",
  // 现货
  "sge_basic", "sge_daily",
  // 期权
  "opt_basic", "opt_daily",
  // 可转债
  "cb_basic", "cb_issue", "cb_call", "cb_rate", "cb_daily", "cb_price_chg", "cb_share",
  "cb_factor_pro",
  // 其他
  "repo_daily", "bc_otcqt", "bc_bestotcqt", "bond_blk", "bond_blk_detail",
  "yc_cb", "fx_obasic", "fx_daily",
  // 宏观经济
  "shibor", "shibor_quote", "cn_gdp", "cn_cpi", "cn_ppi", "sf_month",
  // 港股
  "hk_basic", "hk_tradecal", "hk_daily",
  "hk_balancesheet", "hk_cashflow", "hk_income",
  // 美股
  "us_basic", "us_tradecal",
  "us_balancesheet", "us_cashflow", "us_income",
  // 资讯
  "news", "major_news"
];

const BASE_URL = "https://tushare.citydata.club/";
const TOKEN = process.env.STOCKTODAY_TOKEN || "test";

async function callAPI(endpoint, params = {}) {
  const formData = new URLSearchParams();
  formData.append("TOKEN", TOKEN);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") formData.append(k, String(v));
  }
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      body: formData,
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function testTools() {
  console.log(`Testing ${tools.length} tools...\n`);
  
  let success = 0;
  let failed = 0;
  const errors = [];

  for (const tool of tools) {
    const endpoint = "/" + tool;
    try {
      // 通用参数测试
      const params = getTestParams(tool);
      const result = await callAPI(endpoint, params);
      
      if (result.error) {
        failed++;
        errors.push(`${tool}: ${result.error}`);
      } else if (Array.isArray(result)) {
        success++;
        process.stdout.write(`✅ ${tool} (${result.length} rows)\n`);
      } else if (result.data) {
        success++;
        process.stdout.write(`✅ ${tool} (${result.data.length || 1} rows)\n`);
      } else {
        success++;
        process.stdout.write(`✅ ${tool}\n`);
      }
    } catch (e) {
      failed++;
      errors.push(`${tool}: ${e.message}`);
    }
  }

  console.log(`\n=== Results ===`);
  console.log(`Success: ${success}`);
  console.log(`Failed: ${failed}`);
  
  if (errors.length > 0) {
    console.log(`\nErrors:`);
    errors.forEach(e => console.log(`  - ${e}`));
  }
}

function getTestParams(tool) {
  const params = {};

  // === 特殊参数接口（按 ST_CLIENT.py 签名精确匹配） ===

  // 需要 ann_date
  if (tool === "forecast") {
    params.ann_date = "20250110";
    return params;
  }
  if (tool === "fund_div") {
    params.ann_date = "20250110";
    return params;
  }
  if (tool === "stk_managers") {
    params.ts_code = "600519.SH";
    params.ann_date = "20250110";
    return params;
  }

  // 需要 month
  if (tool === "broker_recommend") {
    params.month = "202501";
    return params;
  }

  // 沪深股通成分股
  if (tool === "hs_const") {
    params.hs_type = "1";
    params.is_new = "1";
    return params;
  }

  // 集合竞价/盘后定价
  if (tool === "stk_auction_o" || tool === "stk_auction_c") {
    params.ts_code = "600519.SH";
    params.trade_date = "20250110";
    return params;
  }

  // pro_bar 行情（复权）
  if (tool === "pro_bar") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    params.adj = "qfq";
    params.freq = "D";
    return params;
  }

  // index_weight 指数成分（不是 ts_code，是 index_code）
  if (tool === "index_weight") {
    params.index_code = "000001.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // index_member 指数成分股
  if (tool === "index_member") {
    params.index_code = "000001.SH";
    return params;
  }

  // index_member_all 指数成分股(全)
  if (tool === "index_member_all") {
    params.l1_code = "A";
    return params;
  }

  // ci_index_member 中证指数成分
  if (tool === "ci_index_member") {
    params.index_code = "000001.SH";
    return params;
  }

  // dc_moneyflow_stock 东财资金流向
  if (tool === "dc_moneyflow_stock") {
    params.trade_date = "20250110";
    return params;
  }

  // 研报
  if (tool === "report_rc") {
    params.ts_code = "600519.SH";
    params.report_date = "20250110";
    return params;
  }

  // 舆情监控
  if (tool === "stk_surv") {
    params.ts_code = "600519.SH";
    params.trade_date = "20250110";
    return params;
  }

  // stk_nineturn 九转序列
  if (tool === "stk_nineturn") {
    params.ts_code = "600519.SH";
    params.trade_date = "20250110";
    return params;
  }

  // 股票因子
  if (tool === "stk_factor" || tool === "stk_factor_pro") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 筹码
  if (tool === "cyq_perf" || tool === "cyq_chips") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 合约映射
  if (tool === "fut_mapping") {
    params.ts_code = "IF9999.CF";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 期货结算/持仓/涨跌停
  if (tool === "fut_settle" || tool === "fut_holding" || tool === "ft_limit") {
    params.trade_date = "20250110";
    params.exchange = "CFFEX";
    return params;
  }

  // 期货分钟线
  if (tool === "ft_mins") {
    params.ts_code = "IF9999.CF";
    params.start_date = "20250101";
    params.end_date = "20250110";
    params.freq = "5";
    return params;
  }

  // 期货周月线
  if (tool === "fut_weekly_monthly") {
    params.ts_code = "IF9999.CF";
    params.start_date = "20250101";
    params.end_date = "20250110";
    params.freq = "W";
    return params;
  }

  // 港股分钟线
  if (tool === "hk_mins") {
    params.ts_code = "00700.HK";
    params.start_date = "20250101";
    params.end_date = "20250110";
    params.freq = "5";
    return params;
  }

  // 港股财务
  if (tool === "hk_income" || tool === "hk_balancesheet" || tool === "hk_cashflow") {
    params.ts_code = "00700.HK";
    return params;
  }

  // 美股财务
  if (tool === "us_income" || tool === "us_balancesheet" || tool === "us_cashflow") {
    params.ts_code = "AAPL.US";
    return params;
  }

  // 可转债每日
  if (tool === "cb_daily") {
    params.ts_code = "113009.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 港股每日复权
  if (tool === "hk_daily_adj") {
    params.ts_code = "00700.HK";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 美股每日复权
  if (tool === "us_daily_adj") {
    params.ts_code = "AAPL.US";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // SHIBOR
  if (tool === "shibor" || tool === "shibor_quote") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 中国宏观
  if (tool === "cn_gdp" || tool === "cn_cpi" || tool === "cn_ppi") {
    params.start_date = "20240101";
    params.end_date = "20250110";
    return params;
  }

  // 上海期货月度
  if (tool === "sf_month") {
    params.start_month = "202401";
    params.end_month = "202501";
    return params;
  }

  // 银行间报价
  if (tool === "bc_otcqt" || tool === "bc_bestotcqt") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 债券大宗交易
  if (tool === "bond_blk" || tool === "bond_blk_detail") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 指数全球/申万/中证
  if (tool === "index_global") {
    params.ts_code = "WI.SP";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  if (tool === "ci_daily") {
    params.trade_date = "20250110";
    return params;
  }

  if (tool === "sw_daily") {
    params.trade_date = "20250110";
    return params;
  }

  // 东财指数
  if (tool === "dc_daily") {
    params.ts_code = "399001.SZ";
    params.trade_date = "20250110";
    return params;
  }

  // 国债/中债指数
  if (tool === "gz_index" || tool === "wz_index") {
    params.ts_code = "000001.SH";
    params.trade_date = "20250110";
    return params;
  }

  // 同花顺/东财热点
  if (tool === "ths_hot" || tool === "dc_hot") {
    params.market = "SH";
    params.trade_date = "20250110";
    return params;
  }

  // 每日信息
  if (tool === "daily_info") {
    params.trade_date = "20250110";
    params.exchange = "SSE";
    return params;
  }

  // sz_daily_info
  if (tool === "sz_daily_info") {
    params.trade_date = "20250110";
    params.ts_code = "000001.SZ";
    return params;
  }

  // ths_daily
  if (tool === "ths_daily") {
    params.ts_code = "885001.TI";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // idx_factor_pro
  if (tool === "idx_factor_pro") {
    params.ts_code = "000001.SH";
    params.trade_date = "20250110";
    return params;
  }

  // fund_manager / fund_portfolio / fund_nav / fund_share
  if (tool === "fund_manager" || tool === "fund_portfolio" || tool === "fund_nav" || tool === "fund_share") {
    params.ts_code = "000001.OF";
    return params;
  }

  // fund_daily / fund_adj
  if (tool === "fund_daily" || tool === "fund_adj") {
    params.ts_code = "000001.OF";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // fund_factor_pro
  if (tool === "fund_factor_pro") {
    params.ts_code = "000001.OF";
    params.trade_date = "20250110";
    return params;
  }

  // etf_index
  if (tool === "etf_index") {
    params.ts_code = "159919.SZ";
    return params;
  }

  // etf_share_size
  if (tool === "etf_share_size") {
    params.ts_code = "159919.SZ";
    params.trade_date = "20250110";
    return params;
  }

  // 股东增减持
  if (tool === "stk_holdertrade") {
    params.ts_code = "600519.SH";
    params.ann_date = "20250110";
    return params;
  }

  // 主营业务
  if (tool === "fina_mainbz") {
    params.ts_code = "600519.SH";
    params.type = "1";
    return params;
  }

  // 财务指标
  if (tool === "fina_indicator") {
    params.ts_code = "600519.SH";
    return params;
  }

  // 财务审计
  if (tool === "fina_audit") {
    params.ts_code = "600519.SH";
    return params;
  }

  // 新股上市
  if (tool === "new_share") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 披露日期
  if (tool === "disclosure_date") {
    params.end_date = "20250110";
    return params;
  }

  // stk_rewards
  if (tool === "stk_rewards") {
    params.ts_code = "600519.SH";
    return params;
  }

  // hk_hold
  if (tool === "hk_hold") {
    params.ts_code = "00700.HK";
    params.exchange = "SEHK";
    return params;
  }

  // ccass_hold / ccass_hold_detail
  if (tool === "ccass_hold") {
    params.ts_code = "00700.HK";
    return params;
  }
  if (tool === "ccass_hold_detail") {
    params.ts_code = "00700.HK";
    params.trade_date = "20250110";
    return params;
  }

  // 质押统计/明细
  if (tool === "pledge_stat" || tool === "pledge_detail") {
    params.ts_code = "600519.SH";
    return params;
  }

  // repurchase 股份回购
  if (tool === "repurchase") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // share_float 流通股本
  if (tool === "share_float") {
    params.ann_date = "20250110";
    return params;
  }

  // block_trade 大宗交易
  if (tool === "block_trade") {
    params.trade_date = "20250110";
    return params;
  }

  // top10_holders / top10_floatholders
  if (tool === "top10_holders" || tool === "top10_floatholders") {
    params.ts_code = "600519.SH";
    return params;
  }

  // 股东户数
  if (tool === "stk_holdernumber") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // kpl_concept / kpl_concept_cons
  if (tool === "kpl_concept" || tool === "kpl_concept_cons") {
    params.trade_date = "20250110";
    return params;
  }

  // kpl_list
  if (tool === "kpl_list") {
    params.trade_date = "20250110";
    params.tag = "涨停";
    return params;
  }

  // limit_list_ths / limit_list_d
  if (tool === "limit_list_ths" || tool === "limit_list_d") {
    params.trade_date = "20250110";
    params.limit_type = "涨停";
    return params;
  }

  // limit_step / limit_cpt_list
  if (tool === "limit_step" || tool === "limit_cpt_list") {
    params.ts_code = "600519.SH";
    params.trade_date = "20250110";
    return params;
  }

  // ths_member / dc_member
  if (tool === "ths_member") {
    params.ts_code = "885001.TI";
    return params;
  }
  if (tool === "dc_member") {
    params.ts_code = "399001.SZ";
    params.trade_date = "20250110";
    return params;
  }

  // hm_detail
  if (tool === "hm_detail") {
    params.trade_date = "20250110";
    return params;
  }

  // index_classify
  if (tool === "index_classify") {
    params.level = "1";
    params.src = "SW";
    return params;
  }

  // index_dailybasic
  if (tool === "index_dailybasic") {
    params.trade_date = "20250110";
    return params;
  }

  // tdx_index / tdx_daily
  if (tool === "tdx_index") {
    params.ts_code = "999999.SZ";
    return params;
  }
  if (tool === "tdx_daily") {
    params.ts_code = "999999.SZ";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // suspend_d
  if (tool === "suspend_d") {
    params.ts_code = "600519.SH";
    params.suspend_type = "1";
    return params;
  }

  // ggt_top10 / ggt_daily / ggt_monthly
  if (tool === "ggt_top10" || tool === "ggt_daily" || tool === "ggt_monthly") {
    params.trade_date = "20250110";
    return params;
  }

  // bak_daily
  if (tool === "bak_daily") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // bak_basic
  if (tool === "bak_basic") {
    params.exchange = "SSE";
    return params;
  }

  // stock_company
  if (tool === "stock_company") {
    params.ts_code = "600519.SH";
    return params;
  }

  // stock_st / st
  if (tool === "stock_st" || tool === "st") {
    params.trade_date = "20250110";
    return params;
  }

  // adj_factor
  if (tool === "adj_factor") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // daily_basic
  if (tool === "daily_basic") {
    params.ts_code = "600519.SH";
    params.trade_date = "20250110";
    return params;
  }

  // dividend
  if (tool === "dividend") {
    params.ts_code = "600519.SH";
    return params;
  }

  // express
  if (tool === "express") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // namechange
  if (tool === "namechange") {
    params.ts_code = "600519.SH";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // news / major_news
  if (tool === "news" || tool === "major_news") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // stk_account 股票账户
  if (tool === "stk_account") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // stk_ah_comparison AH股比价
  if (tool === "stk_ah_comparison") {
    params.trade_date = "20250110";
    return params;
  }

  // ci_index_member 中证指数成分
  if (tool === "ci_index_member") {
    params.index_code = "000001.SH";
    return params;
  }

  // gz_index 国债指数 / wz_index 中债指数
  if (tool === "gz_index" || tool === "wz_index") {
    params.ts_code = "000001.SH";
    params.trade_date = "20250110";
    return params;
  }

  // tdx_index 通达信指数
  if (tool === "tdx_index") {
    params.ts_code = "999999.SZ";
    return params;
  }

  // tdx_daily 通达信指数日线
  if (tool === "tdx_daily") {
    params.ts_code = "999999.SZ";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // dc_daily 东财指数每日
  if (tool === "dc_daily") {
    params.ts_code = "399001.SZ";
    params.trade_date = "20250110";
    return params;
  }

  // fund_sales_ratio / fund_sales_vol 基金销售
  if (tool === "fund_sales_ratio" || tool === "fund_sales_vol") {
    params.trade_date = "20250110";
    return params;
  }

  // fut_trade_cal 期货交易日历
  if (tool === "fut_trade_cal") {
    params.exchange = "CFFEX";
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // 港股财务 hk_balancesheet / hk_cashflow / hk_income
  if (tool === "hk_balancesheet" || tool === "hk_cashflow" || tool === "hk_income") {
    params.ts_code = "00700.HK";
    return params;
  }

  // 美股财务 us_balancesheet / us_cashflow / us_income
  if (tool === "us_balancesheet" || tool === "us_cashflow" || tool === "us_income") {
    params.ts_code = "AAPL.US";
    return params;
  }

  // shibor / shibor_quote
  if (tool === "shibor" || tool === "shibor_quote") {
    params.start_date = "20250101";
    params.end_date = "20250110";
    return params;
  }

  // cn_gdp / cn_cpi / cn_ppi
  if (tool === "cn_gdp" || tool === "cn_cpi" || tool === "cn_ppi") {
    params.start_date = "20240101";
    params.end_date = "20250110";
    return params;
  }

  // sf_month 上海期货月度
  if (tool === "sf_month") {
    params.start_month = "202401";
    params.end_month = "202501";
    return params;
  }

  // cb_factor_pro 可转债因子
  if (tool === "cb_factor_pro") {
    params.ts_code = "113009.SH";
    params.trade_date = "20250110";
    return params;
  }

  // === 默认：需要 ts_code + 日期范围 ===
  if (tool.includes("stock") || tool.includes("stk") || tool.includes("daily") ||
      tool.includes("income") || tool.includes("balance") || tool.includes("cashflow") ||
      tool.includes("dividend") || tool.includes("fina") || tool.includes("holder") ||
      tool.includes("margin") || tool.includes("moneyflow") || tool.includes("auction") ||
      tool.includes("factor") || tool.includes("pledge") || tool.includes("concept") ||
      tool.includes("report") || tool.includes("cyq") || tool.includes("surv") ||
      tool.includes("manager") || tool.includes("reward") || tool.includes("stk_auction")) {
    params.ts_code = "600519.SH";
  }

  // 指数代码
  if (tool.includes("index") && !tool.includes("stock") && !tool.includes("ths") &&
      !tool.includes("ci_") && !tool.includes("sw_") && !tool.includes("dc_") &&
      !tool.includes("gz_") && !tool.includes("wz_") && !tool.includes("tdx_") &&
      !tool.includes("idx_") && !tool.includes("index_global") && !tool.includes("index_member")) {
    params.ts_code = "000001.SH";
  }

  // 基金代码
  if (tool.includes("fund") && !tool.includes("etf")) {
    params.ts_code = "000001.OF";
  }

  // ETF
  if (tool.includes("etf")) {
    params.ts_code = "159919.SZ";
  }

  // 期货代码
  if (tool.includes("fut") || tool === "ft_limit" || tool === "ft_mins") {
    params.ts_code = "IF9999.CF";
  }

  // 港股代码
  if (tool.includes("hk_") && tool !== "hk_hold") {
    params.ts_code = "00700.HK";
  }

  // 美股代码
  if (tool.includes("us_") && !tool.includes("us_basic")) {
    params.ts_code = "AAPL.US";
  }

  // 可转债代码
  if (tool.includes("cb_") && tool !== "cb_basic" && tool !== "cb_daily") {
    params.ts_code = "113009.SH";
  }

  // 期权
  if (tool.includes("opt_")) {
    params.exchange = "SSE";
  }

  // 现货
  if (tool.includes("sge_")) {
    params.ts_code = "au99.99";
  }

  // 外汇
  if (tool.includes("fx_")) {
    params.ts_code = "USD/CNY";
  }

  // 需要日期的接口
  const noDateList = [
    "stock_basic", "index_basic", "fund_basic", "fut_basic", "concept",
    "ths_index", "hk_basic", "us_basic", "sge_basic", "cb_basic", "opt_basic",
    "hm_list", "trade_cal", "report_rc", "broker_recommend", "stk_premarket",
    "stock_st", "st", "stk_rewards", "bak_basic", "pledge_stat", "pledge_detail",
    "share_float", "top10_holders", "top10_floatholders", "fina_indicator",
    "fina_audit", "fina_mainbz", "fund_company", "fund_manager", "fund_portfolio",
    "fund_nav", "fund_share", "etf_basic", "etf_index", "etf_share_size",
    "ccass_hold", "hk_hold", "stk_nineturn", "stk_surv", "disclosure_date",
    "namechange", "news", "major_news", "index_classify", "dc_moneyflow_stock",
    "ci_index_member", "index_member", "index_member_all", "stk_holdernumber",
    "stk_holdertrade", "repurchase", "fut_mapping", "stock_company"
  ];

  if (!noDateList.includes(tool) && Object.keys(params).length > 0) {
    params.start_date = "20250101";
    params.end_date = "20250110";
  } else if (!noDateList.includes(tool) && Object.keys(params).length === 0) {
    // 没有 ts_code 但需要日期的
    params.start_date = "20250101";
    params.end_date = "20250110";
  }

  return params;
}

testTools();
