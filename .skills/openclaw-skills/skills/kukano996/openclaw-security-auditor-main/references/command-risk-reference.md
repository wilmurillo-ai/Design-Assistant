# 命令风险评估参考

本文档包含完整的命令风险分类，用于安全审计时快速查询。

## 风险等级定义

- **CRITICAL (🔴)**: 极高危命令，绝对禁止执行
- **HIGH (🟠)**: 高危命令，必须获得用户明确确认
- **MEDIUM (🟡)**: 中危命令，需要记录并提醒
- **LOW (🟢)**: 低危命令，正常执行

---

## 极高危命令 (CRITICAL) — 绝对禁止

### 磁盘格式化

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `format` | Windows | 格式化磁盘分区，数据完全丢失 |
| `format C:` | Windows | 格式化系统盘，系统无法启动 |
| `diskpart` | Windows | 磁盘分区工具，可删除/修改分区 |
| `mkfs.*` | Linux | 创建文件系统，格式化分区 |
| `mkfs.ext4` | Linux | 格式化为 ext4 |
| `mkfs.ntfs` | Linux | 格式化为 NTFS |
| `mkfs.fat` | Linux | 格式化 FAT |
| `newfs_*` | macOS | 创建文件系统 |
| `newfs_msdos` | macOS | 格式化 MS-DOS |
| `newfs_hfs` | macOS | 格式化 HFS |
| `newfs_apfs` | macOS | 格式化 APFS |

### 磁盘直接写入

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `dd if=* of=/dev/sd*` | Linux | 直接写入磁盘设备，可破坏分区表 |
| `dd if=* of=/dev/hd*` | Linux | 直接写入 IDE 磁盘 |
| `dd if=* of=/dev/nvme*` | Linux | 直接写入 NVMe 磁盘 |
| `dd if=* of=/dev/disk*` | macOS | 直接写入磁盘 |
| `dd if=* of=/dev/rdisk*` | macOS | 直接写入原始磁盘 |
| `dd if=/dev/zero of=*` | All | 清零写入，数据丢失 |
| `dd if=/dev/random of=*` | All | 随机写入，数据破坏 |

