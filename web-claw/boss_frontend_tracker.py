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
$ python boss_frontend_tracker.py --cookie-file ./cookie.txt --pages 1 --sleep 3

依赖: requests, pandas (pip install -r requirements.txt)
注意:
1. Boss 直聘有反爬风控, 请适当增大 --sleep 间隔并控制抓取频率;
2. Cookie 中包含分号, 在 zsh/bash 中必须用引号包住, 否则分号后的内容会被当成命令执行.
"""

import argparse
import datetime as dt
import os
import sys
import time
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

import pandas as pd
import requests

load_dotenv()

API_TEMPLATE = (
    "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?city=101210100&"
    "query=%E5%89%8D%E7%AB%AF&source=1&sortType=2&page={page}"
)  # sortType=2 => 最新
HEADHUNTER_CERT_TYPE = 4
MIN_SALARY_K = 20

HEADERS_BASE = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.zhipin.com/web/geek/job",
    "X-Requested-With": "XMLHttpRequest",
}


class BossAPIError(RuntimeError):
    """Boss 直聘接口返回业务错误。"""


def resolve_cookie(cookie: str | None, cookie_file: str | None) -> str:
    """按参数、文件、环境变量顺序获取 Cookie。"""
    if cookie:
        return cookie.strip()

    if cookie_file:
        path = Path(cookie_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Cookie 文件不存在: {path}")
        return path.read_text(encoding="utf-8").strip()

    env_cookie = os.getenv("BOSS_COOKIE")
    if env_cookie:
        return env_cookie.strip()

    return ""


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
        message = data.get("message") or "未知错误"
        raise BossAPIError(
            f"Boss API error: {message}\n"
            "可能原因：Cookie 失效、未登录、请求环境触发风控，或 Cookie 在 shell 中未正确引用。"
        )
    return data.get("zpData", {}).get("jobList", [])


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
        print(f"[+] 抓取第 {p} 页")
        page_items = fetch_page(p, cookie, sleep)
        if not page_items:
            print(f"[!] 第 {p} 页没有返回岗位数据")
            continue

        for item in page_items:
            if item.get("bossCert") == HEADHUNTER_CERT_TYPE:
                continue
            rows.append(normalize(item))
        print("字段列表:", page_items[0].keys())

    if not rows:
        return pd.DataFrame(columns=["jobId", "职位", "公司", "薪资", "经验", "学历", "发布日期", "地区"])

    df = pd.DataFrame(rows).drop_duplicates("jobId")
    salary_floor = pd.to_numeric(df["薪资"].str.extract(r"(\d+)")[0], errors="coerce").fillna(0)
    df = df[salary_floor >= MIN_SALARY_K]
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
    parser.add_argument("--cookie", help="浏览器抓包得到的 Cookie 字符串。注意必须用引号包住")
    parser.add_argument("--cookie-file", help="从文件读取 Cookie，避免 shell 分号截断问题")
    parser.add_argument("--pages", type=int, default=4, help="抓取页数 (每页约 30 条)")
    parser.add_argument("--sleep", type=float, default=0.8, help="每页抓取间隔秒")
    parser.add_argument("--out", default="./data", help="快照输出目录")
    args = parser.parse_args()

    try:
        cookie = resolve_cookie(args.cookie, args.cookie_file)
        if not cookie:
            raise EnvironmentError("请通过 --cookie、--cookie-file 或 BOSS_COOKIE 提供 Cookie")
    except (EnvironmentError, FileNotFoundError) as e:
        print(f"[!] 错误: {e}")
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
