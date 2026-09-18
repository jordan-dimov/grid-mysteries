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
`raw/<source>/<resource>/<date>/<sha256>`; bytes identical to an earlier
day's are not written again, and the manifest line points at the object
that holds them with `unchanged_from: <date>`. A CKAN resource whose
`last_modified` is unchanged since the previous capture is not downloaded
at all (its metadata is captured and the line says `skipped`). Responses
over 8 MB are streamed to disk and uploaded from the file. Nothing is
parsed.

## 5. Jobs (render.yaml, `type: cron`, Docker runtime, region Frankfurt)

| job | schedule (UTC) | command | env vars as values | env vars unsynced (set in the dashboard) |
|---|---|---|---|---|
| `vintage-capture` | daily 06:30 | `grid-mysteries capture run` | `VINTAGE_STORE=s3://a115-vintages`, `AWS_DEFAULT_REGION=eu-west-2` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (the capture writer), `HEALTHCHECK_URL_CAPTURE` |
| `tracker-013` | daily 09:00 | `scripts/run-013-render` (pull state, `run.py --phase acquire --seal $SEAL_013`, push state, ping) | `VINTAGE_STORE=s3://a115-vintages`, `AWS_DEFAULT_REGION=eu-west-2` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_013`, `SEAL_013` (the 013 declaration's digest prefix, `d20d5920`) |

Both jobs: `type: cron`, `runtime: docker`, `dockerfilePath: ./Dockerfile`,
`region: frankfurt`, `plan: starter`, `autoDeploy: false`. `render.yaml` is
the blueprint and must match this table.

**Where the unsynced values live (from 2026-09-16).** The five secrets are
in the dashboard-managed environment group `vintage-secrets`, linked to both
cron jobs and referenced from the blueprint with `fromGroup`; they are no
longer declared per job. Background: the first scheduled `tracker-013` run
(09:00 UTC, 2026-09-16) failed with the `a115-cli-jordan` key although the
manual run at 22:22 UTC the night before had succeeded with the writer key.
The hypothesis that a blueprint sync had re-applied the launch-time value
did not fit the timeline: the last sync-triggered deploy was at 21:56 UTC
and the last deploy of any kind (a1c2624) at 22:20 UTC, both before the
22:22 UTC success, and no deploy followed. The likely cause is a per-job
dashboard edit that was not saved on that job. The group removes the
per-job edit as a failure mode either way.

**Superseded on 2026-09-17, kept above as it was written.** The paragraph
above is wrong in its conclusion, and the evidence is a second identical
failure. `tracker-013` failed again on its scheduled run at 09:01 UTC on
2026-09-17 with the same error, in `pull-state`:

    botocore.errorfactory.AccessDenied: An error occurred (AccessDenied)
    when calling the GetObject operation: User:
    arn:aws:iam::713341927530:user/a115-cli-jordan is not authorized to
    perform: s3:GetObject on resource:
    "arn:aws:s3:::a115-vintages/state/013/data/raw/neso/013/2026-09-15/
    daily_balancing_costs_2026-27.csv"

The pattern across the three runs held so far is the diagnostic one:

| run | trigger | outcome |
|---|---|---|
| 2026-09-16 09:00 UTC | schedule | AccessDenied as `a115-cli-jordan`, exit 1 |
| 2026-09-16 09:58 UTC | manual | succeeded; pulled 6 files, pinned 3, pushed 6 |
| 2026-09-17 09:01 UTC | schedule | AccessDenied as `a115-cli-jordan`, exit 1 |

So the environment group was created and the manual run saw it, but the
**scheduled** runs did not. Neither cron job has been deployed since
`dep-daks9adbedkc73cu5keg` at 2026-09-15T22:20Z (commit `a1c2624`), which
is *before* the group was made on 2026-09-16. A Render cron job's scheduled
runs use the environment captured by its last deploy; a manually triggered
run picks up the current values. That is the whole discrepancy, and it means
**an environment fix to a cron job with `autoDeploy: false` does nothing
until the job is deployed.**

`vintage-capture` is unaffected and ran clean at 06:35 UTC on 2026-09-17, so
whatever key its deployed environment carries is adequate for what it does;
only `tracker-013`'s deployed environment is wrong. The fix is a deploy of
`tracker-013` alone, at the same commit, so that only the environment
changes:

    render deploys create crn-dakrtsbl550s73alah40 --commit a1c2624 --wait

**Checked in the dashboard, same day: it does.** Both cron jobs define the
AWS key pair at the job level *as well as* linking the group, so every secret
in `vintage-secrets` is duplicated on the job that uses it:

| | job-level variables | linked group |
|---|---|---|
| `tracker-013` | `AWS_ACCESS_KEY_ID`, `AWS_DEFAULT_REGION`, `AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_013`, `SEAL_013`, `VINTAGE_STORE` | `vintage-secrets` |
| `vintage-capture` | `AWS_ACCESS_KEY_ID`, `AWS_DEFAULT_REGION`, `AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_CAPTURE`, `VINTAGE_STORE` | `vintage-secrets` |
| `vintage-secrets` holds | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_013`, `HEALTHCHECK_URL_CAPTURE`, `SEAL_013` | — |