### 系统目录删除

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `rm -rf /` | Unix | 删除整个文件系统 |
| `rm -rf /*` | Unix | 删除根目录下所有内容 |
| `rm -rf ~` | Unix | 删除用户主目录 |
| `rm -rf $HOME` | Unix | 删除用户主目录 |
| `rd /s /q C:\` | Windows | 删除 C 盘 |
| `rd /s /q C:\Windows` | Windows | 删除 Windows 目录 |
| `del /f /s /q C:\Windows\*` | Windows | 删除系统文件 |
| `deltree` | Windows | 删除目录树（旧命令） |

### 分区表操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `fdisk` | Linux | 分区表编辑 |
| `cfdisk` | Linux | 交互式分区编辑 |
| `parted` | Linux | 分区编辑 |
| `gparted` | Linux | 图形分区编辑 |
| `diskutil` | macOS | 磁盘工具命令行 |
| `diskutil eraseDisk` | macOS | 擦除磁盘 |
| `diskutil partitionDisk` | macOS | 重新分区 |

### 系统服务关键操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `systemctl stop systemd-*` | Linux | 停止核心系统服务 |
| `systemctl disable systemd-*` | Linux | 禁用核心系统服务 |
| `sc stop csrss` | Windows | 停止关键系统进程 |
| `sc stop smss` | Windows | 停止会话管理器 |
| `sc stop wininit` | Windows | 停止 Windows 初始化 |
| `kill -9 1` | Linux | 杀死 init 进程 |
| `kill -9 pidof systemd` | Linux | 杀死 systemd |

### 内核模块操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `insmod` | Linux | 加载内核模块 |
| `rmmod` | Linux | 卸载内核模块 |
| `modprobe -r` | Linux | 卸载模块及依赖 |
| `kextload` | macOS | 加载内核扩展 |
| `kextunload` | macOS | 卸载内核扩展 |

### 注册表关键操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `reg delete HKLM\*` | Windows | 删除本地机器注册表 |
| `reg delete HKLM\SYSTEM` | Windows | 删除系统配置 |
| `reg delete HKLM\SOFTWARE` | Windows | 删除软件配置 |
| `reg delete "HKLM\BCD00000000"` | Windows | 删除启动配置 |

### 安全软件禁用

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| 停止杀毒软件服务 | All | 系统暴露于威胁 |
| 卸载安全软件 | All | 移除系统保护 |
| 禁用防火墙 | All | 网络暴露 |
| 禁用 Windows Defender | Windows | 移除内置保护 |

---

## 高危命令 (HIGH) — 需要明确确认

### 文件删除

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `rm -rf [path]` | Unix | 递归强制删除 |
| `rm -r [path]` | Unix | 递归删除 |
| `rm -f [path]` | Unix | 强制删除 |
| `rd /s [path]` | Windows | 递归删除目录 |
| `rmdir /s [path]` | Windows | 递归删除目录 |
| `del /s [path]` | Windows | 递归删除文件 |
| `del /f [path]` | Windows | 强制删除 |
| `rmdir -p` | Unix | 递归删除父目录 |
| `unlink` | Unix | 删除文件 |
| `shred` | Linux | 安全删除（覆写） |
| `srm` | Unix | 安全删除 |
| `erase` | Windows | 删除文件 |

### 批量删除模式

| 模式 | 平台 | 风险描述 |
|------|------|----------|
| `rm -rf *` | Unix | 删除当前目录所有内容 |
| `rm -rf .*` | Unix | 删除隐藏文件 |
| `del /q *` | Windows | 安静模式删除所有 |
| `del /s /q *` | Windows | 递归安静删除 |

### 软件安装/卸载

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `brew install` | macOS | 安装软件 |
| `brew uninstall` | macOS | 卸载软件 |
| `brew remove` | macOS | 移除软件 |
| `apt install` | Linux | 安装软件包 |
| `apt remove` | Linux | 移除软件包 |
| `apt purge` | Linux | 彻底清除软件包 |
| `apt autoremove` | Linux | 自动移除依赖 |
| `yum install` | Linux | 安装软件包 |
| `yum remove` | Linux | 移除软件包 |
| `dnf install` | Linux | 安装软件包 |
| `dnf remove` | Linux | 移除软件包 |
| `pacman -S` | Linux | 安装软件包 |
| `pacman -R` | Linux | 移除软件包 |
| `pacman -Rs` | Linux | 移除软件包及依赖 |
| `winget install` | Windows | 安装软件 |
| `winget uninstall` | Windows | 卸载软件 |
| `choco install` | Windows | 安装软件 |
| `choco uninstall` | Windows | 卸载软件 |
| `scoop install` | Windows | 安装软件 |
| `scoop uninstall` | Windows | 卸载软件 |
| `msiexec /i` | Windows | 安装 MSI |
| `msiexec /x` | Windows | 卸载 MSI |
| `msiexec /fa` | Windows | 强制重新安装 |
| `npm install -g` | All | 全局安装 Node 包 |
| `npm uninstall -g` | All | 全局卸载 Node 包 |
| `pip install` | All | 安装 Python 包 |
| `pip uninstall` | All | 卸载 Python 包 |
| `gem install` | All | 安装 Ruby 包 |
| `gem uninstall` | All | 卸载 Ruby 包 |
| `cargo install` | All | 安装 Rust 包 |
| `cargo uninstall` | All | 卸载 Rust 包 |

### 系统配置修改

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| 修改 `/etc/hosts` | Unix | 修改主机解析 |
| 修改 `C:\Windows\System32\drivers\etc\hosts` | Windows | 修改主机解析 |
| `netsh advfirewall` | Windows | 修改防火墙规则 |
| `netsh firewall` | Windows | 修改防火墙（旧） |
| `ufw enable/disable` | Linux | 启用/禁用防火墙 |
| `ufw allow/deny` | Linux | 修改防火墙规则 |
| `iptables` | Linux | 修改防火墙规则 |
| `ip6tables` | Linux | 修改 IPv6 防火墙 |
| `nft` | Linux | 修改防火墙规则 |
| `firewalld` | Linux | 修改防火墙 |

### 计划任务操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `schtasks /create` | Windows | 创建计划任务 |
| `schtasks /delete` | Windows | 删除计划任务 |
| `schtasks /change` | Windows | 修改计划任务 |
| `schtasks /run` | Windows | 运行计划任务 |
| `crontab -e` | Unix | 编辑 cron 任务 |
| `crontab -r` | Unix | 删除所有 cron 任务 |
| `crontab [file]` | Unix | 替换 cron 任务 |
| `launchctl load` | macOS | 加载 launchd 任务 |
| `launchctl unload` | macOS | 卸载 launchd 任务 |
| `launchctl start` | macOS | 启动服务 |
| `launchctl stop` | macOS | 停止服务 |

### 权限修改

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `chmod -R` | Unix | 递归修改权限 |
| `chmod 777` | Unix | 完全开放权限 |
| `chmod 000` | Unix | 完全禁止访问 |
| `chown -R` | Unix | 递归修改所有者 |
| `chgrp -R` | Unix | 递归修改组 |
| `icacls` | Windows | 修改 ACL |
| `icacls /grant` | Windows | 授予权限 |
| `icacls /deny` | Windows | 拒绝权限 |
| `icacls /remove` | Windows | 移除权限 |
| `setfacl` | Linux | 修改 ACL |
| `attrib` | Windows | 修改文件属性 |
| `attrib -r -s -h` | Windows | 移除保护属性 |

### 系统 PATH 修改

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `setx PATH` | Windows | 永久修改 PATH |
| 修改 `/etc/paths` | macOS | 修改系统 PATH |
| 修改 `/etc/environment` | Linux | 修改环境变量 |
| 修改 `~/.bashrc` PATH | Unix | 修改用户 PATH |
| 修改 `~/.zshrc` PATH | Unix | 修改用户 PATH |
| 修改 `~/.profile` PATH | Unix | 修改用户 PATH |

### 用户账户操作

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `useradd` | Linux | 添加用户 |
| `userdel` | Linux | 删除用户 |
| `usermod` | Linux | 修改用户 |
| `groupadd` | Linux | 添加组 |
| `groupdel` | Linux | 删除组 |
| `passwd` | Unix | 修改密码 |
| `net user` | Windows | 用户管理 |
| `net localgroup` | Windows | 组管理 |
| `net accounts` | Windows | 账户策略 |
| `dscl` | macOS | 目录服务 |
| `sysadminctl` | macOS | 系统管理员 |

### 服务管理

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `systemctl start` | Linux | 启动服务 |
| `systemctl stop` | Linux | 停止服务 |
| `systemctl restart` | Linux | 重启服务 |
| `systemctl enable` | Linux | 启用服务 |
| `systemctl disable` | Linux | 禁用服务 |
| `service start` | Linux | 启动服务 |
| `service stop` | Linux | 停止服务 |
| `sc start` | Windows | 启动服务 |
| `sc stop` | Windows | 停止服务 |
| `sc config` | Windows | 配置服务 |
| `sc delete` | Windows | 删除服务 |

---

## 中危命令 (MEDIUM) — 记录并提醒

### 文件覆写

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `>` (重定向) | All | 覆写文件 |
| `>>` (追加重定向) | All | 追加到文件 |
| `tee` | Unix | 输出到文件 |
| `tee -a` | Unix | 追加到文件 |
| `sponge` | Unix | 就地编辑 |
| `sed -i` | Unix | 就地编辑 |
| `perl -i` | Unix | 就地编辑 |
| `awk` 输出重定向 | Unix | 处理并输出 |

### 网络下载

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `curl -O` | All | 下载文件 |
| `curl -o` | All | 下载到指定文件 |
| `curl -L` | All | 跟随重定向下载 |
| `wget` | All | 下载文件 |
| `wget -O` | All | 下载到指定文件 |
| `wget --no-check-certificate` | All | 忽略证书下载 |
| `Invoke-WebRequest` | PowerShell | 下载 |
| `Invoke-RestMethod` | PowerShell | REST 请求 |
| `iwr` | PowerShell | 简写下载 |
| `irm` | PowerShell | 简写 REST |
| `Start-BitsTransfer` | PowerShell | BITS 下载 |
| `aria2c` | All | 多线程下载 |
| `axel` | All | 多线程下载 |

### 远程执行

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `curl * \| bash` | Unix | 下载并执行 |
| `curl * \| sh` | Unix | 下载并执行 |
| `wget -O - * \| bash` | Unix | 下载并执行 |
| `irm * \| iex` | PowerShell | 下载并执行 |
| `iex (iwr *)` | PowerShell | 下载并执行 |
| `Invoke-Expression` | PowerShell | 执行字符串 |
| `eval` | Unix | 执行字符串 |
| `source <(curl *)` | Unix | 下载并 source |

### 压缩/解压

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `tar -x` | Unix | 解压 |
| `tar -xf` | Unix | 解压文件 |
| `tar -xzf` | Unix | 解压 gzip |
| `tar -xjf` | Unix | 解压 bzip2 |
| `unzip` | All | 解压 zip |
| `unzip -o` | All | 覆盖解压 |
| `7z x` | All | 解压 |
| `rar x` | All | 解压 rar |
| `gzip -d` | Unix | 解压 gzip |
| `bzip2 -d` | Unix | 解压 bzip2 |
| `xz -d` | Unix | 解压 xz |
| `Expand-Archive` | PowerShell | 解压 |
| `Compress-Archive` | PowerShell | 压缩 |

### 环境变量修改

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `export` | Unix | 设置环境变量 |
| `set` | Unix/Windows | 设置变量 |
| `setx` | Windows | 永久设置变量 |
| `$env:VAR=` | PowerShell | 设置环境变量 |
| `[Environment]::SetEnvironmentVariable` | PowerShell | 设置环境变量 |
| `unset` | Unix | 删除变量 |

### 进程管理

| 命令 | 平台 | 风险描述 |
|------|------|----------|
| `kill` | Unix | 终止进程 |
| `killall` | Unix | 终止所有匹配进程 |
| `pkill` | Unix | 按模式终止 |
| `xkill` | Unix | 图形终止 |
| `taskkill` | Windows | 终止任务 |
| `taskkill /f` | Windows | 强制终止 |
| `taskkill /im` | Windows | 按映像终止 |
| `Stop-Process` | PowerShell | 停止进程 |
| `Stop-Process -Force` | PowerShell | 强制停止 |

---

## 低危命令 (LOW) — 正常执行

### 文件查询

| 命令 | 平台 | 说明 |
|------|------|------|
| `ls` | Unix | 列出目录 |
| `ll` | Unix | 详细列表（别名） |
| `dir` | Windows | 列出目录 |
| `Get-ChildItem` | PowerShell | 列出项目 |
| `gci` | PowerShell | 简写 |
| `find` | Unix | 查找文件 |
| `findstr` | Windows | 查找字符串 |
| `grep` | Unix | 文本搜索 |
| `Select-String` | PowerShell | 文本搜索 |
| `sls` | PowerShell | 简写 |

### 文件读取

| 命令 | 平台 | 说明 |
|------|------|------|
| `cat` | Unix | 显示文件内容 |
| `less` | Unix | 分页查看 |
| `more` | All | 分页查看 |
| `head` | Unix | 查看开头 |
| `tail` | Unix | 查看结尾 |
| `Get-Content` | PowerShell | 读取内容 |
| `gc` | PowerShell | 简写 |
| `type` | Windows | 显示文件 |

### 系统信息查询

| 命令 | 平台 | 说明 |
|------|------|------|
| `uname` | Unix | 系统信息 |
| `hostname` | All | 主机名 |
| `whoami` | All | 当前用户 |
| `id` | Unix | 用户 ID |
| `pwd` | Unix | 当前目录 |
| `cd` | All | 切换目录 |
| `echo` | All | 输出文本 |
| `date` | All | 日期时间 |
| `ver` | Windows | 版本信息 |
| `systeminfo` | Windows | 系统信息 |
| `Get-ComputerInfo` | PowerShell | 计算机信息 |

###  harmless 工具

| 命令 | 平台 | 说明 |
|------|------|------|
| `jq` | All | JSON 处理 |
| `cut` | Unix | 文本切割 |
| `sort` | Unix | 排序 |
| `uniq` | Unix | 去重 |
| `wc` | Unix | 字数统计 |
| `tr` | Unix | 字符转换 |
| `awk` | Unix | 文本处理（只读） |
| `sed` | Unix | 流编辑（只读） |
| `xargs` | Unix | 参数传递 |

---

## 命令组合风险评估

### 管道组合

管道命令的风险取各组件的最高风险等级：

```bash
# 示例：中危 + 低危 = 中危
curl https://example.com | jq .  # MEDIUM (curl)

