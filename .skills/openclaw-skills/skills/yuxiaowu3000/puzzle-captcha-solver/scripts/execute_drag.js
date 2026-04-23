// execute_drag.js
// Playwright 拖动执行脚本
// 用于 agent-browser eval 命令

/**
 * 执行拖动操作
 * @param {HTMLElement} slider - 滑块元素
 * @param {Array<Array<number>>} trajectory - 轨迹数组 [[x1,y1], [x2,y2], ...]
 */
async function executeDrag(slider, trajectory) {
    const page = slider._page || slider.page;
    
    if (!page) {
        throw new Error("无法获取 page 对象");
    }
    
    // 获取滑块边界
    const box = await slider.boundingBox();
    if (!box) {
        throw new Error("无法获取滑块边界");
    }
    
    const startX = box.x + box.width / 2;
    const startY = box.y + box.height / 2;
    
    // 移动到滑块位置
    await page.mouse.move(startX, startY);
    await sleep(100);
    
    // 按下鼠标
    await page.mouse.down();
    await sleep(50);
    
    // 按轨迹移动
    for (let i = 0; i < trajectory.length; i++) {
        const [dx, dy] = trajectory[i];
        const newX = startX + dx;
        const newY = startY + dy;
        
        await page.mouse.move(newX, newY);
        
        // 60 FPS（每帧 16ms）
        await sleep(16);
    }
    
    // 稍微停顿再释放（模拟真实行为）
    await sleep(100);
    
    // 释放鼠标
    await page.mouse.up();
    await sleep(100);
}

/**
 * 睡眠函数
 * @param {number} ms - 毫秒数
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 查找滑块元素（多种选择器）
 */
function findSliderElement() {
    const selectors = [
        // 大麦网
        '.slider-btn',
        '.yidun_slider',
        
        // 淘宝/天猫
        '.slider',
        '#slider',
        '.nc-slider',
        
        // 京东
        '.JD_slider',
        '.slide-btn',
        
        // 通用
        '[class*="slider"]',
        '[id*="slider"]',
        'button[class*="drag"]',
        'div[class*="drag"]'
    ];
    
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            return element;
        }
    }
    
    return null;
}

// 如果使用 CLI 调用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { executeDrag, sleep, findSliderElement };
}
