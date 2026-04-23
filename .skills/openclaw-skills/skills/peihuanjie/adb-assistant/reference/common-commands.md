# ADB 常用命令参考

## 设备连接

```bash
# 列出已连接设备
adb devices

# 通过 WiFi 连接
adb connect <ip>:<port>

# 断开连接
adb disconnect <ip>:<port>

# 重启 adb 服务
adb kill-server && adb start-server
```

## 应用管理

```bash
# 列出已安装应用
adb shell pm list packages

# 安装 APK
adb install <path/to/app.apk>

# 卸载应用
adb uninstall <package_name>

# 启动应用
adb shell am start -n <package_name>/<activity_name>

# 强制停止应用
adb shell am force-stop <package_name>
```

## 日志与调试

```bash
# 实时日志
adb logcat

# 按标签过滤
adb logcat -s <TAG>

# 清除日志缓存
adb logcat -c

# 导出日志到文件
adb logcat -d > /tmp/logcat.txt

# 抓取 bugreport
adb bugreport > /tmp/bugreport.zip
```

## 文件操作

```bash
# 推送文件到设备
adb push <local_path> <device_path>

# 从设备拉取文件
adb pull <device_path> <local_path>

# 截屏
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png .

# 录屏
adb shell screenrecord /sdcard/record.mp4
```

## 系统信息

```bash
# 系统属性
adb shell getprop

# 系统版本
adb shell getprop ro.build.display.id

# CPU 信息
adb shell cat /proc/cpuinfo

# 内存信息
adb shell cat /proc/meminfo

# 磁盘使用
adb shell df -h
```

## 网络调试

```bash
# 查看网络接口
adb shell ifconfig

# 查看 IP 地址
adb shell ip addr show

# 网络连通性测试
adb shell ping -c 3 <host>

# 查看端口监听
adb shell netstat -tlnp
```

## 输入模拟

```bash
# 模拟点击
adb shell input tap <x> <y>

# 模拟滑动
adb shell input swipe <x1> <y1> <x2> <y2>

# 模拟按键
adb shell input keyevent <keycode>

# 输入文本
adb shell input text "<text>"
```

## 车载专用（需通过 AI 接口查询具体命令）

车载系统的 ADB 命令因车型和系统版本不同而有差异，建议通过 AI 查询接口获取精准命令：

```bash
curl -s 'http://test.xui.xiaopeng.local:8009/ai/v1/chat_query' \
-H 'Content-Type: application/json' \
-d '{"user_id": "<user_id>", "query": "<你的问题>"}'
```