# 示例：高危 + 低危 = 高危
curl https://example.com | bash  # CRITICAL (远程执行)
```

### 命令链

分号、&&、|| 连接的命令链风险取各命令的最高风险等级：

```bash
# 示例：低危 && 高危 = 高危
cd /tmp && rm -rf important  # HIGH

# 示例：低危 ; 极高危 = 极高危
echo "test" ; rm -rf /  # CRITICAL
```

### 子 shell

子 shell 中的命令需要单独评估：

```bash
# 需要评估子 shell 内容
$(command)
`command`
```

---

## 快速查询表

| 命令类别 | 示例 | 风险等级 |
|----------|------|----------|
| 格式化磁盘 | `format`, `mkfs` | CRITICAL |
| 删除根目录 | `rm -rf /` | CRITICAL |
| 直接写磁盘 | `dd of=/dev/sd*` | CRITICAL |
| 删除用户文件 | `rm -rf ~/file` | HIGH |
| 批量删除 | `rm -rf *` | HIGH |
| 安装软件 | `brew install` | HIGH |
| 修改 hosts | 编辑 hosts 文件 | HIGH |
| 修改防火墙 | `ufw`, `iptables` | HIGH |
| 下载执行 | `curl \| bash` | MEDIUM |
| 网络下载 | `curl`, `wget` | MEDIUM |
| 文件覆写 | `> file` | MEDIUM |
| 环境变量 | `export VAR=` | MEDIUM |
| 列出目录 | `ls`, `dir` | LOW |
| 读取文件 | `cat`, `Get-Content` | LOW |
| 系统信息 | `uname`, `whoami` | LOW |
