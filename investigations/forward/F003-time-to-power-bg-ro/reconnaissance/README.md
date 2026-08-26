# F003 — pre-declaration reconnaissance record

**Dates:** 2026-08-25 (background agents) and 2026-08-26 (direct verification).
**Status:** this directory records what was looked at *before* any declaration
was written. Nothing here is a finding of the study. Under the forward-track
protocol (see `../../CANDIDATE-PROTOCOL.md`, "Evidence used to justify
generation only"), it exists so that the eventual `DECLARATION.md` cannot claim
to have predicted what was already known on the day it was frozen.

## What was done

Five reconnaissance agents were run in parallel, each instructed to map the
*availability* of evidence — publisher, document, resolution, access,
machine-readability, what it can and cannot support — and explicitly **not** to
report which substations or regions look attractive or any node-level number.

| file | scope | verification labelling |
|---|---|---|
| `recon-bulgaria.md` | ESO plans, ESO open data and map APIs, Naredba 6 / Energy Act, DSOs, government data, announcements | per item: fetched / snippet / failed |
| `recon-romania.md` | Transelectrica PDRET 2026–2035 and 2024–2033, capacity maps and registers, ANRE Ordin 59/2013 as amended, DSOs, government data, announcements | per item: fetched / snippet / blocked |
| `recon-entsoe.md` | TYNDP 2024/2026 datasets, the nodal grid model and its request route, CGMES datasets, Transparency Platform, Capacitypedia, derived open datasets, licences; draft request wording | per item: fetched / file opened / snippet / not determined |
| `recon-tooling.md` | pypowsybl, pandapower, PyPSA/PyPSA-Eur, other tools; what a CGMES model carries; what a load-injection screen can and cannot say; effort | verified by running on Python 3.14 where stated |
| `recon-commercial.md` | incumbents, demand, transactions, connection rules for large consumers, local-knowledge cost, developer behaviour, other kills | per item: fetched / local extract / snippet / not found |

All five reports are the agents' own text. Each states where its web-search
budget ran out and which fetches failed. Secondary claims in them are
**hypothesis leads, not evidence**, until pinned from a primary source.

## What was verified directly (2026-08-26) and pinned

`../evidence/reconnaissance-manifest.json` lists six ESO EAD artefacts fetched
directly and stored under `data/raw/eso/` with SHA-256 digests:

- the 2021 "Електронна карта за свободен капацитет" page and its one-page
  explanation PDF (`webapps.eso.bg/capacity/`);
- the 2026 "ESO Map" application shell and its two list endpoints
  (`get-points.php`: 474 substation features — 281 at 110 kV, 27 at 400 kV,
  16 at 220 kV, 150 without a voltage class — with autotransformer MVA,
  joined/delivered/installed sums and assigned projects; `get-lines.php`:
  810 lines — 694×110 kV, 63×400 kV, 53×220 kV);
- one per-substation record from `get-point-json.php`, requested to learn the
  **field names only**. Its rows, per voltage level, are labelled (Bulgarian
  verbatim): total transfer capacity for connection; for generating capacity;
  for consuming capacity; for mixed consuming-and-generating objects;
  standalone storage; generation + storage; DSOs including closed DSOs; and
  **"Оставащ капацитет за присъединяване на нови мощности"** (remaining
  capacity for connection of new capacities) — each with `powerMw` and
  sub-fields `opinion`, `pd` (preliminary contract) and `contract`, plus a
  `plannedProject` text.

## Contamination disclosure

Inspecting the structure of the 2021 map page printed the first ~5 values of
each data array (Sofia-area substations) as part of a field-name sample; the
per-substation probe record for one 400 kV substation was fetched and its
labels printed, but its numeric values were not printed or read. No candidate
area named in the commissioning brief (Plovdiv/Rakovski/Maritsa, Maritsa East /
Stara Zagora, Kozloduy, Targovishte, Burgas, Aleko 2, Uzundzhovo, Obraztsov
Chiflik, Madara 2, Pleven 3) was looked up. The Bulgaria agent reports fetching
one per-substation record (`pj.json`) and did not report its values. This is as
clean as a structure inspection can be made and is recorded rather than
claimed away.

## Session note

The five agents were interrupted by a machine restart before any had written
its report to disk; all were resumed from their transcripts and wrote their
reports afterwards. The commercial agent's file was lost and its report was
transcribed from the agent's returned text. Working copies the agents
downloaded (plans, annexes, regulations) were lost with the scratchpad and must
be re-fetched and pinned before any of them is cited as evidence.
