import requests
import time
import rich
from collections import defaultdict
from rich.console import Console
from rich.table import Table
import aiohttp

# 配置日志
console = Console()
time_windows = 1

# 初始化计数器和开始时间
counters = defaultdict(list)
unique_values = defaultdict(int)  # 记录所有数值种类的数量
start_time = time.time()

def update_counters(value):
    current_time = time.time()
    counters[value].append((value, current_time))

    # 更新所有数值种类的数量
    unique_values[value] += 1

def print_statistics():
    table = Table(title="统计数据", show_lines=True)
    table.add_column("时间窗口", justify="center")
    table.add_column("值", justify="center")
    table.add_column("出现次数", justify="center")
    table.add_column("占比 (%)", justify="center")

    current_time = time.time()
    total = 0
    counts = defaultdict(int)

    # 只统计1小时内的数据
    for key, timestamp_list in counters.items():
        valid_timestamps = [t for t in timestamp_list if (current_time - t[1]) < 3600 * int(time_windows)]
        counts[key] = len(valid_timestamps)
        total += len(valid_timestamps)

    if total > 0:
        for key, count in counts.items():
            table.add_row('{}h'.format(str(time_windows)), str(key), str(count), f"{count / total * 100:.2f}")

    # 显示所有数值种类的数量
    unique_table = Table(title="所有唯一值", show_lines=True)
    unique_table.add_column("值", justify="center")
    unique_table.add_column("出现次数", justify="center")
    for key, count in unique_values.items():
        unique_table.add_row(str(key), str(count))

    console.clear()
    console.print(table)
    console.print(unique_table)

async def get_reward_rate_async():
    url = 'https://fullnode.mainnet.sui.io/'
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'client-sdk-type': 'typescript',
        'client-sdk-version': '1.12.0',
        'client-target-api-version': '1.36.0',
        'content-type': 'application/json',
        'origin': 'https://suimine.xyz',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://suimine.xyz/',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "sui_getObject",
        "params": [
            "0x1aa2497f14d27b2d7c2ebd9dd607cda0279dc4d54a57e3a8476a1236474b6567",
            {"showContent": True}
        ]
    }

    async with aiohttp.ClientSession() as session:  # 创建一个异步会话
        async with session.post(url, headers=headers, json=payload) as response:  # 发起异步POST请求
            if response.status == 200:
                data = await response.json()  # 异步读取响应JSON
                reward_rate = data['result']['data']['content']['fields']['reward_rate']
                return reward_rate
            else:
                raise Exception(f"Failed to fetch data (status code: {response.status})")

def get_reward_rate_sync():
    url = 'https://fullnode.mainnet.sui.io/'
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'client-sdk-type': 'typescript',
        'client-sdk-version': '1.12.0',
        'client-target-api-version': '1.36.0',
        'content-type': 'application/json',
        'origin': 'https://suimine.xyz',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://suimine.xyz/',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "sui_getObject",
        "params": [
            "0x1aa2497f14d27b2d7c2ebd9dd607cda0279dc4d54a57e3a8476a1236474b6567",
            {"showContent": True}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if 'result' in data:
        reward_rate = data['result']['data']['content']['fields']['reward_rate']
        return reward_rate
    else:
        raise Exception("Failed to fetch data.")

def main():
    while True:
        try:
            value = get_reward_rate_sync()
            update_counters(value)
            print_statistics()
            print('当前reward_rate：', value)
        except requests.exceptions.RequestException as e:
            console.log(f"请求失败：{e}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
