---
# TunnelProxy - AI 实用技巧

## 目录

1. [处理 PTY 回显问题](#1-处理-pty-回显问题)
2. [多行命令和脚本](#2-多行命令和脚本)
3. [大文件传输不截断](#3-大文件传输不截断)
4. [获取命令退出码](#4-获取命令退出码)
5. [处理超时](#5-处理超时)
6. [组合使用 - 先传脚本再执行](#6-组合使用---先传脚本再执行)
7. [环境变量传递](#7-环境变量传递)
8. [处理 PTY 粘性输出](#8-处理-pty-粘性输出)
9. [判断远程设备类型](#9-判断远程设备类型)
10. [调试 PTY 问题](#10-调试-pty-问题)
11. [故障速查表](#11-故障速查表)

---

## 1. 处理 PTY 回显问题

PTY 默认会回显你发送的命令，导致输出混入命令本身。

**解决方案：**

```bash
# 方法 A：发送 stty -echo 关闭回显
echo "stty -echo; ls -la" | nc 127.0.0.1 27417

# 方法 B：用 ; echo 标记分隔
echo "ls -la; echo '===END==='" | nc 127.0.0.1 27417
# 然后只取 ===END=== 之前的内容
```

2. 多行命令和脚本

```bash
# 用分号分隔
echo "cd /tmp; mkdir test; cd test; pwd" | nc 127.0.0.1 27417

# 用管道传递多行（推荐）
echo -e "line1\nline2\nline3" | nc 127.0.0.1 27417

# 执行复杂脚本（用 heredoc）
cat << 'EOF' | nc 127.0.0.1 27417
for i in 1 2 3; do
    echo "Number $i"
done
EOF
```

3. 大文件传输不截断

PTY 不适合传输大量二进制数据，用 HTTP 通道：

```python
# ✅ 正确：大文件用 HTTP
from http_transfer import TunnelHTTP
http = TunnelHTTP()
http.download("/path/to/large.bin", "./large.bin")

# ❌ 错误：用 PTY cat 会卡死
echo "cat /path/to/large.bin" | nc 127.0.0.1 27417  # 别这样
```

4. 获取命令退出码

```bash
# 方式1：在命令中捕获
echo "ls /tmp; echo EXIT_CODE=\$?" | nc 127.0.0.1 27417

# 方式2：用 && 和 || 链式判断
echo "test -f /etc/passwd && echo EXISTS || echo MISSING" | nc 127.0.0.1 27417
```

5. 处理超时

PTY 默认没有命令超时，需要在命令层处理：

```bash
# 用 timeout 命令
echo "timeout 5 ping google.com" | nc 127.0.0.1 27417

# 或用 curl 的 --max-time
echo "curl --max-time 10 https://slow-site.com" | nc 127.0.0.1 27417
```

6. 组合使用 - 先传脚本再执行

```python
# 1. 上传 Python 脚本
from http_transfer import TunnelHTTP
http = TunnelHTTP()
http.upload("./my_script.py")  # 上传到远程 /upload/my_script.py

# 2. 通过 PTY 执行
import socket
s = socket.socket()
s.connect(("127.0.0.1", 27417))
s.send(b"python3 /upload/my_script.py\n")
result = s.recv(4096).decode()
```

7. 环境变量传递

```bash
# 在命令中设置临时环境变量
echo "export MY_VAR=hello; echo \$MY_VAR" | nc 127.0.0.1 27417

# 或用 env 命令
echo "env MY_VAR=hello bash -c 'echo \$MY_VAR'" | nc 127.0.0.1 27417
```

8. 处理 PTY 粘性输出

PTY 会保留前一个命令的 prompt 和输出：

```python
# 每次执行前清空缓冲区
def clean_exec(cmd):
    s = socket.socket()
    s.connect(("127.0.0.1", 27417))
    # 先发送一个空命令清空
    s.send(b"\n")
    s.recv(4096)  # 吃掉残留
    # 再执行真实命令
    s.send(f"{cmd}\n".encode())
    result = s.recv(4096).decode()
    return result
```

9. 判断远程设备类型

```bash
# 检测 Android
echo "getprop ro.build.version.release" | nc 127.0.0.1 27417

# 检测 Linux 发行版
echo "cat /etc/os-release" | nc 127.0.0.1 27417

# 检测架构
echo "uname -m" | nc 127.0.0.1 27417
```

10. 调试 PTY 问题

```bash
# 看原始输出（包括控制字符）
echo "ls" | nc 127.0.0.1 27417 | cat -A

# 测试回显状态
echo "echo TEST" | nc 127.0.0.1 27417
# 如果输出 "echo TEST" 说明回显开启

# 强制重置 PTY 状态
echo -e "stty sane\nreset\n" | nc 127.0.0.1 27417
```

11. 故障速查表

现象 原因 解决
输出为空 PTY 回显/缓冲区问题 加 ; echo MARKER
输出有乱码 二进制数据混入 用 HTTP 通道传二进制
命令卡住 等待用户输入 确保命令不交互
结果被截断 socket.recv 太小 循环读取直到超时
上传失败 缺少 UPLOAD_MAGIC 检查环境变量
部分输出丢失 PTY 行缓冲 用 stdbuf -oL 禁用缓冲

---

参考链接

· TunnelProxy 项目：https://github.com/TurinFohlen/tunnel_proxy
· FRP 内网穿透：https://github.com/fatedier/frp
· PTY 原理：https://en.wikipedia.org/wiki/Pseudoterminal

```
