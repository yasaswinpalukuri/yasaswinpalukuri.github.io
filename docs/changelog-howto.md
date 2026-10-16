# Logging an upgrade

When something ships — on Groot, on this site, or on the infrastructure under
either — append an entry to `changelog.json` **in the same commit as the change
it describes**. That coupling is the whole point: the log cannot drift from
reality if it moves with the code.

`live.html` reads the file directly. The newest entry drives the
**"since last upgrade"** figure on the status page, so the number is true by
construction instead of by a hardcoded date.

---

## Prompt for the developer agent

> You have just shipped a change. Append an entry to the top of the `entries`
> array in `changelog.json` in the `yasaswinpalukuri.github.io` repo, and commit
> it alongside the change.
>
> Fields:
> - `date` — the day it **shipped**, `YYYY-MM-DD`. Not the day work started.
> - `scope` — `groot`, `portfolio` or `infra`.
> - `title` — short imperative phrase, no trailing period.
> - `what` — what concretely changed. Name the files, services or counts.
> - `why` — the problem it solved. This is the part worth reading.
> - `value` — what it bought: a number, a risk removed, or time saved.
>
> Rules:
> - Only log things that **actually shipped**. An open pull request is not an
>   upgrade. If it is merged but not deployed, say so in `what`.
> - No invented metrics. If you did not measure it, describe the change instead.
> - Newest entry first. Keep `_schema` at the top of the file untouched.
> - Validate the file parses as JSON before committing.
> - Write plainly. A hiring manager reads this page.

---

## Example of a good entry

```json
{
  "date": "2026-10-06",
  "scope": "groot",
  "title": "Mock the backend in the dashboard E2E suite",
  "what": "Added 7 Playwright tests covering overview load, streamed chat reply, job-tracker status change and the API 500 state, with the backend mocked through page.route() network fixtures. Runs as a GitHub Actions job on every pull request.",
  "why": "The dashboard was only ever tested by hand against a live backend, so a broken chat stream reached the box before anyone noticed.",
  "value": "7/7 passing in CI, and regressions now surface on the pull request instead of on the running system."
}
```

## What a bad entry looks like

```json
{
  "date": "2026-10-06",
  "scope": "groot",
  "title": "Improved performance",
  "what": "Various optimisations and refactoring",
  "why": "Code quality",
  "value": "40% faster"
}
```

Vague on every field, and the number is unsourced. "40% faster" at what, measured
how? An interviewer will ask, and there is no answer. Either measure it and say
what you measured, or describe the change and leave the number out.

---

## Checking it rendered

```bash
python3 -m json.tool changelog.json > /dev/null   # parses?
python3 -m http.server 8000                       # port 8000 is in the API's CORS allowlist
# open http://localhost:8000/live.html and confirm the entry appears
# and that "Since last upgrade" reset to roughly 0h
```
