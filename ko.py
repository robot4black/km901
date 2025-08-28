import requests
import time
import os
from datetime import datetime

event_id = os.getenv("EVENT_ID")
base_url = os.getenv("BASE_URL")
referer_base = os.getenv("REFERER_BASE")

if not event_id or not base_url or not referer_base:
    raise ValueError("请设置环境变量 EVENT_ID, BASE_URL 和 REFERER_BASE")

url = f"{base_url}/{event_id}"
referer = f"{referer_base}/{event_id}"

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
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            option_list = data['data']['optionList']

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n==== {timestamp} ====")
            changes = []
            current_data = {}

            for item in option_list:
                name = item['optionNameValue1']
                qty = item['salesQuantity']
                current_data[name] = qty
                print(f"{name} - {qty}")
                if name in last_data:
                    diff = qty - last_data[name]
                    if diff != 0:
                        changes.append((name, diff))

            if changes:
                print("变化检测到：")
                for name, diff in changes:
                    print(f"  {name}: {diff:+d}")

            print("=================")

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n==== {timestamp} ====\n")
                for item in option_list:
                    f.write(f"{item['optionNameValue1']} - {item['salesQuantity']}\n")
                if changes:
                    f.write("变化检测到：\n")
                    for name, diff in changes:
                        f.write(f"  {name}: {diff:+d}\n")
                f.write("=================\n")

            last_data = current_data

        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.text[:200])

    except requests.exceptions.RequestException as e:
        print("请求发生错误：", e)

    time.sleep(5)
