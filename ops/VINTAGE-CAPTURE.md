# Vintage capture: design, prerequisites, build plan

*Design for the unattended capture of public data that publishers overwrite
in place, per the etrmbiz note of 2026-09-15 ("Vintage capture on Render +
S3, the laptop watchdog, and Morpholog priorities") including its
Amendment 1. Nothing here is deployed until the sponsor says so. This file
is the brief the build commits follow; each part below is one commit.*

## 1. What it does, in one paragraph

A Render cron job runs the grid-mysteries codebase once a day in Docker. It
executes a **capture plan**: for each declared resource it fetches the
bytes, content-addresses them, writes them and a manifest line to an S3
bucket, and stops. It never analyses, never seals, never proposes to
Morpholog. At the end it writes a status object and pings a healthchecks.io
URL, so a missed or failed run raises an email whether or not the laptop is
on. Each daily manifest's digest is witnessed by OpenTimestamps and by two
RFC 3161 authorities, and the proofs sit beside it. A laptop watchdog
(systemd user timer) checks the bucket and syncs the manifests, proofs and
optionally the bytes into the repo, so the laptop stays a full second copy.

## 2. The doctrine it implements (Amendment 1)

- **The rule is witnessed before the data.** Declarations are stamped
  (`scripts/timestamp`) at freeze; the capture job stamps every daily
  manifest. "This rule was frozen before that data existed" is a claim a
  stranger can check against roots we do not control.
- **The reads are logged.** Two credentials: a *capture writer* that can
  only `PutObject` and `GetObject` on the vintage bucket, and an *analysis
  reader* that can only `GetObject` and `ListBucket`. S3 server access
  logging goes to a separate log bucket neither credential can touch. A
  declaration frozen after the archive exists records the **log position**
  at freeze (the latest log object's key and the UTC time), so "no analysis
  read of the window's objects before the witnessed freeze" is checkable
  from the logs rather than promised.
- **The human authors and publishes.** Freezing a declaration and releasing
  a finding stay human acts. Fetch, run and render are unattended. Standing
  instruments carry one seal, their declaration's digest, supplied to the
  job as configuration; there are no per-batch seals. The 013 runner keeps
  its `--seal` gate and receives the declaration prefix from the
  environment.

## 3. Bucket layout (`a115-vintages`, eu-west-2)

    raw/<source>/<resource>/<YYYY-MM-DD>/<sha256>      the bytes (private)
    manifests/<YYYY-MM-DD>.ndjson                       one line per artefact
                                                        (dataset, url, sha256,
                                                        bytes, fetched_at,
                                                        Last-Modified, ETag,
                                                        CKAN last_modified)
    proofs/<YYYY-MM-DD>.ndjson.{ots,tsq,freetsa.tsr,digicert.tsr,timestamps.json}
    status/<job>/latest.json, status/<job>/<YYYY-MM-DD>.json
    state/<instrument>/...                              per-instrument journals
                                                        and pinned artefacts the
                                                        laptop syncs down (013)

Versioning on; Object Lock in governance mode with a five-year retention
default, so no ordinary credential can overwrite or delete; Intelligent
Tiering; `manifests/` and `proofs/` public-read (the public good), `raw/`
and `state/` private (the moat). Access logs to `a115-vintages-logs`.

## 4. The capture plan, version 1

Declared in `src/grid_mysteries/capture/plan.py` as data, one entry per
resource with a fetch strategy. Strategies:

- `ckan`: NESO data-portal resource by id: `resource_show` for
  `last_modified`, then the download URL. Resources: the TEC register
  (`17becbab…`), the daily balancing costs, volume and disaggregated BSAD
  2026-27 files (013's three), the constraint breakdown and boundary flow
  resources 003 used, the skip-rate resources the method studies used, the
  connections-queue and embedded-register resources 011 and 014 used. Ids
  are taken from the investigations that pinned them, never guessed; a
  resource whose id is not in the repo is listed as *to add* in the plan
  with the investigation that will supply it.
- `url`: a plain GET with the response headers kept. Used for the
  DESNZ REPD collection page and its current extract link, the Octopus
  product and tariff endpoints 010 pinned, Contracts Finder and Find a
  Tender daily OCDS packages (previous UTC day), and the ESO (Bulgaria) map
  endpoints.
- `eso_map`: the existing `scripts/snapshot-eso-map` logic moved verbatim
  into the plan (points, lines, one request per substation, 150 ms apart).
- `elexon_remit`: the Insights API REMIT list for the previous UTC day by
  publish time, then each message's detail; the update and withdrawal
  sequence per message is what the revision-fingerprint work needs.

Every strategy produces the same manifest line. Bytes go to
`raw/<source>/<resource>/<date>/<sha256>`; a resource whose bytes hash to
the previous day's digest is still written (a day's copy is a day's copy)
but the manifest line says `unchanged_from: <date>`. Nothing is parsed.

## 5. Jobs (render.yaml, `type: cron`, Docker runtime, region Frankfurt)

| job | schedule (UTC) | command | needs |
|---|---|---|---|
| `vintage-capture` | daily 06:30 | `grid-mysteries capture run` | S3 writer key, healthchecks URL |
| `tracker-013` | daily 09:00 | `run.py --phase acquire --seal $SEAL_013` then sync `data/raw/{elexon,neso}/013` and the 013 journals to `state/013/` | S3 writer key, `SEAL_013=d20d5920` |

Compute and render for 013 and 014 stay on the laptop: they need the
committed evidence, and rendering is a pure function of it. The watchdog
syncs `state/013/` into the repo's `data/raw` and `evidence/` paths; the
runner then finds its artefacts already pinned, verifies them against the
journal, and skips the fetch (it is idempotent by construction).
`scripts/run-013-batch-1` and its crontab line are retired once
`tracker-013` is live; the ESO map crontab line is retired once
`vintage-capture` is.

## 6. Timestamping

After the manifest is written, the job stamps it: OpenTimestamps (pending
until the calendar's block is mined; the watchdog runs `ots upgrade` on
proofs older than a day and re-uploads) and RFC 3161 tokens from
freetsa.org and DigiCert. Proofs go to `proofs/`. The same script stamps
every declaration at freeze.

## 7. Watchdog (`scripts/check-vintages`, systemd user timer)

`Persistent=true`, on boot and every twelve hours. Five checks: every job's
`status/latest.json` is younger than its schedule allows; artefact counts
and bytes per resource sit inside a band learned from the last thirty
runs; a random sample of yesterday's manifest entries re-downloads and
matches its digest; a proof exists for each manifest; Object Lock, logging
and public-access settings are unchanged. Then one sync: manifests and
proofs into `data/manifests/`, `state/` into the repo, bytes optionally
into `data/raw/archive/`. Failures go to `notify-send` and a log line.
Units under `ops/systemd/`; `ops/install-watchdog` links and enables them
(a deliberate act, not part of any commit's effect).

## 8. Archive adapter

`sources/archive.py`: given a manifest date and resource, read the bytes
from S3 (analysis reader) or the local mirror and pin them like any other
artefact, with the manifest line as provenance. A vintage the archive holds
is then a legitimate source for a declaration frozen after that date.

## 9. Prerequisites the sponsor must do (nothing below works without them)

1. **Render**: `render login` (the CLI is installed and logged out), and
   the GitHub repository must be reachable by Render, which means the
   branch with the build must be pushed. Pushing is the sponsor's act.
2. **AWS**: an account and admin credentials to run `ops/aws-bootstrap.sh`
   once (creates the two buckets with versioning, Object Lock, logging,
   Intelligent Tiering and the public-read prefixes; creates the
   `vintage-capture-writer`, `vintage-analysis-reader` and
   `vintage-watchdog` IAM users with their policies; prints the keys). The
   file `~/.aws/credentials-a115` exists but is not wired to the `a115`
   profile; either wire it (`AWS_SHARED_CREDENTIALS_FILE` or a copy into
   `~/.aws/credentials` under `[a115]`) or use fresh keys.
3. **healthchecks.io**: one check per job (`vintage-capture` daily with a
   two-hour grace, `tracker-013` daily); the ping URLs go to Render as
   `HEALTHCHECK_URL_CAPTURE` and `HEALTHCHECK_URL_013`.
4. **Render environment variables**: `AWS_ACCESS_KEY_ID` and
   `AWS_SECRET_ACCESS_KEY` (the writer), `AWS_DEFAULT_REGION=eu-west-2`,
   `VINTAGE_BUCKET=a115-vintages`, the two healthchecks URLs,
   `SEAL_013=d20d5920`, and `COMPANIES_HOUSE_API_KEY` for later
   (`~/dev/accounting/.envrc` has it).
5. **Laptop**: the watchdog profile (`vintage-watchdog` keys under
   `[a115-watchdog]` in `~/.aws/credentials`), then `ops/install-watchdog`.
6. **Say "deploy"**: `render blueprint launch` (or the dashboard) creates
   the two cron jobs from `render.yaml`; the first run is watched by hand.

## 10. Build plan, one commit per part

1. This design (this file) and `ops/aws-bootstrap.sh`.
2. `capture/` package: plan, fetchers, object store (local for tests, S3
   for production), manifest, status, healthcheck ping; `grid-mysteries
   capture run|plan|dry-run`; Dockerfile; `render.yaml` cron entry; tests
   against the local store with fake fetchers.
3. Timestamp step in the job, and `sources/archive.py`.
4. `scripts/check-vintages`, the systemd units, `ops/install-watchdog`.
5. ESO map snapshot moved into the plan; its crontab line documented as
   retired on deploy.
6. `tracker-013` job: acquisition on Render, sync to `state/013/`, watchdog
   sync into the repo; `scripts/run-013-batch-1` documented as retired on
   deploy.

## 10a. Build status (2026-09-15)

Parts 1 to 6 are built and committed; nothing is deployed and no crontab
line has been changed. Part 5 (the ESO map) is the plan's `ESO-MAP`
resource from part 2 plus the retirement notice on
`scripts/snapshot-eso-map`; part 6 is `scripts/run-013-render` with the
`tracker-013` cron entry and `capture pull-state` / `push-state`. Not
built: the log-position record at freeze (needs the log bucket to exist)
and the `ots upgrade` sweep in the watchdog (a follow-up once proofs exist
in the bucket).

## 11. Cost

Render cron: about one dollar a month plus minutes of compute a day. S3:
gigabytes a month at Intelligent Tiering rates, under a pound.
healthchecks.io: free tier. OpenTimestamps and freetsa.org: free; DigiCert's
public TSA: free.
