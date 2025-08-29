import os
import requests
import time
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

def get_china_time():
    return datetime.now(ZoneInfo("Asia/Shanghai"))

DISCORD_WEBHOOK_URL = os.getenv ( "DISCORD_WEBHOOK_URL")

def send_to_discord ( message: str ) :
    if not DISCORD_WEBHOOK_URL:
        print ( "未设置 DISCORD_WEBHOOK_URL，跳过推送")
        return
    try:
        r = requests.post ( DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
        if r.status_code != 204:
            print ( "发送到 Discord 失败：", r.status_code, r.text)
    except Exception as e:
        print ( "推送到 Discord 出错：", e)

def write_log ( log_file, timestamp, rows, changes ) :
    with open ( log_file, "a", encoding="utf-8") as f:
        f.write ( f"\n==== {timestamp} ====\n")
        for row in rows:
            f.write ( row + "\n")
        if changes:
            f.write ( "变化检测到：\n")
            for name, diff in changes:
                f.write ( f"  {name}: {diff:+d}\n")
        f.write ( "=================\n")

def fetch_kr_product (  ) :
    url = os.getenv ( "KR_URL")
    referer = os.getenv ( "KR_REFERER")
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": referer,
    }
    log_file = "ko.txt"
    last_data = {}

    while True:
        try:
            resp = requests.get ( url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json ( )
                option_list = data.get ( 'data', {} ) .get ( 'optionList', [])
                timestamp = datetime.now (  ) .strftime ( '%Y-%m-%d %H:%M:%S')
                current_data, changes, rows = {}, [], []

               # print ( f"\n==== [KR接口] {timestamp} ====")
                for item in option_list:
                    name = item.get ( 'optionNameValue1', '')
                    qty = item.get ( 'salesQuantity', 0)
                    current_data[name] = qty
                    row = f"{name} - {qty}"
                    rows.append ( row)
                    #print ( row)
                    if name in last_data:
                        diff = qty - last_data[name]
                        if diff != 0:
                            changes.append (  ( name, diff ) )

                if changes:
                   # print ( "变化检测到：")
                    #for name, diff in changes:
                       # print ( f"  {name}: {diff:+d}")
                    change_text = "\n".join ( f"{n}: {d:+d}" for n, d in changes)
                    current_text = "\n".join ( rows)
                    msg = (
                        f"[KR接口] {timestamp}\n变化检测到：\n{change_text}\n\n当前数据：\n{current_text}"
                    )
                    send_to_discord ( msg)

               # print ( "=================")
                write_log ( log_file, timestamp, rows, changes)
                last_data = current_data
            else:
                print ( "KR 请求失败：", resp.status_code, resp.text[:200])
        except Exception as e:
            print ( "KR 接口异常：", e)
        time.sleep ( 5)

def fetch_tw_product (  ) :
    url = os.getenv ( "TW_URL")
    referer = os.getenv ( "TW_REFERER")
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate,zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": referer,
        "user-agent": "Mozilla/5.0",
        "x-requested-with": "XMLHttpRequest"
    }
    log_file = "tw.txt"
    last_data = {}

    while True:
        try:
            resp = requests.get ( url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json ( )
                option_list = data.get ( 'variants', [])
                timestamp = datetime.now (  ) .strftime ( '%Y-%m-%d %H:%M:%S')
                current_data, changes, rows = {}, [], []

                #print ( f"\n==== [TW接口] {timestamp} ====")
                for item in option_list:
                    name = item.get ( 'option1', '')
                    qty = item.get ( 'inventory_quantity', 0)
                    current_data[name] = qty
                    row = f"{name} - {qty}"
                    rows.append ( row)
                    #print ( row)
                    if name in last_data:
                        diff = qty - last_data[name]
                        if diff != 0:
                            changes.append (  ( name, diff ) )

                if changes:
                    print ( "变化检测到：")
                    #for name, diff in changes:
                        #print ( f"  {name}: {diff:+d}")
                    change_text = "\n".join ( f"{n}: {d:+d}" for n, d in changes)
                    current_text = "\n".join ( rows)
                    msg = (
                        f"[TW接口] {timestamp}\n变化检测到：\n{change_text}\n\n当前数据：\n{current_text}"
                    )
                    send_to_discord ( msg)

                print ( "=================")
                write_log ( log_file, timestamp, rows, changes)
                last_data = current_data
            else:
                print ( "TW 请求失败：", resp.status_code, resp.text[:200])
        except Exception as e:
            print ( "TW 接口异常：", e)
        time.sleep ( 5)

if __name__ == "__main__":
    t1 = threading.Thread(target=fetch_kr_product, daemon=True)
    t2 = threading.Thread(target=fetch_tw_product, daemon=True)
    t1.start()
    t2.start()
    
    time.sleep(60*60)  
    print("运行 30 分钟结束，程序退出")
