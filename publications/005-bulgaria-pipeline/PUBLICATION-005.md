# Publication Pack 005 — 9,330 MW of Bulgarian data centres, and thirty

No new analysis. Every number in the visual (`ladder.svg`, rendered by
`render.py` from `evidence.json`, which transcribes — with sources — the
figures pinned in Forward Mysteries F003 and F004) is in
`investigations/forward/F003-time-to-power-bg-ro/` and
`investigations/forward/F004-stranded-pipeline-bg/`. F004's declaration was
frozen before its evidence was gathered; its reopening triggers are
published here with the claim, as the forward-track rule requires.
**Human gate: publication.**

## Draft post copy

> Bulgaria's grid operator has received applications for 9,330 megawatts
> of data centres. The country's peak demand is about seven thousand.
> The amount of data-centre capacity actually built is about thirty.
>
> I went looking for the information advantage everyone assumes exists
> in a market like that — the substation nobody has noticed, the
> transformer with room to spare. It isn't there, because ESO publishes
> it. Its map lists every substation's remaining connection capacity,
> split by what has been reserved for generation and for consumption,
> and by the stage each reservation has reached: opinion, preliminary
> contract, contract. The queue is public, by node, and it is updated
> continuously.
>
> And it has been acted on. An ESO connection opinion costs under four
> thousand euros, arrives in fourteen days, lasts a year, and reserves
> nothing. By August, 3,795 MW of data-centre projects held one. ESO's
> chief executive explained why, in one sentence: investors get an
> opinion first "because a positive opinion increases the value of the
> project and allows it to be sold to a strategic investor."
>
> So I looked for the strategic investors. Not one has bought a
> Bulgarian site at 50 MW or more. The largest transaction in the
> country is an operating colocation business of 14.8 MW. The flagship
> €3 billion campus has a government memorandum and, as of this month,
> no evidenced land, grid contract, permit, customer or contractor. The
> one fully documented case of a developer repurposing a site next to
> its own solar park stalled in June when the municipal council withdrew
> its land consent after a residents' meeting.
>
> What the record shows, then, is not scarcity. It is inventory. Several
> gigawatts of cheap, non-exclusive positions, held by parties who are
> — in the regulator's own words — waiting to sell them to a buyer who
> has not yet appeared.
>
> I don't know how that resolves, and I wrote down in advance what would
> make me look again: a named buyer acquiring a site at 50 MW or more; a
> binding operator capacity agreement; disclosed financing for one of the
> announced campuses; opinion-stage projects visibly moving through
> permits into construction; or evidence of strategic buyers bidding for
> partially developed positions. Until one of those happens, the honest
> reading of 9,330 MW is that it measures the price of an opinion, not
> the demand for a data centre.

## The visual

**`ladder.svg`** — four horizontal bars on one MW scale: requested,
holding an opinion, preliminary contracts, installed — with the 2035
forecast peak as a hairline. The installed bar is a sliver with its label
outside; that is the chart.

## Expert corner

- **The map.** `webapps.eso.bg/joining/public/map`, endpoints
  `get-points.php` (474 substations), `get-lines.php` (810 lines) and
  `get-point-json.php` (per substation, by voltage level: total transfer
  capacity for connection; reserved for generation / consumption / mixed
  / standalone storage / generation-plus-storage / DSOs; remaining
  capacity — each with `opinion`, `pd`, `contract` sub-fields). Verified
  2026-08-26: "remaining" equals total minus the sum of the reserved rows
  at every voltage level of the probed record. Pinned by digest in
  `F003-time-to-power-bg-ro/evidence/reconnaissance-manifest.json`.
- **The rules.** Наредба № 6/2024 (consolidated to ДВ 35/14.04.2026):
  opinion in 14 days (чл. 15), valid one year (чл. 16), no financial
  guarantee for a new consumption object (чл. 16а applies to storage at
  existing sites), preliminary contract requires a right to build,
  connection contract requires an effective building permit (чл. 21),
  position transferable with the site (чл. 20(2)). Study fee for > 100
  MVA: 7,410 BGN excl. VAT (ESO price list).
- **The figures.** 9,330 MW / 5,535 MW intentions / 3,795 MW with
  opinions as of 3 Aug 2026 — ESO figures supplied to economic.bg,
  published 12 Aug 2026, article pinned. ~27–30 MW installed: Capital.bg
  19 Aug 2026 (pinned body). No preliminary contracts with data-centre
  applicants: ESO via Mediapool, 26 May 2026. Regional split (Plovdiv
  2,260 / Burgas 1,860 / Pleven 1,140 / Montana 970 / Sofia 920 / Stara
  Zagora 510 MW) is a press transcription of an ESO briefing and is not
  used in the visual.
- **What F004 tested and how it died.** Pre-declared absorption kill,
  frozen 2026-08-26 (digest `25b50dc6…`): four forcing observations, run
  the same day. O1 found no Bulgarian site marketed with a data-centre
  opinion and no buyer at ≥ 50 MW (falsifier F-A). O3 could attribute zero
  of the 3,795 MW to a named holder — ESO: "the names are not public".
  Verdict: strain *plausible but not measured* (the lapse/conversion
  series is held by ESO and unpublished); commercial form killed by F-A.
- **Reopening triggers** (F004 `NOT-NOW.md`): the five conditions in the
  post, each requiring a primary source with a t_public date.
- **Watch instrument.** A daily snapshot of the map's three endpoints has
  run since 2026-08-26; the first honest read of conversion versus lapse
  by node is due about 24 Nov 2026. Its result will be appended as
  outcome, never used to rewrite this piece.
- **What this does not say.** That the projects are fraudulent, that ESO
  is wrong, or that no data centre will be built in Bulgaria. It says the
  public record contains supply of positions and no evidenced demand for
  them at scale, on the stated date.
