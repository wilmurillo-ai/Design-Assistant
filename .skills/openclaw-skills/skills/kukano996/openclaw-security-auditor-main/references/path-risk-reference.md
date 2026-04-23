# 路径风险评估参考

本文档包含完整的路径风险分类，用于安全审计时快速查询。

## 风险等级定义

- **CRITICAL (🔴)**: 系统关键路径，操作可能导致系统无法启动或严重损坏
- **HIGH (🟠)**: 用户敏感路径，操作可能导致数据丢失或隐私泄露
- **MEDIUM (🟡)**: 需谨慎处理的路径
- **LOW (🟢)**: 工作区路径，用户已授权的操作空间

---

## Windows 系统关键路径 (CRITICAL)

### 系统目录
```
C:\Windows
C:\Windows\*
C:\Windows\System32
C:\Windows\System32\*
C:\Windows\SysWOW64
C:\Windows\SysWOW64\*
C:\Windows\WinSxS
C:\Windows\WinSxS\*
C:\Windows\Boot
C:\Windows\Boot\*
C:\Windows\Registration
C:\Windows\Registration\*
C:\Windows\security
C:\Windows\security\*
C:\Windows\ServiceProfiles
C:\Windows\ServiceProfiles\*
```

### 程序目录
```
C:\Program Files
C:\Program Files\*
C:\Program Files (x86)
C:\Program Files (x86)\*
C:\ProgramData
C:\ProgramData\*
```

### 系统根目录
```
C:\
C:\$Recycle.Bin
C:\$Recycle.Bin\*
C:\Recovery
C:\Recovery\*
C:\System Volume Information
C:\System Volume Information\*
C:\Boot
C:\Boot\*
```

### 注册表路径
```
HKEY_CLASSES_ROOT
HKEY_CURRENT_CONFIG
HKEY_CURRENT_USER
HKEY_LOCAL_MACHINE
HKEY_USERS
HKCR
HKCC
HKCU
HKLM
HKU
```

### 环境变量展开后的关键路径
```
%SystemDrive%\*
%SystemRoot%\*
%WinDir%\*
%ProgramFiles%\*
%ProgramFiles(x86)%\*
%ProgramData%\*
%AllUsersProfile%\*
%Public%\*
```

---

## macOS 系统关键路径 (CRITICAL)

### 系统目录
```
/System
/System/*
/System/Library
/System/Library/*
/System/Library/CoreServices
/System/Library/CoreServices/*
/System/Library/Extensions
/System/Library/Extensions/*
/System/Library/LaunchDaemons
/System/Library/LaunchDaemons/*
/System/Library/StartupItems
/System/Library/StartupItems/*
/System/Volumes
/System/Volumes/*
/System/Volumes/Data
/System/Volumes/Data/*
```

### 系统二进制
```
/bin
/bin/*
/sbin
/sbin/*
/usr/bin
/usr/bin/*
/usr/sbin
/usr/sbin/*
/usr/lib
/usr/lib/*
/usr/libexec
/usr/libexec/*
/usr/local/bin
/usr/local/sbin
```

### 系统配置
```
/etc
/etc/*
/etc/defaults
/etc/defaults/*
/etc/pam.d
/etc/pam.d/*
/etc/ssh
/etc/ssh/*
/etc/sudoers
/etc/sudoers.d
/etc/sudoers.d/*
/private/etc
/private/etc/*
/private/var/db
/private/var/db/*
/private/var/root
/private/var/root/*
```

### 内核扩展
```
/Library/Extensions
/Library/Extensions/*
/System/Library/Extensions
/System/Library/Extensions/*
```

---

## Linux 系统关键路径 (CRITICAL)

### 系统二进制
```
/bin
/bin/*
/sbin
/sbin/*
/usr/bin
/usr/bin/*
/usr/sbin
/usr/sbin/*
/usr/local/bin
/usr/local/bin/*
/usr/local/sbin
/usr/local/sbin/*
```

### 系统库
```
/lib
/lib/*
/lib32
/lib32/*
/lib64
/lib64/*
/libx32
/libx32/*
/usr/lib
/usr/lib/*
/usr/lib32
/usr/lib32/*
/usr/lib64
/usr/lib64/*
/usr/libexec
/usr/libexec/*
/usr/local/lib
/usr/local/lib/*
```

