# Neptun Watcher

Safe availability watcher for the Miskolci Egyetem Neptun endpoint.

## v0.1

- Checks whether the Neptun endpoint is reachable.
- Does **not** submit a username or password, so it cannot generate additional failed-login attempts or account lockouts.
- Default check interval: 60 seconds; hard minimum: 30 seconds.
- Logs status to `neptun_watcher.log`.
- The Windows launcher opens the browser when the endpoint becomes reachable again after an outage.

## Run on Windows

```powershell
py -3 neptun_watcher.py --interval 60 --open-on-up
```

or double-click:

```text
start_neptun_watcher.bat
```

Stop with `Ctrl+C`.

## Safety

Because repeated failed authentication attempts can temporarily suspend a Neptun account, v0.1 deliberately does not automate credential submission. Login/session monitoring can be added later with explicit rate limiting and lockout detection after the exact login flow has been verified.
