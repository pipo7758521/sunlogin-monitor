# 向日葵主机上下线监控工具

将向日葵的主机上下线通知实时转发到你的微信。

## 📦 文件清单

```
向日葵监控/
├── sunlogin_monitor.py      # 监控主脚本（核心程序）
├── config.ini               # 配置文件（已预配置好）
├── 启动监控.bat             # 双击运行（推荐）
├── 使用说明.txt             # 使用指南
├── README.md                # 本文件
└── last_notify_id.txt       # 记录文件（自动生成，勿删）
```

## 🚀 快速开始

### 1. 检查配置
打开 `config.ini` 文件，确认 SendKey 是否正确：
```ini
[通知设置]
SendKey = [REDACTED-SendKey]
CheckInterval = 5
```
**SendKey 已预填充**，如需更换可访问 https://sct.ftqq.com/ 获取。

### 2. 运行程序
双击 `启动监控.bat` 即可启动。

控制台会显示：
```
=======================================================
向日葵主机上下线监控 (可配置版)
=======================================================
配置文件: config.ini
SendKey: SCT403***
数据库: C:\...\wpndatabase.db
检测间隔: 5 秒
-------------------------------------------------------
运行中，按 Ctrl+C 停止...
```

### 3. 接收通知
当向日葵主机上线/下线时，微信会收到类似这样的通知：
- 🔴 主机下线：`Sunlogin Device OFFLINE` + `Device: 服务器名称`
- 🟢 主机上线：`Sunlogin Device ONLINE` + `Device: 服务器名称`

## 📋 配置说明

### config.ini
```ini
[通知设置]
SendKey = 你的SendKey        # 必填
CheckInterval = 5             # 检测间隔（秒）

[数据库设置]
DBPath = C:\Users\{用户名}\AppData\Local\Microsoft\Windows\Notifications\wpndatabase.db
HandlerId = 90                # 向日葵应用的ID
```

### 开机自启动（可选）
1. 按 `Win + R`，输入 `shell:startup`
2. 回车打开启动文件夹
3. 将 `启动监控.bat` 的快捷方式复制进去

## 🔧 技术原理

1. **数据源**：读取 Windows 通知中心数据库
   - 路径：`C:\Users\...\AppData\Local\Microsoft\Windows\Notifications\wpndatabase.db`
   - 向日葵 HandlerId: 90

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

3. **转发**：提取设备名和状态，翻译为英文发送到微信

## ⚠️ 注意事项

- ✅ 确保已安装 Python 3.x
- ✅ 确保已安装 requests 库：`pip install requests`
- ⚠️ 运行期间不要关闭命令行窗口
- ⚠️ 不要删除 `last_notify_id.txt` 文件（会重复发送通知）
- ⚠️ Windows 系统必须安装了向日葵客户端并配置了被控主机

## ✅ 测试结果

已验证可正常监控 20 台主机的上下线通知：

| 时间 | 设备 | 事件 | 通知 |
|------|------|------|------|
| 08-24 09:27:06 | Device-1 | 下线 | ✅ OFFLINE |
| 08-24 09:27:13 | Device-1 | 上线 | ✅ ONLINE |
| 08-24 09:28:49 | Device-2 | 下线 | ✅ OFFLINE |

## 📝 更新日志

**v1.0 (2025-08-24)**
- ✅ 支持读取 Windows 通知中心数据库
- ✅ 自动识别向日葵主机上下线通知
- ✅ 翻译为英文发送到微信（解决中文编码问题）
- ✅ 支持配置文件，无需修改代码
- ✅ 自动记录处理进度
- ✅ 支持开机自启动
