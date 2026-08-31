import datetime as dt
import threading
import tkinter as tk
from pathlib import Path

from neptun_watcher import DEFAULT_URL, append, check, classify, now, stamp

INTERVAL_SECONDS = 30
TIMEOUT_SECONDS = 12
PROBE_LOG = Path("neptun_watcher.log")
EVENTS_LOG = Path("neptun_availability.log")


class NeptunStatusGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Neptun status")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.configure(bg="#080808")
        self.root.geometry("410x112+900+700")

        self.state = "CHECKING"
        self.since = now()
        self.last_probe = None
        self.busy = False

        self.title_label = tk.Label(root, text="NEPTUN", fg="#eeeeee", bg="#080808", font=("Consolas", 11, "bold"))
        self.title_label.pack(anchor="w", padx=14, pady=(10, 0))
        self.status_label = tk.Label(root, text="CHECKING", fg="#ffd54f", bg="#080808", font=("Consolas", 17, "bold"))
        self.status_label.pack(anchor="w", padx=14)
        self.detail_label = tk.Label(root, text="initial probe...", fg="#d0d0d0", bg="#080808", font=("Consolas", 10))
        self.detail_label.pack(anchor="w", padx=14)
        self.probe_label = tk.Label(root, text="", fg="#888888", bg="#080808", font=("Consolas", 9))
        self.probe_label.pack(anchor="w", padx=14)

        self.root.after(100, self.start_probe)
        self.root.after(1000, self.tick)

    def start_probe(self):
        if self.busy:
            return
        self.busy = True
        threading.Thread(target=self.probe, daemon=True).start()

    def probe(self):
        checked_at = now()
        status, final_url, body = check(DEFAULT_URL, TIMEOUT_SECONDS)
        state = classify(status, final_url, body)
        append(PROBE_LOG, f"{stamp(checked_at)} | {state} | status={status} | {final_url}")
        self.root.after(0, lambda: self.apply_probe(checked_at, state, status))

    def apply_probe(self, checked_at, state, status):
        old = self.state
        old_reachable = old == "UP"
        reachable = state == "UP"
        self.last_probe = checked_at
        self.busy = False

        if old == "CHECKING":
            self.since = checked_at
            append(EVENTS_LOG, f"{stamp(checked_at)} | GUI_INITIAL | {'AVAILABLE' if reachable else 'UNAVAILABLE'} | state={state}")
        elif reachable != old_reachable:
            elapsed = int((checked_at - self.since).total_seconds())
            if reachable:
                append(EVENTS_LOG, f"{stamp(checked_at)} | AVAILABLE | previous_state={old} | previous_duration_seconds={elapsed}")
            else:
                append(EVENTS_LOG, f"{stamp(checked_at)} | UNAVAILABLE | previous_state={old} | previous_duration_seconds={elapsed} | state={state}")
            self.since = checked_at
        elif state != old:
            append(EVENTS_LOG, f"{stamp(checked_at)} | STATE_CHANGE | {old} -> {state}")
            self.since = checked_at

        self.state = state
        self.render()
        self.root.after(INTERVAL_SECONDS * 1000, self.start_probe)

    def tick(self):
        self.render()
        self.root.after(1000, self.tick)

    def render(self):
        if self.state == "UP":
            text, color = "UP / ELERHETO", "#61d36b"
        elif self.state == "CHECKING":
            text, color = "CHECKING", "#ffd54f"
        elif self.state == "OVERLOADED":
            text, color = "TERHELT", "#ffb74d"
        else:
            text, color = f"DOWN / {self.state}", "#ff6666"

        elapsed = max(0, int((now() - self.since).total_seconds()))
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        since_text = self.since.strftime("%H:%M:%S")
        last_text = self.last_probe.strftime("%H:%M:%S") if self.last_probe else "-"

        self.status_label.config(text=text, fg=color)
        self.detail_label.config(text=f"since {since_text}   duration {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.probe_label.config(text=f"last check {last_text}   next <= {INTERVAL_SECONDS}s")


def main():
    root = tk.Tk()
    NeptunStatusGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
