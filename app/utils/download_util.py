import time

import requests
import os
# 定义 MP3 文件的 URL 模板
base_url = "https://f.bmcx.com/file/gangqin/samples/piano/a{}.mp3"  # 假设文件名是数字或特定格式

# 定义保存目录
save_dir = "/home/yu/piano_notes/"
os.makedirs(save_dir, exist_ok=True)

# 下载 MP3 文件
for i in range(88, 100):  # 假设有 88 个单音
    url = base_url.format(i)
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(save_dir, f"a{i}.mp3")
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
        time.sleep(2)
    else:
        print(f"Failed to download: {url}")