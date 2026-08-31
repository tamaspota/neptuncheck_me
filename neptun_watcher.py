import argparse
import datetime as dt
import time
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path

# Official University of Miskolc student Neptun endpoint linked by the university Neptun page.
DEFAULT_URL = "https://neptunweb1.uni-miskolc.hu/"


def now():
    return dt.datetime.now().astimezone()


def stamp(value=None):
    return (value or now()).isoformat(timespec="seconds")


def check(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NeptunWatcher/0.3"})
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


def append(path, line):
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    p = argparse.ArgumentParser(description="Safe Neptun availability watcher. Does NOT submit credentials.")
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--interval", type=int, default=60, help="seconds between checks; minimum 30")
    p.add_argument("--timeout", type=int, default=12)
    p.add_argument("--open-on-up", action="store_true", help="open browser once when service becomes reachable")
    p.add_argument("--log", default="neptun_watcher.log", help="every probe")
    p.add_argument("--events-log", default="neptun_availability.log", help="UP/DOWN transitions and outage durations")
    args = p.parse_args()
    args.interval = max(args.interval, 30)

    log_path = Path(args.log)
    events_path = Path(args.events_log)
    last = None
    down_since = None
    opened = False
    print(f"Neptun Watcher v0.3 | {args.url} | interval={args.interval}s")
    print(f"Probe log: {log_path} | Availability history: {events_path}")
    print("No username/password is stored or submitted. Ctrl+C to stop.")

    try:
        while True:
            checked_at = now()
            status, final_url, body = check(args.url, args.timeout)
            state = classify(status, final_url, body)
            line = f"{stamp(checked_at)} | {state} | status={status} | {final_url}"
            print(line, flush=True)
            append(log_path, line)

            reachable = state == "UP"
            was_reachable = last == "UP" if last is not None else None

            if last is None:
                event = f"{stamp(checked_at)} | INITIAL | {'AVAILABLE' if reachable else 'UNAVAILABLE'} | state={state}"
                append(events_path, event)
                if not reachable:
                    down_since = checked_at
            elif reachable != was_reachable:
                if reachable:
                    duration = checked_at - down_since if down_since else None
                    seconds = int(duration.total_seconds()) if duration else 0
                    event = f"{stamp(checked_at)} | AVAILABLE | downtime_seconds={seconds} | previous_state={last}"
                    append(events_path, event)
                    print(f"EVENT: {event}")
                    down_since = None
                else:
                    down_since = checked_at
                    event = f"{stamp(checked_at)} | UNAVAILABLE | previous_state={last} | state={state}"
                    append(events_path, event)
                    print(f"EVENT: {event}")

            if args.open_on_up and reachable and last not in (None, "UP") and not opened:
                webbrowser.open(args.url)
                opened = True
                print("Service is reachable again; opened the student Neptun page. Login remains manual.")
            if not reachable:
                opened = False
            last = state
            time.sleep(args.interval)
    except KeyboardInterrupt:
        append(events_path, f"{stamp()} | WATCHER_STOPPED | last_state={last}")
        print("\nStopped.")


if __name__ == "__main__":
    main()