### 系统配置
```
/etc
/etc/*
/etc/cron.d
/etc/cron.d/*
/etc/cron.daily
/etc/cron.daily/*
/etc/cron.hourly
/etc/cron.hourly/*
/etc/cron.monthly
/etc/cron.monthly/*
/etc/cron.weekly
/etc/cron.weekly/*
/etc/default
/etc/default/*
/etc/init.d
/etc/init.d/*
/etc/rc.d
/etc/rc.d/*
/etc/security
/etc/security/*
/etc/sudoers
/etc/sudoers.d
/etc/sudoers.d/*
/etc/ssh
/etc/ssh/*
/etc/systemd
/etc/systemd/*
```

### 虚拟文件系统
```
/proc
/proc/*
/sys
/sys/*
/dev
/dev/*
/run
/run/*
/boot
/boot/*
```

---

## 用户敏感路径 (HIGH)

### SSH 密钥和配置
```
~/.ssh
~/.ssh/*
%USERPROFILE%\.ssh
%USERPROFILE%\.ssh\*
$HOME/.ssh
$HOME/.ssh/*
```

### AWS 凭证
```
~/.aws
~/.aws/*
%USERPROFILE%\.aws
%USERPROFILE%\.aws\*
$HOME/.aws
$HOME/.aws/*
~/.aws/credentials
~/.aws/config
```

### 通用配置文件
```
~/.config
~/.config/*
%APPDATA%\*
%LOCALAPPDATA%\*
$HOME/.config
$HOME/.config/*
```

### Shell 配置
```
~/.bashrc
~/.bash_profile
~/.bash_login
~/.bash_logout
~/.bash_history
~/.zshrc
~/.zprofile
~/.zlogin
~/.zlogout
~/.zsh_history
~/.profile
~/.shrc
~/.cshrc
~/.tcshrc
~/.inputrc
%USERPROFILE%\.bashrc
%USERPROFILE%\.bash_profile
%USERPROFILE%\.zshrc
%USERPROFILE%\.profile
```

### 环境变量文件
```
~/.env
~/.env.local
~/.env.production
~/.env.development
~/.bash_env
%USERPROFILE%\.env
$HOME/.env
```

### 密码管理器数据
```
~/.password-store
~/.password-store/*
~/.keepass
~/.keepass/*
~/.1password
~/.1password/*
~/.bitwarden
~/.bitwarden/*
%APPDATA%\1Password
%APPDATA%\1Password\*
%APPDATA%\Bitwarden
%APPDATA%\Bitwarden\*
```

### 浏览器数据
```
~/.mozilla
~/.mozilla/*
~/.config/google-chrome
~/.config/google-chrome/*
~/.config/chromium
~/.config/chromium/*
~/.config/BraveSoftware
~/.config/BraveSoftware/*
~/.config/Microsoft
~/.config/Microsoft/*
~/.config/opera
~/.config/opera/*
~/.config/vivaldi
~/.config/vivaldi/*
~/.safari
~/.safari/*
%APPDATA%\Mozilla\Firefox
%APPDATA%\Mozilla\Firefox\*
%LOCALAPPDATA%\Google\Chrome
%LOCALAPPDATA%\Google\Chrome\*
%LOCALAPPDATA%\Microsoft\Edge
%LOCALAPPDATA%\Microsoft\Edge\*
%APPDATA%\Opera Software
%APPDATA%\Opera Software\*
%LOCALAPPDATA%\BraveSoftware
%LOCALAPPDATA%\BraveSoftware\*
```

### 邮件客户端数据
```
~/.thunderbird
~/.thunderbird/*
~/.var/app/org.mozilla.Thunderbird
~/.var/app/org.mozilla.Thunderbird/*
~/Library/Mail
~/Library/Mail/*
%APPDATA%\Thunderbird
%APPDATA%\Thunderbird\*
```

