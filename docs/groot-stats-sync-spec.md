# Groot stats sync — requirements

Spec for the daily job on the M720Q that keeps the live figures on
`yasaswinpalukuri.github.io` current. Hand this to whoever maintains the Groot box.

Scope has widened: the job currently syncs **one** number in **one** file. It needs
to sync **four** values across **four** files.

---

## 1. What exists today

A daily job edits `index.html` in a clone of the site repo, adds 24 to a runtime
figure, commits and pushes:

```
chore: update Groot uptime to 6125h [2026-10-15]
```

It rewrites that number in three places by matching the prose around it:

```html
<span class="term-val">Uptime: 6125 hours</span>
<div class="stat-value">6125<span style="font-size:0.55em;">hrs</span></div>
<span class="green">uptime 6125h and counting</span>
```

### Three problems

1. **It matches prose.** Reword the sentence and the match fails. The job keeps
   running, finds nothing, exits 0, and the number silently freezes.
2. **It increments instead of computing.** A missed run undercounts forever; a
   doubled run overcounts forever.
3. **It only covers runtime, and only in `index.html`.** The model count, disk
   size and agent count are hardcoded in several other places that nothing keeps
   in sync. They are already drifting — see §3.

---

## 2. Source of truth

`groot-status-api.py` on the box, served via Tailscale Funnel at
`https://groot.tailc6acbd.ts.net/status`:

```json
{"agents":6,"models_loaded":10,"models_disk_gb":39,"collections":6,
 "faithfulness":"1.000","memory_used_gb":11.8,"uptime_hours":506}
```

### 2.1 Fix the model count first

`models_loaded` counts **every** model on the box (10, 39GB), including models
used for unrelated work. Groot's agents use 7 (27GB). The site should report the
agent models, not the host total.

Add an allowlist to `groot-status-api.py` and report both:

```python
AGENT_MODELS = {            # the models Groot's 6 agents actually use
    "qwen2.5:7b", "deepseek-r1:14b", "qwen2.5-coder:7b",
    "phi3:medium", "mistral:7b", "nomic-embed-text",
    # ...confirm this list against `ollama list` on the box
}
```

Return:

| Field | Meaning |
|---|---|
| `agent_models` | count of installed models in `AGENT_MODELS` |
| `agent_models_gb` | their combined size, rounded |
| `models_on_host` | total installed (the current `models_loaded`) |
| `models_on_host_gb` | total size (the current `models_disk_gb`) |

Keep `models_loaded` / `models_disk_gb` as aliases of the host totals so
`live.html` does not break mid-deploy.

### 2.2 Runtime vs uptime

`uptime_hours` is **time since last boot** (currently ~506h — the box rebooted on
Sep 24). The site's 6125h is **total runtime since Feb 2, 2026**. These are
different things and must not share a label.

- **Total runtime** → computed from a fixed start date, written into the HTML by
  this job.
- **Current session** → `uptime_hours` from the API, read live by `live.html`.
  Needs no cron.

---

## 3. Values to sync, and where they live

Every number below is currently hardcoded. The job must update **all** occurrences.

| Value | Source | Current | Occurrences |
|---|---|---|---|
| Total runtime (h) | computed from `2026-02-02` | 6125 | `index.html` ×3 |
| Agent models | `agent_models` | 7 | `index.html` ×3, `groot.html` ×2, `live.html` ×1 |
| Agent models GB | `agent_models_gb` | 27 | `index.html` ×3, `groot.html` ×3, `live.html` ×1 |
| ChromaDB collections | `collections` | 6 | `index.html` ×2, `groot.html` ×1, `live.html` ×1 |

Exact locations found in the current files:

**index.html** — hero terminal (`7 models loaded (27GB)`, `6 ChromaDB collections`,
`Uptime: 6125 hours`), Groot stats grid (`7` Ollama Models, `6` ChromaDB
Collections, `6125` Running), build-log Jul entry (`6 agents live. 7 models,
27GB.`), project-card metrics strip (`7` / `models · 27GB`), footer
(`uptime 6125h and counting`).

**groot.html** — section heading `27GB of models, 16GB of RAM, zero GPUs`, body
text `The seven models total 27GB on disk`, stat cards `7` (Models sharing RAM)
and `27GB` (On disk).

**live.html** — the `SNAPSHOT` fallback object (`models_loaded: 7`,
`models_disk_gb: 27`, `collections: 6`).

> `groot.html` spells the count in words ("The seven models total…"). Either
> reword it to carry the number in markup, or accept that it stays manual — but
> decide, do not leave it silently drifting.

---

## 4. Required mechanism

### 4.1 Target data attributes, never prose

The HTML will carry each synced number in a marked span:

```html
<span data-groot="runtime">6125</span>
<span data-groot="models">7</span>
<span data-groot="models-gb">27</span>
<span data-groot="collections">6</span>
```

Update every element matching, regardless of surrounding text:

```
(<span data-groot="runtime">)(\d+)(</span>)
```

Replace group 2 only. Copy can then be edited freely without breaking the job.

For `live.html`'s `SNAPSHOT` object, match the JS keys instead:

```
(models_loaded:\s*)(\d+)
(models_disk_gb:\s*)(\d+)
(collections:\s*)(\d+)
```

### 4.2 Compute runtime, do not increment

```
RUNTIME_START = 2026-02-02T00:00:00-05:00
total_hours   = floor((now - RUNTIME_START) / 3600)
```

Self-correcting: a missed day fixes itself on the next run.

### 4.3 Scan every HTML file

Walk `*.html` at the repo root. Do not hardcode `index.html` — `groot.html`,
`live.html` and any future page must be covered automatically.

---

## 5. Operational requirements

1. **Idempotent.** If nothing changed, make no commit and exit 0. No empty commits.
2. **Fail loudly.** If a value resolves but zero matching elements are found for
   it, exit non-zero and log which one. Silent no-ops caused problem 1.
3. **Fail safe on the API.** If `/status` is unreachable or returns a bad payload,
   update runtime only (it is computed locally) and leave the API-sourced values
   untouched. Never write `0`, `null` or `None` into the page.
4. **Sanity-bound every value.** Reject and log anything outside: models 1–50,
   models_gb 1–500, collections 1–50, runtime monotonically non-decreasing.
   A bad write here lands on a page recruiters read.
5. **Only touch those numbers.** No reformatting of surrounding markup.
6. **`git pull --rebase` before editing**, so a hand edit from the laptop is not
   clobbered. On conflict: abort, leave the tree clean, exit non-zero.
7. **Commit message:** `chore: sync Groot stats — runtime <N>h, <M> models [YYYY-MM-DD]`
8. **Log every run**: timestamp, each value, matches per value, committed yes/no.

---

## 6. Verification

```bash
# 1. dry run — prints what would change, commits nothing
<job> --dry-run

# 2. run, then confirm the live page agrees
<job>
curl -s https://yasaswinpalukuri.github.io/ | grep -o 'data-groot="[a-z-]*">[0-9]*'

# 3. second run the same day must be a no-op
<job> && <job>

# 4. API-down behaviour: block the endpoint, run, confirm runtime still
#    updates and the model numbers are left alone
```

---

## 7. Dependency on the site repo

This spec assumes `index.html`, `groot.html` and `live.html` carry the
`data-groot="..."` spans described in §4.1. **They do not yet.** Sequence:

1. Update `groot-status-api.py` with the allowlist (§2.1) and deploy it.
2. Add the `data-groot` spans to the HTML and push.
3. Deploy the new job.

If the job is deployed before step 2 it will find no matches and — by
requirement §5.2 — exit non-zero rather than silently doing nothing.
