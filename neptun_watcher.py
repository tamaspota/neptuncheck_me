import argparse
import datetime as dt
import time
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path

DEFAULT_URL = "https://neptun.uni-miskolc.hu/"


def stamp():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def check(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "NeptunWatcher/0.1 availability-monitor"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(32768).decode("utf-8", errors="ignore").lower()
            return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, e.geturl(), ""
    except Exception as e:
        return None, url, f"{type(e).__name__}: {e}"


def classify(status, final_url, body):
    if status is None:
        return "DOWN"
    lock_words = ("felfüggeszt", "felfuggeszt", "sikertelen bejelentkez")
    if any(w in body for w in lock_words):
        return "LOCK_PAGE"
    if 200 <= status < 400:
        return "UP"
    if status in (429, 500, 502, 503, 504):
        return "OVERLOADED"
    return f"HTTP_{status}"


def main():
    p = argparse.ArgumentParser(description="Safe Neptun availability watcher. Does NOT submit credentials.")
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--interval", type=int, default=60, help="seconds between checks; minimum 30")
    p.add_argument("--timeout", type=int, default=12)
    p.add_argument("--open-on-up", action="store_true", help="open browser once when service becomes reachable")
    p.add_argument("--log", default="neptun_watcher.log")
    args = p.parse_args()
    args.interval = max(args.interval, 30)

    log_path = Path(args.log)
    last = None
    opened = False
    print(f"Neptun Watcher v0.1 | {args.url} | interval={args.interval}s")
    print("No username/password is stored or submitted. Ctrl+C to stop.")

    try:
        while True:
            status, final_url, body = check(args.url, args.timeout)
            state = classify(status, final_url, body)
            line = f"{stamp()} | {state} | status={status} | {final_url}"
            print(line, flush=True)
            with log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

            if args.open_on_up and state == "UP" and last not in (None, "UP") and not opened:
                webbrowser.open(args.url)
                opened = True
                print("Service is reachable again; opened the login page. Login remains manual.")
            if state != "UP":
                opened = False
            last = state
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
