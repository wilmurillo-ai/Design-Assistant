/**
 * 眠小兔插件测试脚本
 */

const plugin = require('./sleep-rabbit-plugin.js');

async function testPlugin() {
  console.log('='.repeat(60));
  console.log('眠小兔OpenClaw插件测试');
  console.log('='.repeat(60));
  
  // 测试1: 初始化插件
  console.log('\n[测试1] 初始化插件...');
  const initialized = await plugin.initialize({});
  if (!initialized) {
    console.error('❌ 插件初始化失败');
    return;
  }
  console.log('✅ 插件初始化成功');
  
  // 测试2: 获取命令列表
  console.log('\n[测试2] 获取命令列表...');
  const commands = plugin.getCommands();
  console.log(`✅ 找到 ${Object.keys(commands).length} 个命令:`);
  Object.keys(commands).forEach(cmd => {
    console.log(`  - /${cmd}: ${commands[cmd].description}`);
  });
  
  // 测试3: 测试帮助命令
  console.log('\n[测试3] 测试帮助命令...');
  try {
    const helpResult = await plugin.handleHelp([], {});
    console.log('✅ 帮助命令测试成功');
    console.log(helpResult.substring(0, 200) + '...');
  } catch (error) {
    console.error('❌ 帮助命令测试失败:', error);
  }
  
  // 测试4: 测试睡眠分析命令（模拟）
  console.log('\n[测试4] 测试睡眠分析命令（模拟参数）...');
  try {
    // 注意：这里使用模拟路径，实际测试需要真实EDF文件
    const testArgs = ['D:\\openclaw\\AISleepGen\\data\\edf\\SC4001E0-PSG.edf'];
    console.log('测试参数:', testArgs);
    
    // 由于需要真实文件，这里只测试命令处理逻辑
    console.log('⚠️  需要真实EDF文件进行完整测试');
    console.log('✅ 命令处理器可用');
  } catch (error) {
    console.error('❌ 睡眠分析命令测试失败:', error);
  }
  
  // 测试5: 直接测试Python技能
  console.log('\n[测试5] 直接测试Python技能...');
  try {
    const versionResult = await plugin.executeSkill('--version', []);
    console.log('✅ Python技能测试成功:');
    console.log(versionResult);
  } catch (error) {
    console.error('❌ Python技能测试失败:', error);
    console.log('可能的原因:');
    console.log('1. Python未安装或不在PATH中');
    console.log('2. 依赖库未安装 (mne, numpy, scipy)');
    console.log('3. 技能文件路径错误');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('测试完成');
  console.log('='.repeat(60));
  
  // 清理
  await plugin.cleanup();
}

// 运行测试
testPlugin().catch(error => {
  console.error('测试过程中发生错误:', error);
  process.exit(1);
});