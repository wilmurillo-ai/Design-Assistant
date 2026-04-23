const fs = require('fs');
const path = require('path');

// 简单的HTTP请求封装
async function httpPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

async function fetchUserData(email, password) {
    return httpPost('https://puckg.fun/api/agent/user-data', { email, password });
}

async function fetchFoodData(userId, startDate, endDate, mealType = null) {
    const payload = { userId };
    if (startDate) payload.startDate = startDate;
    if (endDate) payload.endDate = endDate;
    if (mealType) payload.mealType = mealType;
    return httpPost('https://www.puckg.xyz/api/food/analysis/by-date-range', payload);
}

function generateFoodReport(foodData, userEmail, dateRange, outputFile, templatePath) {
    let template = fs.readFileSync(templatePath, 'utf8');
    const foodDataJson = JSON.stringify(foodData, null, 4);

    // 替换数据
    template = template.replace(/const FOOD_DATA = \{[\s\S]*?\};/, `const FOOD_DATA = ${foodDataJson};`);
    template = template.replace('const USER_EMAIL = "user@example.com";', `const USER_EMAIL = "${userEmail}";`);
    template = template.replace(
        /const DATE_RANGE = \{\s*start: "[^"]+",\s*end: "[^"]+"\s*\};/,
        `const DATE_RANGE = {\n            start: "${dateRange[0]}",\n            end: "${dateRange[1]}"\n        };`
    );

    fs.writeFileSync(outputFile, template, 'utf8');
    console.log(`✅ 报告已生成: ${outputFile}`);
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.log('用法: node generate_food_report.js <邮箱> <密码> [开始日期] [结束日期]');
        console.log('示例: node generate_food_report.js user@example.com password123');
        console.log('      node generate_food_report.js user@example.com password123 2026-03-01 2026-03-31');
        process.exit(1);
    }

    const [email, password, startArg, endArg] = args;

    // 日期范围
    let startDate, endDate;
    if (startArg && endArg) {
        startDate = startArg;
        endDate = endArg;
    } else {
        const now = new Date();
        startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        endDate = lastDay.toISOString().split('T')[0];
    }

    console.log(`📧 邮箱: ${email}`);
    console.log(`📅 日期范围: ${startDate} 至 ${endDate}`);
    console.log('-'.repeat(50));

    // 1. 登录
    console.log('🔐 正在登录...');
    const userResult = await fetchUserData(email, password);
    if (!userResult.success) {
        console.log(`❌ 登录失败: ${userResult.message}`);
        process.exit(1);
    }
    const userId = userResult.data.user.id;
    console.log(`✅ 登录成功，用户ID: ${userId}`);

    // 2. 获取数据
    console.log('\n📊 正在获取饮食数据...');
    const foodResult = await fetchFoodData(userId, startDate, endDate);
    if (!foodResult.success || !foodResult.data) {
        console.log(`❌ 获取数据失败: ${foodResult.message}`);
        process.exit(1);
    }

    const data = foodResult.data;

    // 打印摘要
    console.log('\n' + '='.repeat(60));
    console.log('📊 饮食数据摘要');
    console.log('='.repeat(60));
    console.log(`总记录数: ${data.totalCount}`);
    console.log(`总热量: ${data.totalCalories} kcal`);

    if (data.stats) {
        console.log('\n' + '='.repeat(60));
        console.log('🍽️ 按餐型统计');
        console.log('='.repeat(60));
        for (const [mealType, stat] of Object.entries(data.stats)) {
            console.log(`${mealType}: ${stat.count} 餐, ${stat.totalCalories} kcal`);
        }
    }

    // 3. 生成报告
    const monthStr = startDate.substring(0, 7);
    const outputFile = `food_report_${monthStr}.html`;
    const skillDir = path.dirname(__dirname);
    const templatePath = path.join(skillDir, 'assets', 'food_report_template.html');

    generateFoodReport(data, email, [startDate, endDate], outputFile, templatePath);

    // 4. 保存JSON
    const jsonFile = `food_data_${monthStr}.json`;
    fs.writeFileSync(jsonFile, JSON.stringify(data, null, 2), 'utf8');
    console.log(`✅ 数据已保存: ${jsonFile}`);

    console.log('\n🎉 完成！生成的文件:');
    console.log(`   📄 ${outputFile}`);
    console.log(`   📄 ${jsonFile}`);
}

main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
});
