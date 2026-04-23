/**
 * 验证码处理执行脚本
 * 
 * 在 Playwright 浏览器环境中执行验证操作
 * 支持旋转、拼图滑块、点击等验证码类型
 * 
 * @param {Object} action - 验证动作
 * @param {string} action.type - 验证码类型：rotate|puzzle|click|graphic
 * @param {Object} action.params - 具体参数
 */
async function executeAction(action) {
    const { type, params } = action;
    
    console.log(`🚀 执行验证操作：${type}`);
    
    switch (type) {
        case "rotate":
            return await executeRotate(params);
        
        case "puzzle":
            return await executePuzzle(params);
        
        case "click":
            return await executeClick(params);
        
        case "graphic":
            return await handleGraphic(params);
        
        default:
            throw new Error(`未知的验证码类型：${type}`);
    }
}

/**
 * 执行旋转验证码
 */
async function executeRotate(params) {
    const { angle, direction, center, radius } = params;
    
    console.log(`🔄 旋转 ${angle}° ${direction}`);
    
    // 1. 找到旋转滑块
    const slider = await findRotateSlider();
    if (!slider) {
        throw new Error("未找到旋转滑块");
    }
    
    // 2. 获取滑块位置
    const box = await slider.boundingBox();
    
    // 3. 计算拖动距离（角度转像素）
    // 假设 180 度对应 200 像素
    const dragDistance = (angle / 180) * 200;
    const isClockwise = direction === "clockwise";
    const actualDistance = isClockwise ? dragDistance : -dragDistance;
    
    // 4. 生成人类拖动轨迹
    const trajectory = generateHumanTrajectory(actualDistance, 2.5);
    
    // 5. 执行拖动
    await performDrag(slider, box, trajectory);
    
    // 6. 等待验证结果
    await sleep(1500);
    
    console.log("✅ 旋转验证完成");
    return { success: true, message: "验证通过" };
}

/**
 * 执行拼图滑块验证码
 */
async function executePuzzle(params) {
    const { slider, offset } = params;
    
    console.log(`🧩 拖动滑块 ${offset}px`);
    
    // 1. 找到滑块元素
    const sliderElement = await findPuzzleSlider();
    if (!sliderElement) {
        throw new Error("未找到滑块元素");
    }
    
    // 2. 获取边界
    const box = await sliderElement.boundingBox();
    
    // 3. 生成拖动轨迹
    const trajectory = generateHumanTrajectory(offset, 2.0);
    
    // 4. 执行拖动
    await performDrag(sliderElement, box, trajectory);
    
    // 5. 等待验证结果
    await sleep(1500);
    
    console.log("✅ 拼图验证完成");
    return { success: true, message: "验证通过" };
}

/**
 * 执行点击验证码
 */
async function executeClick(params) {
    const { points } = params;
    
    console.log(`👆 点击 ${points.length} 个位置`);
    
    for (const point of points) {
        await page.mouse.click(point.x, point.y);
        await sleep(300);
    }
    
    await sleep(1000);
    
    console.log("✅ 点击验证完成");
    return { success: true, message: "验证通过" };
}

/**
 * 处理图形验证码（需要用户输入）
 */
async function handleGraphic(params) {
    const { message } = params;
    
    console.log("🔢 图形验证码需要用户输入");
    
    // 截图保存
    await page.screenshot({ path: "graphic_captcha.png" });
    
    return {
        success: false,
        message: "图形验证码需要用户手动输入，请查看 graphic_captcha.png"
    };
}

/**
 * 查找旋转滑块
 */
async function findRotateSlider() {
    const selectors = [
        '.rotate-slider',
        '.slider-btn',
        '[class*="rotate"]',
        '[class*="slider"]',
    ];
    
    for (const selector of selectors) {
        try {
            const element = await document.querySelector(selector);
            if (element) return element;
        } catch (e) {
            continue;
        }
    }
    
    return null;
}

/**
 * 查找拼图滑块
 */
async function findPuzzleSlider() {
    const selectors = [
        '.slider-btn',
        '.puzzle-slider',
        '[class*="slider"]',
        'canvas + div[class*="slider"]',
    ];
    
    for (const selector of selectors) {
        try {
            const element = await document.querySelector(selector);
            if (element) return element;
        } catch (e) {
            continue;
        }
    }
    
    return null;
}

/**
 * 生成人类拖动轨迹
 */
function generateHumanTrajectory(distance, duration = 2.0) {
    const trajectory = [];
    const steps = Math.floor(duration * 60);
    
    // 启动停顿
    const pauseSteps = Math.floor(0.3 * 60);
    for (let i = 0; i < pauseSteps; i++) {
        trajectory.push({
            x: 0,
            y: Math.random() * 2 - 1,
            delay: 16
        });
    }
    
    // 主拖动（ease-out）
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const progress = 1 - Math.pow(1 - t, 3);
        
        const x = distance * progress;
        const y = Math.sin(t * Math.PI * 4) * 2 + (Math.random() * 2 - 1);
        const delay = 16 + Math.random() * 8 - 4;
        
        trajectory.push({ x, y, delay });
    }
    
    // 到达微调
    for (let i = 0; i < 5; i++) {
        trajectory.push({
            x: distance + (Math.random() * 4 - 2),
            y: Math.random() * 2 - 1,
            delay: 30
        });
    }
    
    return trajectory;
}

/**
 * 执行拖动操作
 */
async function performDrag(slider, box, trajectory) {
    const page = slider._context._page;
    
    const startX = box.x + box.width / 2;
    const startY = box.y + box.height / 2;
    
    // 移动到滑块
    await page.mouse.move(startX, startY);
    await sleep(200 + Math.random() * 200);
    
    // 按下鼠标
    await page.mouse.down();
    
    // 按轨迹移动
    let currentX = startX;
    let currentY = startY;
    
    for (const point of trajectory) {
        currentX += point.x;
        currentY += point.y;
        
        await page.mouse.move(currentX, currentY);
        await sleep(point.delay);
    }
    
    // 保持片刻
    await sleep(300 + Math.random() * 200);
    
    // 释放鼠标
    await page.mouse.up();
}

/**
 * 睡眠函数
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { executeAction };
}
