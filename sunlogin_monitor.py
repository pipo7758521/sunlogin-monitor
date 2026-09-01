# -*- coding: utf-8 -*-
"""
向日葵主机上下线监控 - 可配置版
通知渠道：PushPlus（免费微信推送）
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import re
import time
import os
import requests
import configparser
from datetime import datetime

# 获取脚本所在目录
def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

SCRIPT_DIR = get_script_dir()
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.ini")
STATE_FILE = os.path.join(SCRIPT_DIR, "last_notify_id.txt")

# 向日葵 AppId（稳定标识，不随 RecordId 变化）
SUNLOGIN_APPID = "oray.sunlogin"

def load_config():
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        config['通知设置'] = {
            'Token': '请在此填入你的PushPlus Token',
            'CheckInterval': '5'
        }
        config['数据库设置'] = {
            'DBPath': r'C:\Users\{用户名}\AppData\Local\Microsoft\Windows\Notifications\wpndatabase.db',
            # AppId 更稳定，优先使用；留空则回退到 HandlerId
            'AppId': SUNLOGIN_APPID,
            'HandlerId': '90'
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            config.write(f)
        print(f"已创建配置文件: {CONFIG_FILE}")
        print("请修改配置文件后重新运行脚本")
        return None

    config.read(CONFIG_FILE, encoding='utf-8-sig')

    return {
        'token': config.get('通知设置', 'Token', fallback=''),
        'check_interval': config.getint('通知设置', 'CheckInterval', fallback=5),
        'db_path': config.get('数据库设置', 'DBPath', fallback=''),
        'app_id': config.get('数据库设置', 'AppId', fallback=SUNLOGIN_APPID),
        'handler_id': config.getint('数据库设置', 'HandlerId', fallback=90)
    }

def resolve_handler_id(db_path, app_id, fallback_id):
    """根据 PrimaryId 自动查出向日葵的 RecordId。
    找不到时回退到配置的 HandlerId（兼容旧版配置）。"""
    if not app_id:
        return fallback_id, False
    try:
        conn = sqlite3.connect("file:" + db_path + "?mode=ro", uri=True)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT RecordId FROM NotificationHandler WHERE PrimaryId=?",
            (app_id,)
        ).fetchone()
        conn.close()
        if row:
            return row[0], True
    except Exception as e:
        print(f"查询 AppId 失败: {e}")
    return fallback_id, False

def filetime_to_dt(ft):
    if not ft:
        return "N/A"
    unix = (ft - 116444736000000000) / 10000000
    return datetime.fromtimestamp(unix).strftime("%Y-%m-%d %H:%M:%S")

def load_last_id():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            pass
    return 0

def save_last_id(nid):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(str(nid))

def parse_notification(payload):
    try:
        text = payload.decode("utf-8", errors="ignore")
        texts = re.findall(r"<text[^>]*>(.*?)</text>", text, re.DOTALL)
        texts = [t.strip() for t in texts if t.strip()]
        if len(texts) >= 2:
            return texts[0], texts[1]
        elif texts:
            return texts[0], ""
    except Exception:
        pass
    return None, None

def translate_to_english(title, content):
    if "下线" in title or "下线" in content:
        status = "offline"
    elif "上线" in title or "上线" in content:
        status = "online"
    else:
        status = "alert"
    device = re.sub(r"(下线啦|上线啦|下线|上线)", "", content or "").strip()
    if device:
        return [f"{device} {status}"]
    else:
        return [f"Device {status}"]

def send_wechat(token, title_text, content_text):
    """通过 PushPlus 发送微信通知"""
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title_text,
            "content": content_text,
            "template": "txt"
        }
        resp = requests.post(url, data=data, timeout=10)
        result = resp.json()
        return result.get("code") == 200
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def read_new_notifications(db_path, handler_id, last_id):
    try:
        conn = sqlite3.connect("file:" + db_path + "?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Id, Payload, ArrivalTime FROM Notification "
            "WHERE HandlerId=? AND Id>? ORDER BY Id ASC",
            (handler_id, last_id)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"读取数据库失败: {e}")
        return []

def main():
    print("=" * 55)
    print("向日葵主机上下线监控 (PushPlus 版)")
    print("=" * 55)

    config = load_config()
    if not config:
        return

    if not config['token'] or config['token'] == '请在此填入你的PushPlus Token':
        print("错误：请先在 config.ini 中配置 PushPlus Token")
        print("获取地址：https://www.pushplus.plus/")
        input("按回车键退出...")
        return

    if not config['db_path']:
        print("错误：请先在 config.ini 中配置 DBPath")
        input("按回车键退出...")
        return

    # 自动探测 HandlerId（优先 PrimaryId 匹配）
    handler_id, auto = resolve_handler_id(config['db_path'], config['app_id'], config['handler_id'])
    if auto:
        source = f"自动匹配 AppId={config['app_id']}"
    else:
        source = f"回退到配置值 HandlerId={config['handler_id']}（未找到 {config['app_id']}，请确认向日葵已安装）"

    print(f"配置文件: {CONFIG_FILE}")
    print(f"数据库: {config['db_path']}")
    print(f"HandlerId: {handler_id}  ({source})")
    print(f"检测间隔: {config['check_interval']} 秒")
    print("-" * 55)

    last_id = load_last_id()
    print(f"上次处理通知 ID: {last_id}")
    print("-" * 55)
    print("运行中，按 Ctrl+C 停止...\n")

    while True:
        try:
            rows = read_new_notifications(config['db_path'], handler_id, last_id)

            for nid, payload, arrival in rows:
                title, content = parse_notification(payload)
                if not title and not content:
                    continue

                time_str = filetime_to_dt(arrival)
                print(f"[{time_str}] 检测到通知 ID:{nid}")
                print(f"  标题: {title}")
                print(f"  内容: {content}")

                parts = translate_to_english(title, content)
                title_en = parts[0]
                desp_en = "\n".join(parts)

                if send_wechat(config['token'], title_en, desp_en):
                    print(f"  ✓ 已发送到微信: {title_en}")
                else:
                    print(f"  ✗ 发送失败")

                last_id = nid
                save_last_id(nid)
                print()

        except Exception as e:
            print(f"监控异常: {e}")

        time.sleep(config['check_interval'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已停止监控")
        input("按回车键退出...")
