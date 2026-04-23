---
name: error-debugger
description: Error debugging assistant. Analyzes error messages, locates root causes, and provides solutions. Triggers: error debugging, bug fix, stack trace, exception handling.
metadata: {"openclaw": {"emoji": "🐛"}}
---

# Error Debugger — 错误调试助手

## 功能说明

分析各类错误，帮助快速定位和解决问题。

## 使用方法

### 1. 错误分析

```
用户: 帮我分析这个错误：
TypeError: Cannot read property 'name' of undefined
    at UserComponent.render (App.js:25)
```

分析：
- 错误类型：TypeError
- 错误原因：访问undefined的属性
- 问题位置：App.js 第25行
- 可能原因：数据未加载、异步问题、空值未处理

### 2. 代码问题定位

```
用户: 这段代码为什么报错？
[粘贴代码和错误信息]
```

定位：
- 分析代码逻辑
- 检查变量状态
- 识别问题代码
- 解释错误原因

### 3. 解决方案

```
用户: 如何修复这个SQL错误？
ERROR: column "user_id" does not exist
```

解决方案：
1. 检查表结构
2. 确认列名拼写
3. 检查是否需要别名
4. 提供修复SQL

### 4. 预防建议

```
用户: 如何避免这类错误再次发生？
```

建议：
- 添加类型检查
- 使用防御性编程
- 添加单元测试
- 代码审查要点

## 示例输出

```
错误分析报告

【错误信息】
TypeError: Cannot read property 'name' of undefined

【问题定位】
文件: App.js
行号: 25
代码: const userName = user.profile.name

【原因分析】
1. 直接原因：user.profile 为 undefined
2. 根本原因：
   - API数据未加载完成就尝试访问
   - 缺少空值检查
   - 异步渲染时序问题

【解决方案】

方案一：添加空值检查
```javascript
const userName = user?.profile?.name || '未知用户';
```

方案二：条件渲染
```javascript
{user?.profile && <div>{user.profile.name}</div>}
```

方案三：设置默认值
```javascript
const user = data || { profile: { name: 'Guest' } };
```

【预防措施】
1. 使用 TypeScript 进行类型检查
2. 对 API 返回数据做校验
3. 添加加载状态处理
4. 编写边界情况测试用例

【相关资源】
- JavaScript 可选链操作符文档
- React 条件渲染最佳实践
```

## 支持错误类型

- JavaScript/TypeScript 运行时错误
- Python 异常
- SQL 数据库错误
- HTTP 网络错误
- 构建/编译错误
