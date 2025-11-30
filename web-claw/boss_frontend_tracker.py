#!/usr/bin/env python3
"""
Boss 直聘杭州前端岗位跟踪脚本
================================
功能:
1. 登录后携带 Cookie 调用 Boss 直聘官方接口, 抓取最近更新的杭州前端岗位列表;
2. 将每次抓取结果保存为带时间戳的 CSV 快照;
3. 与上一次快照对比, 输出新增/下线岗位变化情况.

使用方法:
$ python boss_frontend_tracker.py --cookie "SESSION=xxxx; other=yyy" --pages 4 --out ./data

依赖: requests, pandas (pip install -r requirements.txt)
注意: Boss 直聘有反爬风控, 请适当增大 --sleep 间隔并控制抓取频率.
"""

import argparse
import datetime as dt
import sys
import time
from pathlib import Path
from typing import List, Dict

import pandas as pd
import requests

API_TEMPLATE = (
    "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?city=101210100&"
    "query=%E5%89%8D%E7%AB%AF&source=1&sortType=2&page={page}"
)  # sortType=2 => 最新

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0; +https://github.com)"
}


def fetch_page(page: int, cookie: str, sleep: float = 0.8) -> List[Dict]:
    """抓取单页职位列表."""
    headers = HEADERS_BASE.copy()
    headers["Cookie"] = cookie
    url = API_TEMPLATE.format(page=page)
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    time.sleep(sleep)  # 温柔一些, 避免触发风控
    if data.get("code") != 0:
        raise RuntimeError(f"API error: {data.get('message')}")
    return data["zpData"]["jobList"]


def normalize(j: Dict) -> Dict:
    """提取关键信息."""
    return {
        "jobId": j["encryptJobId"],
        "职位": j["jobName"],
        "公司": j["brandName"],
        "薪资": j["salaryDesc"],
        "经验": j["jobExperience"],
        "学历": j["jobDegree"],
        "发布日期": j["expectDate"],
        "地区": j["cityName"],
    }


def crawl(cookie: str, pages: int, sleep: float) -> pd.DataFrame:
    rows: List[Dict] = []
    for p in range(1, pages + 1):
        for item in fetch_page(p, cookie, sleep):
            # 4 == 猎头; 过滤掉
            if item.get("bossCert") == 4:
                continue
            rows.append(normalize(item))
        print("字段列表:", item.keys())

    df = pd.DataFrame(rows).drop_duplicates("jobId")
    # 只保留薪资下限 >= 20K 的岗位
    df = df[df["薪资"].str.extract(r"(\d+)").astype(int)[0] >= 20]
    return df.sort_values("发布日期", ascending=False).reset_index(drop=True)


def diff(old: pd.DataFrame, new: pd.DataFrame):
    old_ids, new_ids = set(old.jobId), set(new.jobId)
    added = new[new.jobId.isin(new_ids - old_ids)]
    removed = old[old.jobId.isin(old_ids - new_ids)]
    return added, removed


def save_snapshot(df: pd.DataFrame, out_dir: Path):
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"snapshot_{ts}.csv"
    df.to_csv(path, index=False)
    return path


def load_latest_snapshot(out_dir: Path):
    snaps = sorted(out_dir.glob("snapshot_*.csv"))
    if snaps:
        return pd.read_csv(snaps[-1])
    return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="Boss 直聘前端岗位跟踪")
    parser.add_argument("--cookie", help="浏览器抓包得到的 cookie 字符串")
    parser.add_argument("--pages", type=int, default=4, help="抓取页数 (每页约 30 条)")
    parser.add_argument("--sleep", type=float, default=0.8, help="每页抓取间隔秒")
    parser.add_argument("--out", default="./data", help="快照输出目录")
    args = parser.parse_args()

    if not args.cookie:
        print("[!] 错误: 请使用 --cookie 参数提供 Cookie 字符串")
        parser.print_help()
        sys.exit(2)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[+] 抓取最新岗位 …")
    new_df = crawl(args.cookie, args.pages, args.sleep)
    print(f"   共抓到 {len(new_df)} 条符合薪资要求的岗位")

    old_df = load_latest_snapshot(out_dir)
    added, removed = diff(old_df, new_df) if not old_df.empty else (new_df, pd.DataFrame())

    snap_path = save_snapshot(new_df, out_dir)
    print(f"[+] 快照已保存: {snap_path}")

    print("\n=== 变化汇总 ===")
    print(f"新增岗位: {len(added)} 条")
    print(f"下线岗位: {len(removed)} 条")

    if not added.empty:
        print("\n--- 新增 (top 5) ---")
        print(added.head()[["职位", "公司", "薪资", "发布日期"]].to_string(index=False))
    if not removed.empty:
        print("\n--- 下线 (top 5) ---")
        print(removed.head()[["职位", "公司", "薪资", "发布日期"]].to_string(index=False))


if __name__ == "__main__":
    main()