Four of `tracker-013`'s six job-level variables are also in the group. The
group therefore did not replace the per-job values; it shadowed them, or was
shadowed by them, and the job has carried two sources for the same secret
since 2026-09-16. `vintage-capture` has the same duplication and works only
because its job-level pair happens to hold the writer key.

That leaves exactly one fact undetermined from here, and it is a two-second
check by eye that should not be done by reading key material into a
transcript: **is `tracker-013`'s job-level `AWS_ACCESS_KEY_ID` the same as
the group's?**

- If it differs, the job-level value is the `a115-cli-jordan` key and a
  deploy on its own would re-apply it. Deploying alone would not fix this.
- If it matches, the job-level value was corrected on 2026-09-16 and only the
  deploy snapshot is stale.

**The fix that is correct either way, and the one to take:** delete from
`tracker-013` the four job-level variables the group already defines
(`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_013`,
`SEAL_013`), leaving `AWS_DEFAULT_REGION` and `VINTAGE_STORE`, which is what
`render.yaml` declares as plain values. Then deploy. That makes the group the
single source of every secret, which is what creating it was for, and removes
the duplication as a failure mode rather than guessing which copy is live.
The same duplication on `vintage-capture` should go the same way before it
bites there too.

**Done on `tracker-013`, 2026-09-17, at the sponsor's instruction.** The four
duplicated job-level variables were deleted from the job; `AWS_DEFAULT_REGION`
and `VINTAGE_STORE` remain, which is exactly what `render.yaml` declares as
plain values, and `vintage-secrets` is still linked with its five. Verified
after a reload: the job's own Environment Variables list is now those two and
nothing else, so the group is the single source of `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_013` and `SEAL_013`. No value was
read or written, and no key material passed through the session.

`vintage-capture` still carries its own duplicate `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY`. It was left alone deliberately: it works today, and
changing a working job is a separate decision.

**Deployed and verified, 2026-09-17 14:37-14:38 UTC. The job is fixed.**

