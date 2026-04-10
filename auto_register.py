"""
悟空自动填写邀请码脚本（整点抢码版）

使用方式：
1. 打开悟空桌面端，用钉钉扫码登录
2. 等到邀请码输入框出现并获得焦点
3. 运行此脚本，程序会自动等到下一个整点前 1s 发起请求并填入
"""

import requests
import pyautogui
import pyperclip
import time
import datetime
import sys

INVITE_CODE_API = "https://ai-table-api.dingtalk.com/v1/wukong/invite-code"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "referer": "https://wukong.dingtalk.com/",
    "origin": "https://wukong.dingtalk.com",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}


def get_invite_code() -> str:
    try:
        resp = requests.get(INVITE_CODE_API, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        code = data.get("code")
        if not code:
            print(f"[ERROR] 接口返回无 code 字段：{data}")
            return None
        return code
    except requests.RequestException as e:
        print(f"[ERROR] 请求失败：{e}")
        return None


def fill_and_submit(code: str):
    print(f"[INFO] 邀请码：{code}，开始填入...")
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    pyperclip.copy(code)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.1)
    # pyautogui.press("enter")
    pyautogui.click(x=638, y=946)
    print(f"[INFO] 已提交")


def wait_until_before_next_hour(seconds_before: float = 1.0):
    """阻塞直到下一个整点前 seconds_before 秒"""
    now = datetime.datetime.now()
    # 下一个整点
    next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    trigger_time = next_hour - datetime.timedelta(seconds=seconds_before)

    wait_sec = (trigger_time - now).total_seconds()
    if wait_sec < 0:
        # 已经过了触发点，说明刚好在整点附近，直接执行
        return

    print(f"[INFO] 下一个整点：{next_hour.strftime('%H:%M:%S')}，将在 {trigger_time.strftime('%H:%M:%S')} 发起请求\n")

    # 每秒打印一次当前时间和倒计时，最后 0.5s 进入精细等待
    while True:
        now = datetime.datetime.now()
        remaining = (trigger_time - now).total_seconds()
        if remaining <= 0.5:
            break
        mins, secs = divmod(int(remaining), 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            countdown = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            countdown = f"{mins:02d}:{secs:02d}"
        print(f"  当前时间 {now.strftime('%H:%M:%S')}  |  距离整点还有 {countdown}", end="\r")
        time.sleep(1)

    print()  # 换行，避免倒计时行被覆盖

    # 精细等待最后 0.5s
    while True:
        remaining = (trigger_time - datetime.datetime.now()).total_seconds()
        if remaining <= 0:
            break
        time.sleep(0.001)


def main():
    print("[INFO] 请确保悟空邀请码输入框已获得焦点，程序将在整点前 1s 自动抢码并填入")
    print("[INFO] 按 Ctrl+C 可随时退出\n")

    # 启动时先查一次，有码直接填入
    print("[INFO] 启动时先查询一次邀请码...")
    code = get_invite_code()
    if code:
        fill_and_submit(code)
        print("[INFO] 启动时已成功填入，如未成功将在下一个整点继续尝试\n")
    else:
        print("[WARN] 启动时未获取到邀请码，等待整点继续尝试\n")

    while True:
        wait_until_before_next_hour(seconds_before=1.0)

        now = datetime.datetime.now()
        print(f"\n[{now.strftime('%H:%M:%S.%f')[:-3]}] 整点到来，发起请求...")

        code = get_invite_code()
        if code:
            fill_and_submit(code)
            print("[INFO] 完成，如未成功（码已用完）将在下一个整点继续尝试\n")
        else:
            print("[WARN] 未获取到邀请码，下一个整点继续尝试\n")

        # 等 2s 避免在同一整点重复触发
        time.sleep(2)


if __name__ == "__main__":
    main()
