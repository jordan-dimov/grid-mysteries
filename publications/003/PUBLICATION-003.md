# Publication Pack 003 — the half-visible machine

No new analysis. Every number here and in the three visuals
(`overview.svg`, `reel.svg`, `diagram.svg`, rendered by `render.py`
**from the committed evidence files, never typed by hand**) already
exists in the governed record, including the attribution correction
`fnd-003-attribution-corrected`. Corpus: 2026-05-01..31 (episode
2026-05-18..31). **Publication order: this pack publishes before the
benchmark-fragility piece.**

## Draft post copy

> Britain's system operator estimates that "repetitive re-trading" by
> electricity storage behind grid bottlenecks added about £99m to
> balancing costs last year. I tried to reproduce the mechanism from
> public data. I couldn't — and where the reproduction stops turned out
> to be the finding.
>
> Repetitive re-trading is when storage sells electricity, is paid to
> not deliver it because of a transmission bottleneck, and then appears
> scheduled to sell again — potentially being paid to not deliver
> again. It is not prohibited, and the regulator is explicit that it
> can happen while a battery follows every rule: it's what a national
> electricity price plus local grid limits can produce.
>
> So I picked an episode by a rule I froze before touching the data:
> the two weeks in May with the strongest public signature of this
> pattern. It selected fourteen consecutive days of published
> constraint cost at the Scotland–England boundary — £11.5m.
>
> Over exactly those dates, public market data shows GB storage going
> through the visible shape of the mechanism — scheduled to export, bid
> down, scheduled again, bid down again — 8,259 times, involving almost
> 70 GWh of bid-down volume.
>
> One battery went through it 21 times in a single day: 88 separate
> instructions, repeatedly turned from scheduled export through zero
> into full import.
>
> And then the evidence stops. Three links are missing, and they are
> exactly the links the £99m turns on.
>
> First: whether the energy held back was actually re-sold in between —
> the trade happens in markets that publish no such record.
>
> Second: which of those 8,259 repetitions happened behind that
> boundary. NESO publishes where the boundary is. It publishes the
> daily cost of it. It publishes no mapping that ties any unit's
> actions to it. I cannot localise a single cycle — which also means
> nobody outside NESO can.
>
> Third: the operator's own £99m method counts a period as re-trading
> only if a system-flagged instruction was followed by an upward
> schedule revision. I probed the public feeds: schedule revisions are
> never published — they happen entirely inside the window the public
> record doesn't cover. And of the 90,020 storage instructions in my
> fourteen days, only 3.2% carried the system flag. That one battery's
> 21-cycle day? Zero flags. Under the official method, its day might
> not count at all.
>
> So the honest conclusion isn't "£99m is wrong". It's stranger: £99m
> is uncheckable, in both directions, by anyone outside the operator.
> The public record can show the repetitive part. It cannot, by itself,
> prove the re-trading economics.
>
> That matters because Britain is right now weighing new dispatch rules
> for storage behind constraints, motivated by that number. The missing
> inputs are specific: point-in-time schedule revisions, and an
> authoritative map of units to boundaries. Publish those, and outsiders
> can reproduce the diagnosis instead of taking it on trust.
>
> Until then: symptoms visible, diagnosis unreproducible.

## The three visuals

1. **`overview.svg`** — fourteen days, two panels: NESO's published
   daily SSE-SP cost (observed) above GB-wide daily cycle counts
   (concurrence). The panels visibly refuse to correlate — the most
   expensive day had the fewest cycles — which *is* the attribution
   point.
2. **`reel.svg`** — one battery's day: `E_DOLLB-1` on 2026-05-20,
   final-PN export schedule vs deepest accepted instruction, 48
   periods, through zero to −99 MW. Zero SO-flags.
3. **`diagram.svg`** — the signature chain OBSERVED → OBSERVED → **?**
   → OBSERVED, the published money side by side, and the two dashed
   boxes explaining why the columns cannot be joined. Closes with the
   thesis sentence.

## Every displayed number, bound to its source

| Number | Value | Source of truth | Governed finding |
|---|---|---|---|
| Selected episode | SSE-SP, 2026-05-18..31 | `evidence/selected-episode.json` | `fnd-003-episode-reconstructed` |
| Repeat-curtailment cycles (GB-wide, episode dates) | 8,259 | `selected-episode.json` → `repeat_curtailment_score` | `fnd-003-attribution-corrected` (labelling) |
| Storage bid-down volume (GB-wide) | 69,869 MWh | `selected-episode.json` → `storage_bid_down_mwh` | `fnd-003-attribution-corrected` (labelling) |
| Published SSE-SP outturn cost, episode | £11,510,565 | `episode-accounting.json` → `published_constraint_cost_for_group_gbp` | `fnd-003-episode-reconstructed` |
| Daily cost / daily cycle series | 14 pairs | `presentation-series.json` (labelling block inside) | — (post-selection description) |
| Focus unit day | E_DOLLB-1, 2026-05-20, 21 cycles, 88 acceptances | `excerpt.json`, `episode-ledger.json` | `fnd-003-episode-reconstructed` |
| Storage BM cashflows (GB-wide, episode dates) | bids −£6.74m · offers +£9.15m | `episode-accounting.json` | `fnd-003-episode-reconstructed` |
| Non-storage BM cashflows (GB-wide) | bids −£3.52m · offers +£78.39m | `episode-accounting.json` | `fnd-003-episode-reconstructed` |
| SO-flag tally | 2,904 of 90,020 (3.2%); focus unit 0 of 1,492 | `so-flag-tally.json` (script `so_flag_tally.py`) | `fnd-003-attribution-corrected` |
| NESO RRT estimate | ~£99m FY 2025/26 (12-hour window), from ~£64m FY 2024/25; pumped storage ~80% of two-year total | pinned Ofgem paper (`reference-manifest.json`, `art-003-ofgem-rrt-paper`) | `fnd-003-attribution-corrected` |
| PN revisions structurally unpublished | 5 probes incl. validation control | `pn-vintage-probe.json` (`art-003-pn-vintage-probe`) | — (registered source) |
| Boundary location public, mapping absent | Scotland diagram + CMIS pinned | `reference-manifest.json` | `fnd-003-episode-reconstructed` |

## Language contracts (carried from the research note, binding)

"Storage", never "batteries", for aggregates (pumped storage is ~80% of
the two-year RRT total). "Repeat-curtailment cycles consistent with
RRT", never "re-trades". Cycle counts and cashflows are GB-wide unless
the line is NESO's own boundary-specific series. No line is a saving,
waste, or "cost of RRT". NESO's dispatch-option assessment is "under
active assessment" — no formal proposal is asserted. The £99m is an
order-of-magnitude estimate with biases both ways (Ofgem's own
characterisation); this pack never claims the true figure is above or
below it.

## Reproduction

`uv run python publications/003/render.py` regenerates the three SVGs
byte-for-byte from committed evidence. The underlying series:
`investigations/003-follow-the-constraint/presentation_series.py`
(post-selection description; no new rule). Full investigation
reproduction is documented in the investigation's `NOTE.md`.