`render deploys create --commit <sha>` is refused for a cron job ("cannot
deploy cron job service ... by commit reference ID"), so the deploy takes the
branch head: `render deploys create crn-dakrtsbl550s73alah40 --wait`. That
built `fa41084` rather than `a1c2624`. Checked before deploying: the build
inputs (`pyproject.toml`, `uv.lock`, `Dockerfile`, `.python-version`) are
identical between the two, and the only code the job runs that differs is
`scripts/run-013-render` (the exit-code fix above) and
`capture/state.py` (the `--include` globs of `f6eea13`, which the current
`run-013-render` already depends on). Deploying the head is therefore the
coherent pair, not a mixture.

A one-off verification run on the new deploy
(`render jobs create crn-dakrtsbl550s73alah40 --start-command scripts/run-013-render`)
succeeded in 25 seconds and did the whole job:

    pull-state 013: 7 file(s)
    pinned data/raw/neso/013/2026-09-17/daily_balancing_costs_2026-27.csv
    pinned data/raw/neso/013/2026-09-17/daily_balancing_volume_2026-27.csv
    pinned data/raw/neso/013/2026-09-17/disaggregated_bsad_2026-27.csv
    neso 2026-09-17: fetched 3, verified and skipped 0
    push-state 013: 6 file(s)
    === done

So `AccessDenied` is gone, and the 2026-09-17 vintage the failed 09:00 run
missed is pinned after all — the gap in the daily NESO series is closed
rather than left. Batch 1 remains eligible from 2026-09-19 and nothing about
it has been fetched.

**A one-off job's logs are a separate resource from the service's.** Use
`render logs --resources job-<id>` for a triggered run; the service's own log
stream does not carry it, which makes a successful triggered run look silent
if you only watch the service.

### The laptop watchdog has been failing since 2026-09-16, and nothing said so

Found while checking what cleanup remained, 2026-09-17. The systemd user timer
is installed and enabled and fires twice daily, and its last three runs all
failed in about a second:

| run | result |
|---|---|
| Sep 16 10:59 BST | ok (this is the sync committed at `4609d3c`) |
| Sep 16 22:59 BST | FAILED |
| Sep 17 11:00 BST | FAILED |

    botocore.exceptions.ProfileNotFound: The config profile (a115-watchdog)
    could not be found

`scripts/check-vintages` runs with `AWS_PROFILE=a115-watchdog`, which the
bootstrap note of 2026-09-15 says to put in `~/.aws/credentials`. That file
now holds `[default]` and nothing else, and was itself rewritten at 15:10 on
2026-09-17 to 991 bytes — the same size as `credentials.bak.1780496153` from
June, which also holds only `[default]`. Something is rewriting that file and
dropping the section. Restoring it needs the watchdog access key from the
bootstrap note, which is the sponsor's to handle; no key material was read
here.

**The consequence is the part that matters:** the archive has not synced into
the repository since the morning of 2026-09-16. `data/manifests/` holds
2026-09-15 and 2026-09-16 and not 2026-09-17, although the store has that
day's manifest and its five proof files — the container check listed them.

**And the reason nobody noticed is structural.** Both Render jobs ping
healthchecks.io and are watched. The watchdog's only failure channel was
`notify-send`, which under a systemd *user* service reaches no desktop bus,
and the unit sets no environment at all. `scripts/check-vintages` pings
`HEALTHCHECK_URL_WATCHDOG` on success and `/fail` on failure, and is a no-op
until that variable is set.

**Armed 2026-09-17.** A fourth healthchecks.io check, `vintage-watchdog`, was
created in the same project (12 hour period, 2 hour grace, e-mail integration
like the other three) to match the timer's twice-daily schedule. The ping URL
is **not** in this repository and must not be put here: a healthchecks.io ping
URL is a capability URL, and `render.yaml` keeps the other two out of git for
exactly that reason. It lives in a local drop-in,
`~/.config/systemd/user/vintage-watchdog.service.d/healthcheck.conf` (0600),
and is recorded beside the other two in
`~/.aws/vintage-bootstrap-2026-09-15.txt`. Verified end to end:
`systemctl --user start vintage-watchdog.service` exits 0 and the check shows
the ping. The committed unit in `ops/systemd/` is unchanged, so
`ops/install-watchdog` stays safe to re-run — the drop-in survives it.

**`s3:GetBucketVersioning` is not worth granting after all.** Under the
watchdog's own identity `bucket-settings` reports "as expected"; it only fails
when `capture check` is run as a Render job under the writer key, which is an
ad-hoc diagnostic and not part of normal operation. Nothing to do.

### `vintage-capture` cleaned up the same way, 2026-09-17 14:44-14:46 UTC

Its three duplicated job-level variables (`AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `HEALTHCHECK_URL_CAPTURE`) were deleted, leaving
`AWS_DEFAULT_REGION` and `VINTAGE_STORE`, and the job was deployed
(`dep-dalvq3u1egvs73814ee0`). Both cron jobs now take every secret from
`vintage-secrets` and nothing else, which is what the group was created for.

**The capture was not re-run to verify, deliberately.** A second `capture run`
on the same day is *not* idempotent in the way it looks: `run.py` reads the
day's manifest and writes `existing + new` back, then re-witnesses the
concatenated bytes and overwrites `proofs/<day>.ndjson.*`. A verification run
would therefore have lengthened today's manifest and destroyed the timestamp
proofs over the bytes the 06:30 run actually captured. Anyone tempted to
"just trigger it again" to test something should read that code first.

The safe check is the watchdog, which only ever calls `get` and `keys`:

    render jobs create crn-dakrtsbl550s73alah50 \
      --start-command "uv run --no-sync --group capture --group registers grid-mysteries capture check"

It read `manifests/`, `proofs/` and all of `state/013/` without a single
access error, and named the identity it was running as:

    User: arn:aws:iam::713341927530:user/vintage-capture-writer

So the group supplies the **capture writer**, not `a115-cli-jordan`, and the
cleanup is confirmed good on both jobs.

**Two things that check turned up, neither caused by the cleanup.**

1. `check-vintages` reports FAILED under the writer key, and always will:
   `check_bucket_settings` calls `GetBucketVersioning`, which
   `vintage-capture-writer` is not authorised for. The watchdog is a laptop
   tool run with an administrative identity; it is not runnable as a Render
   job as it stands. Either grant the writer `s3:GetBucketVersioning` or have
   the check skip that one when the call is refused.
2. `sync MISMATCH` on `state/013/.../acquisition-log.json` and
   `.../neso-manifest.json`: the store is ahead of the repository, because the
   14:38 recovery run pinned the 2026-09-17 vintages and nothing has synced
   them down yet. **The laptop watchdog needs a run and a commit** — note that
   the laptop's own AWS session was expired as of this afternoon, so that
   needs re-authenticating first.

**Standing consequence for this file:** whenever a secret or environment
value used by a cron job changes, the job must be deployed for the schedule
to see it. Add the deploy to the change, or the next scheduled run keeps the
old value silently.

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
until the calendar's block is mined; an `ots upgrade` sweep in the watchdog
is a follow-up, not yet built) and RFC 3161 tokens from freetsa.org and
DigiCert. Proofs go to `proofs/`. `scripts/freeze` stamps every
declaration at the freeze with the same three proofs.

## 7. Watchdog (`scripts/check-vintages`, systemd user timer)

`Persistent=true`, on boot and every twelve hours. Five checks: every job's
`status/latest.json` is younger than its schedule allows; the latest run's
artefact counts and bytes per resource sit inside a band learned from the
thirty days before it (anchored on `latest.json`, not on today's date, since
the 04:12 run precedes the 06:30 capture); a random sample of yesterday's manifest entries re-downloads and
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

## 10a. Build and deployment status (2026-09-15)

Parts 1 to 6 are built and committed; nothing is deployed and no crontab
line has been changed. **Prerequisites done by the sponsor on
2026-09-15:** both buckets (`a115-vintages`, `a115-vintages-logs`) and the
three IAM users exist via `ops/aws-bootstrap.sh` (first run failed on a
stdout capture bug, fixed; second run completed; Object Lock verified); the
three access keys and the two healthchecks.io ping URLs are held by the
sponsor; the watchdog profile is on the laptop. **Still to do:** `render
login`, push the branch, launch the blueprint from the dashboard and enter
the unsynced variables, then `ops/install-watchdog` and the two crontab
removals. Part 5 (the ESO map) is the plan's `ESO-MAP`
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

## 12. Proposed, 2026-09-17: demand-connection sources and the constraint forecast (not built, not fetched)

*From the inventory in `ops/DEMAND-CONNECTION-SOURCES.md` (Job 1 of the
session brief of 2026-09-17) and the 013 forecast note. Nothing below is in
`plan.py` yet, no schema pass has run, and the first fetch waits for the
sponsor's seal. The inventory's headline is that no public register of
demand connections exists, so this section captures the few artefacts that
do, in vintages, before Gate 2 Phase 2 demand offers (September 2026 to
March 2027) and Ofgem's fee decisions change them.*

Proposed `PLAN` entries, in the plan's own terms (bytes identical to an
earlier day are linked, not rewritten, so a daily cadence on a monthly file
costs one HEAD-sized manifest line a day):

| name | source / resource | strategy | params | why |
|---|---|---|---|---|
| `NESO-EA-REGISTER` | `neso` / `existing-agreements-register` | `url` | `https://www.neso.energy/document/373996/download` | the one NESO list naming demand projects; overwritten in place under one document id (v.2.0, 11 Jun 2026; the 2026-01-22 bytes differ) |
| `NESO-CONNECTIONS-REFORM-RESULTS-PAGE` | `neso` / `connections-reform-results-page` | `url` | `https://www.neso.energy/industry-information/connections-reform/connections-reform-results` | the page that links the EA register; catches a re-issue or a Phase 2 demand publication the day it lands |
| `NESO-24MA-CONSTRAINT-COST-FORECAST` | `neso` / `24-months-ahead-constraint-cost-forecast` | `ckan` | `resource_id=28b85d3f-a1cc-4bb9-80af-600f2cca266a` | 013 forecast note: 384 bytes, overwritten monthly, July 2026 vintage already lost |
| `NESO-24MA-CONSTRAINT-LIMITS` | `neso` / `24-months-ahead-constraint-limits` | `ckan` | resource id to record from the package (`24-months-ahead-constraint-limits`) | sister dataset, same overwrite pattern |
| `NESO-BSUOS-MONTHLY-FORECAST` | `neso` / `bsuos-monthly-forecast` | `ckan` (needs a package-listing variant: a new resource id each month, like the skip-rate files) | package `bsuos-monthly-forecast` | dated by NESO already; cheap insurance against a page reorganisation like the MBSS one (`data-portal/mbss` now 403) |
| `UKPN-LARGE-DEMAND-LIST` | `ukpn` / `large-demand-list` | `url` | the Opendatasoft CSV export of `ukpn-large-demand-list` (export URL to confirm on the dataset page; the API export form is `/api/explore/v2.1/catalog/datasets/ukpn-large-demand-list/exports/csv`) | anonymised, but the only DNO demand-project list; single live dataset, last modified 2025-11-04 |
| `UKPN-DATA-CENTRES-BY-LA`, `UKPN-DEMAND-MOD-LEAD-TIMES` | `ukpn` / … | `url` | same export form, dataset ids from the inventory | aggregates that name no project but move when the queue moves |
| `NGED-CONNECTIONS-REFORM` | `nged` / `connections-reform-register`, `connections-reform-outcomes` | `url` | the two CSV URLs on `connecteddata.nationalgrid.co.uk` (to record; dated file names `251212`, `260709`) | CMP435 projects NGED manages; demand inclusion undetermined until the schema pass |
| `SSEN-ECR` | `ssen` / `embedded-capacity-register` | `ckan` with a `base` parameter (`https://data-api.ssen.co.uk`) — a small change to `strategies.ckan`, which today assumes the NESO API base | package `embedded_capacity_register` | SSEN is the one DNO that keeps monthly vintages (Oct 2023 to Sep 2026) as separate resources; capturing them makes a DNO's own history readable back |
| `OFGEM-CURATE-PAGE` | `ofgem` / `data-centre-connection-reforms` | `url` | the consultation page | catches the decision document the day it is published |
| `ENA-CONNECTIONS-DASHBOARD` | `ena` / `connections-data-page` | `url` | `https://www.energynetworks.org/industry/connecting-to-the-networks/connections-data` | weekly overwrite, zero Wayback captures; the HTML alone may not carry the widget's data, which the first capture will show |

Not proposed: the ECRs of NGED, UKPN, NPg, SPEN and ENWL (generation and
storage only; demand is not in scope, and the vintage archive's purpose here
is demand); the NESO Demand IRN and the DNO call for input (confidential,
unpublished); DESNZ's strategic demand list (promised, not published).

Order of work once the sponsor says so: (1) seal; (2) one manual fetch of
each artefact into `data/raw/<source>/…`, journalled with digest; (3) the
schema pass, `scripts/schema-report csv|xlsx <file> <archive>`, committed
under `archives/neso-ea-register/`, `archives/ukpn-large-demand-list/`,
`archives/nged-connections-reform/`, `archives/ssen-ecr/`; (4) the `PLAN`
entries above, with the `ckan` base parameter and the package-listing
variant built and tested against the local store; (5) deploy `vintage-capture`
(a plan change is a code change, so the cron job must be deployed for the
schedule to see it, per §5). Nothing analytical follows from this section:
a declaration over any of these archives is a separate, later act.

**Built and live-tested 2026-09-18, not deployed.** The seal was given the
same day. `plan.py` now carries `NESO-EA-REGISTER`,
`NESO-CONNECTIONS-REFORM-RESULTS-PAGE`, `NESO-24MA-CONSTRAINT-COST-FORECAST`,
`NESO-24MA-CONSTRAINT-LIMITS`, `NESO-BSUOS-MONTHLY-FORECAST`,
`UKPN-OVERALL-QUEUE-INSIGHTS`, `NGED-CONNECTIONS-REFORM-REGISTER`,
`NGED-CONNECTIONS-REFORM-OUTCOMES`, `SSEN-ECR`, `OFGEM-CURATE-PAGE` and
`ENA-CONNECTIONS-DASHBOARD`. Three pieces of machinery were needed and are
tested: a per-resource `headers` field (the browser user agent SSEN's and the
ENA's edges require, declared on those two resources only), a `base`
parameter on the `ckan` strategy for portals other than NESO's, and a
`ckan_package` strategy that reads `package_show` and downloads only the listed
resources whose `last_modified` differs from the last capture, each file its
own dataset (`<name>-<resource id>`), so SSEN's 38 vintages and NESO's monthly
BSUoS files are captured once each. Against a local store on 2026-09-18 the
eleven entries captured 199 artefacts with no error (SSEN 43 files, 89 MB; the
BSUoS package 141 CSVs), and a second-day run downloaded only the changed
listings. The first sealed fetch itself was done by hand with
`scripts/pin-demand-sources` and is recorded in
`archives/demand-sources/manifest-2026-09-18.json`; the schema pass is in
`ops/DEMAND-CONNECTION-SOURCES.md` §4. **The UKPN key, same day.** The
sponsor registered on UKPN's open-data portal (Huwise login) and generated an
API key labelled `grid-mysteries vintage-capture` (permission: browse all
datasets); the extension refused to hand the value to the session, so the
sponsor saved it to `~/.aws/ukpn-api-key` (0600) by hand. With it the three
exports carry their rows (496 / 45 / 70). `plan.py` carries them as
`UKPN-LARGE-DEMAND-LIST`, `UKPN-DATA-CENTRES-BY-LA` and
`UKPN-DEMAND-MODAPP-LEAD-TIMES` with a `secret_header` resolved at run time
from `UKPN_API_KEY`; a resource whose variable is unset is **reported as an
error and never fetched**, because a keyless export is a header-only file that
would otherwise be captured as a vintage, and the secret never reaches a
manifest (tested). **`UKPN_API_KEY` added to `vintage-secrets` on 2026-09-18**, at the sponsor's
request, through the Render REST API (`PUT /env-groups/evg-dal68s5g1s2s73ecrrb0/env-vars/UKPN_API_KEY`)
with the value read from the local key file; the group now holds six
variables and is linked to both cron jobs. The Render CLI has no env-group
command, so the API with the CLI's own token is the route. **Still to do, the
sponsor's act:** deploy `vintage-capture`
(`render deploys create crn-dakrtsbl550s73alah50 --wait`), because a plan
change is a code change and an environment change alike reach the schedule
only through a deploy (§5).

**Deployed 2026-09-18 (`dep-dam7kb142hec738jkrb0`, by the sponsor), and
verified with a one-off `capture plan` job: the deployed image lists all 30
plan entries, the eleven demand sources and the three keyed UKPN datasets
among them. The first scheduled capture under the new plan is the 06:30 UTC
run of 2026-09-18.**

**A mistake, recorded.** The first verification job was written as
`sh -c "… test -n \"$UKPN_API_KEY\" …"` to report whether the variable was
present without printing it. Two things were wrong with that. Render
substitutes environment variables into a one-off job's start command
*before* the shell sees it, and the quoting collapsed so the shell tried to
execute the whole string as one command name and failed with "File name too
long", echoing the entire substituted command, **key value included**, into
that job's log (`job-dam7kqtbedkc73achrig`). The key is therefore visible to
anyone who can read the service's job logs on Render, and it passed through
the session transcript. The remedy is rotation: revoke the key on UKPN's
API-keys page, generate a new one, save it to `~/.aws/ukpn-api-key`, and set
it in `vintage-secrets` again through the API, then deploy. **Standing rule
from this:** never reference a secret variable in a Render start command,
even to test its presence; the environment group's variable list, read
through the API, is the check.

### 2026-09-18: two alerts, one watchdog bug and one Cloudflare finding

**04:12 BST, `vintage-watchdog` DOWN.** The first pre-capture run since the
timer was re-enabled. `check_bands` looked up `status/vintage-capture/
2026-09-18.json`, which cannot exist at 04:12 because the capture runs at
06:30 UTC, and reported `no status for 2026-09-18` as a failure. Every other
check passed. Fixed: the band is anchored on `status/latest.json` and its
history is the thirty days before *that* day; staleness stays with
`check_freshness`. Regression test
`test_a_run_before_the_day_s_capture_bands_the_latest_status_not_today_s`.
The 16:12 run would have passed on its own; the 04:12 run would have failed
every day.

**07:41 BST, `vintage-capture` DOWN, Render "Exited with status 1".** The
first scheduled run under the demand-source plan. 26 of 29 entries captured
(the manifest for 2026-09-18 was written and witnessed; nothing is lost).
Three errors, all HTTP 403: both NGED DSA PDFs (the CSVs from the same host
passed) and the ENA connections page (sent the browser agent). Probe from the
job's own egress (one-off job `job-dameoo2d0e5s73f5skf0`, egress
74.220.51.146): all three URLs answer 403 with `cf-mitigated: challenge` and
Cloudflare's "Just a moment..." page under the project agent, two browser
agents and a browser agent with Accept headers; the NGED CSV answers 200
under all of them. From the laptop (82.44.101.149) every URL answers 200
under every agent. So the 2026-09-18 note in `ops/DEMAND-CONNECTION-SOURCES.md`
that "the ENA site refuses the identifying user agent" was a laptop finding
that does not transfer: the edge challenges the *address*, and no header
passes a JavaScript challenge. Remedy in the plan: NGED's two `ckan_package`
entries take `formats: CSV,XLSX` (the PDFs are methodology documents, pinned
in `archives/demand-sources/manifest-2026-09-18.json`); the ENA page leaves
the plan for `TO_ADD` with the finding. A Wayback save was also tried from
the laptop and was rate-limited (429), so that route is untested. Reaches the
schedule only through a push and `render deploys create
crn-dakrtsbl550s73alah50 --wait --confirm`; until then the 06:30 run fails
daily on the same three entries and the healthcheck stays down.

**How to probe from Render's egress without quoting.** Render's one-off
start command keeps quote characters literally and splits on whitespace
(`sh -c "…"` hands the shell a string that begins with a quote, and
`echo <b64> | base64 -d | sh` echoes the pipe), which is the same parsing
that leaked the UKPN key above. A single token with no whitespace survives:

    render jobs create crn-dakrtsbl550s73alah50 \
      --start-command "/usr/local/bin/python3 -c exec(bytes.fromhex('<hex of a script>').decode())"

with `xxd -p script.py | tr -d '\n'` for the hex. The script uses the stdlib
only, touches no store and references no variable. Its log is read with
`render logs --resources job-<id>`.

**Pushed and deployed 2026-09-18 07:55 UTC (`b5bff1a`, `dep-damet6v40ujc73amb0ag`,
by the sponsor), verified with a one-off `capture plan` job
(`job-dametiad0e5s73f6duv0`): the deployed image lists 28 plan entries, both
NGED entries among them, and the ENA page under TO ADD. The first scheduled
run under this plan is the 06:30 UTC run of 2026-09-19; the capture
healthcheck clears on its success, and the watchdog's freshness check
follows at the next 16:12 or 04:12 run after that.**



### 2026-09-18 09:00 UTC: `tracker-013` failed at pull-state, the day before batch 1

**10:01 BST, `tracker-013` DOWN, "Exited with status 1".** The log ends at
`pull-state 013: 12 file(s)` with two `MISMATCH` lines
(`evidence/acquisition-log.json`, `evidence/neso-manifest.json`) and no
runner output: `pull-state` exits 1 on any MISMATCH, so `scripts/run-013-render`
stopped before `run.py`, and nothing was acquired for 2026-09-18
(`state/013/data/raw/neso/013/` ends at 2026-09-17).

**Cause, structural.** The live image (`dep-dalvm9e1egvs7380li60`, commit
`fa41084`) carries the repository's copies of those two files as they were at
build time. The 14:44 recovery run of 2026-09-17 then pinned that day's
vintages and pushed a newer log and manifest to the archive; the laptop synced
and committed them (`0444cb8`), but the image did not change. `pull` replaces
a local file only when the archive's bytes extend it, and `write_json`
re-serialises the whole document, so the two are MISMATCH, not `grew`. This
would recur after every run that pushes state: the job can succeed only on
the first run after a deploy. It would have failed again on 2026-09-19, batch
1's first eligible day.

**Fix.** `pull-state --overwrite`: the archive wins for a file that differs,
reported as `replaced`. The job passes it (the image's copy is a snapshot,
never an authority); the laptop watchdog does not (a MISMATCH there means the
repository and the archive diverged, and a person looks). Test
`test_pull_overwrite_lets_the_archive_win_for_the_unattended_job`.

**What today's miss cost.** The tracker's own 2026-09-18 pin is absent from
`state/013/`. The 06:30 capture job holds NESO's 2026-09-18 BSAD file under
`raw/neso/disaggregated-bsad-2026-27/2026-09-18/`, and its CKAN metadata for
the costs and volume files is unchanged since 2026-09-15, so the archive holds
what NESO published today either way. A one-off `scripts/run-013-render` on
the new image pins the day into `state/013/` as the 2026-09-17 recovery did.

**Sponsor's acts, in order:** push; `render deploys create
crn-dakrtsbl550s73alah40 --wait --confirm`; then `render jobs create
crn-dakrtsbl550s73alah40 --start-command scripts/run-013-render` and read its
log with `render logs --resources job-<id>`; then the laptop watchdog
(`systemctl --user start vintage-watchdog.service`) syncs the new state down
for a commit. All before 09:00 UTC on 2026-09-19.
