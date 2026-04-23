/**
 * 测试真实 STP 调用
 */

async function testRealSTP() {
    console.log('=== Testing Real STP Integration ===\n');
    
    try {
        const { STPIntegratorEnhanced } = require('../skills/github-collab/stp-integrator-enhanced');
        const stp = new STPIntegratorEnhanced();
        
        console.log('1. STP Installation Status:');
        console.log('   Status:', stp.isSTPInstalled() ? '✅ Installed' : '❌ Not Installed');
        console.log('');
        
        if (stp.isSTPInstalled()) {
            console.log('2. Testing Real STP Call:');
            console.log('   Task: "Build a React application with user authentication"');
            console.log('   Context: "Frontend project with Node.js backend"');
            console.log('');
            
            // 真实 STP 调用
            const result = await stp.splitTask(
                'Build a React application with user authentication',
                'Frontend project with Node.js backend'
            );
            
            console.log('   ✅ Real STP call successful!');
            console.log('   Output:', JSON.stringify(result, null, 2));
        } else {
            console.log('2. STP Not Installed, Testing Simulation Mode:');
            console.log('   Task: "Build a React application with user authentication"');
            console.log('   Context: "Frontend project with Node.js backend"');
            console.log('');
            
            // 模拟模式
            const result = await stp.splitTask(
                'Build a React application with user authentication',
                'Frontend project with Node.js backend'
            );
            
            console.log('   ✅ Simulation successful!');
            console.log(`   - Generated ${result.tasks.length} tasks`);
            console.log(`   - Created ${result.executionPlan.length} execution phases`);
            console.log('');
            
            console.log('3. Task Breakdown:');
            result.tasks.forEach((task, index) => {
                console.log(`   ${index + 1}. ${task.name}`);
                console.log(`      Priority: ${task.priority}, Est: ${task.estimated_hours}h`);
                console.log(`      Dependencies: ${task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}`);
            });
            console.log('');
            
            console.log('4. Execution Plan:');
            result.executionPlan.forEach((phase, index) => {
                console.log(`   Phase ${index + 1}: ${phase.tasks.length} tasks, ${phase.duration}h`);
            });
            console.log('');
            
            console.log('=== Test Summary ===');
            console.log('✅ STP Integration Ready');
            console.log('✅ Simulation Mode Working');
            console.log('⏳ Real STP calls available after installation');
            console.log('');
            console.log('To install STP skill:');
            console.log('1. Clone to: /workspace/.openclaw/skills/stp');
            console.log('2. Or: ~/.openclaw/skills/stp');
            console.log('3. Run: node tests/test-real-stp.js again');
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        console.error('Stack:', error.stack);
    }
}

// 运行测试
testRealSTP().catch(console.error);