# 向日葵主机上下线监控工具

将向日葵的主机上下线通知实时转发到你的微信（基于 PushPlus 免费推送）。

## 📦 文件清单

```
向日葵监控/
├── sunlogin_monitor.py      # 监控主脚本（核心程序）
├── config.ini               # 配置文件
├── README.md                # 本文件
└── last_notify_id.txt       # 记录文件（自动生成，勿删）
```

## 🚀 快速开始

### 1. 配置 PushPlus Token
打开 `config.ini` 文件，填入你的 PushPlus Token：
```ini
[通知设置]
Token = 你的PushPlus_Token
CheckInterval = 5
```

获取 Token 步骤：
1. 访问 https://www.pushplus.plus/，微信扫码登录/注册
2. 在官网首页获取「一对一发送」的 Token 复制粘贴到配置文件
3. **重要**：需完成实名认证，否则无法发送（错误码 905）：https://verify.pushplus.plus

### 2. 运行程序
```bash
python sunlogin_monitor.py
```

或直接双击运行已打包的 `SunloginMonitor.exe`

### 3. 接收通知
当向日葵主机上线/下线时，微信会收到类似这样的通知：
- 🔴 主机下线：`设备名 offline`
- 🟢 主机上线：`设备名 online`

## 📋 配置说明

### config.ini
```ini
[通知设置]
Token = xxxxxxxxxxxxxxxxxxxx      # 必填（PushPlus 一对一 Token）
CheckInterval = 5                  # 检测间隔（秒）

[数据库设置]
DBPath = C:\Users\{用户名}\AppData\Local\Microsoft\Windows\Notifications\wpndatabase.db
AppID = oray.sunlogin          # 向日葵应用标识（稳定不变，自动匹配）
HandlerId = 90                 # 兜底值（无法自动匹配时使用，可留空）
```

> **关于 HandlerId 的自动探测**：Windows 通知数据库里的 `HandlerId`（如 90）是系统按启动顺序分配的整数，**换机器/重装系统后可能变化**。脚本通过更稳定的 `AppID`（`oray.sunlogin`）自动查询出正确的 HandlerId，无需手动关心数字。

### 监控其他程序（可选）
脚本不只监控向日葵，任何会弹 Windows Toast 通知的程序都能监控。运行以下命令查看当前机器可监控的程序：
```bash
python sunlogin_monitor.py --list
```
会显示类似：
```
 HandlerId |    通知数 | AppId
        90 |     17 | oray.sunlogin
        92 |      1 | Microsoft.Explorer.Notification.{A9827327-...}
```
把你想要的程序 `AppId` 填入 `config.ini` 的 `AppID` 字段，即可监控该程序的通知。

### 开机自启动（可选）
1. 按 `Win + R`，输入 `shell:startup`
2. 回车打开启动文件夹
3. 将 `SunloginMonitor.exe` 的快捷方式复制进去

## 🔧 技术原理

1. **数据源**：读取 Windows 通知中心数据库
   - 路径：`C:\Users\{用户名}\AppData\Local\Microsoft\Windows\Notifications\wpndatabase.db`
   - 向日葵标识：`NotificationHandler.PrimaryId = oray.sunlogin`（稳定，自动匹配）
   - 数字 `HandlerId`（90）由系统分配，脚本按 `AppID` 自动探测

2. **通知格式**：解析 XML 格式的 Toast 通知
   ```xml
   <toast>
     <visual>
       <binding template="ToastGeneric">
         <text>设备下线提醒</text>
         <text>服务器名称下线啦</text>
       </binding>
     </visual>
   </toast>
   ```

3. **转发**：提取设备名和状态，翻译为英文，通过 **PushPlus (www.pushplus.plus)** 发送到微信

## 🚀 发布版本

- **v1.3**：从 Server酱 迁移到 PushPlus (v1.3 正式版，2026-09 验证通过)
- **v1.1**：支持通知格式改为 `设备名称 online/offline`

## ⚠️ 注意事项

- ⚠️ 运行期间不要关闭命令行窗口
- ⚠️ 不要删除 `last_notify_id.txt` 文件（会重复发送通知）
- ⚠️ Windows 系统必须安装了向日葵客户端并配置了被控主机
- ⚠️ 需配置 `wpndatabase.db` 文件路径正确（根据实际 Windows 用户名）

## 📝 更新日志

**v1.3 - 2026-09-01**
- ✅ Server酱 收费，迁移至 PushPlus（免费微信推送）
- ✅ 配置项由 `SendKey` 改为 `Token`
- ✅ 已验证实名认证 PushPlus 账号推送功能正常

**v1.2**
- ✅ 修复 config.ini UTF-8 BOM 导致解析失败

**v1.1**
- ✅ 支持读取 Windows 通知中心数据库
- ✅ 自动识别向日葵主机上下线通知
- ✅ 翻译为英文发送到微信（解决中文编码问题）
- ✅ 支持配置文件，无需修改代码
- ✅ 自动记录处理进度，避免重复发送