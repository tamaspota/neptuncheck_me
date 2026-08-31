# Changelog

## 2026-08-31 — v0.2

### Added
- Persistent probe log (`neptun_watcher.log`) for every availability check.
- Availability transition log (`neptun_availability.log`) for INITIAL / AVAILABLE / UNAVAILABLE events.
- Downtime duration in seconds when the endpoint becomes reachable again.
- Watcher stop event.
- Console event output on availability transitions.

### Safety
- No Neptun username or password is stored or submitted.
- Minimum polling interval remains 30 seconds; default is 60 seconds.
- Runtime logs are excluded from Git via `.gitignore`.

### Observed test state
- v0.1 ran locally on Windows from approximately 2026-08-31 15:45 to 15:50 CEST.
- Five consecutive probes reported `DOWN`, `status=None` for the configured endpoint `https://neptun.uni-miskolc.hu/`.
- v0.2 started locally at approximately 2026-08-31 15:51 CEST and also initially reported `DOWN`, `status=None`.
- This observation alone does **not** prove a Neptun outage. Possible explanations include an incorrect/obsolete endpoint, DNS/network/TLS reachability, server-side filtering, or an actual outage/maintenance period.

### Next validation
- Keep v0.2 running through the expected registration window and verify whether it records an `AVAILABLE` transition.
- If it remains permanently `DOWN` while Neptun is demonstrably reachable in a normal browser, verify and replace the configured endpoint before adding login automation.

## 2026-08-31 — v0.1

### Initial version
- Standard-library-only Python availability watcher.
- 60-second default polling.
- Optional browser opening when the endpoint returns after being unavailable.
- No automated authentication.