### 聊天记录
```
~/.config/Signal
~/.config/Signal/*
~/.config/telegram-desktop
~/.config/telegram-desktop/*
~/.config/discord
~/.config/discord/*
%APPDATA%\Signal
%APPDATA%\Signal\*
%APPDATA%\Telegram Desktop
%APPDATA%\Telegram Desktop\*
%APPDATA%\Discord
%APPDATA%\Discord\*
```

### 加密货币钱包
```
~/.bitcoin
~/.bitcoin/*
~/.ethereum
~/.ethereum/*
~/.config/Electron Cash
~/.config/Electron Cash/*
%APPDATA%\Bitcoin
%APPDATA%\Bitcoin\*
%APPDATA%\Ethereum
%APPDATA%\Ethereum\*
```

### 开发工具配置
```
~/.gitconfig
~/.git-credentials
~/.gitignore_global
~/.docker
~/.docker/*
~/.kube
~/.kube/*
~/.npmrc
~/.yarnrc
~/.pypirc
~/.pip
~/.pip/*
~/.gemrc
~/.m2
~/.m2/*
~/.gradle
~/.gradle/*
~/.cargo
~/.cargo/*
~/.rustup
~/.rustup/*
~/.nuget
~/.nuget/*
%USERPROFILE%\.gitconfig
%USERPROFILE%\.git-credentials
%USERPROFILE%\.docker
%USERPROFILE%\.docker\*
%USERPROFILE%\.kube
%USERPROFILE%\.kube\*
```

### 数据库文件
```
~/.mysql_history
~/.psql_history
~/.sqlite_history
~/.rediscli_history
~/.mongorc.js
~/.pgpass
~/my.cnf
~/.my.cnf
%APPDATA%\MySQL
%APPDATA%\MySQL\*
%APPDATA%\PostgreSQL
%APPDATA%\PostgreSQL\*
```

---

## 用户主目录 (MEDIUM)

### 主目录根（非敏感子目录）
```
~/*
%USERPROFILE%\*
$HOME/*
~/Documents/*
~/Downloads/*
~/Desktop/*
~/Pictures/*
~/Music/*
~/Videos/*
%USERPROFILE%\Documents\*
%USERPROFILE%\Downloads\*
%USERPROFILE%\Desktop\*
%USERPROFILE%\Pictures\*
%USERPROFILE%\Music\*
%USERPROFILE%\Videos\*
```

**注意**: 主目录根级别的操作需要谨慎，但非敏感子目录的操作风险较低。

---

## 工作区路径 (LOW)

### 当前工作目录
```
./*
./
..
../
```

**注意**: 工作区路径是用户明确授权的操作空间，正常操作无需额外审计。

---

## 路径匹配规则

### 通配符说明

- `*` - 匹配任意字符（不包括路径分隔符）
- `**` - 匹配任意层级目录
- `?` - 匹配单个字符

### 匹配优先级

1. 精确匹配 > 通配符匹配
2. 最长匹配优先
3. 系统路径 > 用户路径 > 工作区路径

### 环境变量展开

在评估路径风险前，必须先展开环境变量：

```bash
# 需要展开的环境变量
Windows: %VAR%, $env:VAR
Unix: $VAR, ${VAR}, ~ (展开为 $HOME)
```

### 路径规范化

在评估前必须进行路径规范化：

1. 展开符号链接
2. 解析 `..` 和 `.`
3. 统一路径分隔符
4. 转换为绝对路径

---

## 快速查询表

| 路径类型 | 示例 | 风险等级 |
|----------|------|----------|
| 系统根目录 | `/`, `C:\` | CRITICAL |
| 系统二进制 | `/bin`, `/usr/bin`, `C:\Windows\System32` | CRITICAL |
| 系统配置 | `/etc`, `C:\Windows\System32\config` | CRITICAL |
| 用户 SSH | `~/.ssh` | HIGH |
| 用户 AWS | `~/.aws` | HIGH |
| 浏览器数据 | `~/.config/google-chrome` | HIGH |
| 密码管理器 | `~/.password-store` | HIGH |
| 用户文档 | `~/Documents` | MEDIUM |
| 用户下载 | `~/Downloads` | MEDIUM |
| 工作区 | `./workspace` | LOW |
