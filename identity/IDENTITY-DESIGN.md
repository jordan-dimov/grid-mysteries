# The identity table as a Morpholog record — design, for the sponsor's word

**Written 2026-09-30; the sponsor's decisions on its four questions came
the same night and are recorded at the end. Frozen by `scripts/freeze` and
committed with the programme beside it (`identity-register.morph`,
programme hash `sha256:312e6e56…`, pinned in `PROGRAMME_HASH.json` and held
to the compiled route by `scripts/check-programmes`). Nothing is built,
deployed or recorded; the build waits for the sponsor's word.** Answers
etrmbiz `notes/2026-09-30-morpholog-better-use-2.md` item 1 and the data
plan's item 5.

## What 019 did by hand, and what the record makes of it

019 resolved 1,375 printed customer names to Companies House companies
under two rule versions and 119 human decisions. The machinery was three
files: `links.ndjson` (one line per name and rule version, append-only:
3,230 lines), `links-proposed.json` (the 126 names the rule could not
settle, with their candidates) and `links-admitted.json` (a person's
admissions and refusals, initials and a date; 91 admitted, 28 refused, two
under the copy-date rule with several holders, two under the spacing-only
rule). That is admission standing under authority with as-of replay,
implemented in JSON, and it already has to answer "what did we believe on
date D" by reading git history.

Under the programme:

| in 019's files | in the record |
|---|---|
| a rule version (`019-r2-v1`, `019-r2-v2`) and the frozen declaration it comes from | `RuleVersion(rule_version, declaration_digest)`, registered by the human (freezing is the human's act) |
| a printed name (or, later, a Project ID or a content-identity row key) | `RegisterSubject(subject, kind, first_printed)`, registered by the machine |
| a `links.ndjson` line of class `exact` or `previous-name` | one `LinkProposed(link, subject, company, #exact / #previous_name, rule_version, evidence_digest, proposed_on)` |
| a line of class `ambiguous`, `unresolved` or `identity-guard`, with its candidates | one `LinkProposed(…, #candidate, …)` per candidate, plus `SubjectUnresolved(subject, rule_version, evidence_digest, proposed_on)`: the record says the rule looked |
| an admission in `links-admitted.json` (`company_number`, `on`, `by`) | `admit_link(link, admitted_on, #none, #none, rule_of_admission, note_digest)`, run by the human; the actor is the audit row's, not a string |
| a copy-date admission (`holders` with tenures) | one `admit_link` per holder's proposal, with `tenure_from` / `tenure_until` |
| a refusal | `refuse_link(link, refused_on, reason_digest)`, human only |
| a changed mind (today: edit the file) | `withdraw_admission(link, withdrawn_on, reason_digest)`; the admission stays, dated |
| `evidence_digest` / `search_sha256` | the same digests, on the proposal |
| the note in the file's header stating the rules of admission | the note's digest on each admission; its text stays in the repository |

Nothing in the record is ever retracted. Every predicate that carries a
belief is append-only, and a belief changes only by a later, dated act.

## The two clocks and the one query

- **What did we believe subject X was on date D.** Read `LinkAdmitted`
  joined to `LinkProposed`, minus `AdmissionWithdrawn`, as of the last
  transition on or before D (`inspect claims --as-of <transition>`, or the
  generated client's `claims_named(…, as_of=)`). The answer is a set of
  (company, rule version, admitted on, by whom) and it is the record's
  own state, not a reconstruction from git.
- **Which company bore X at register copy date C.** The admitted link
  whose tenure contains C (`tenure_from` inclusive, `tenure_until`
  exclusive; `#none` at both ends for an admission that holds for every
  copy). This is 019's copy-date rule, kept as data on the admission so a
  certificate can cite it.

A certificate then cites three digests: the rule version's declaration,
the proposal's evidence, and the admission's note, with the admission
date and the actor from the audit row.

## Authority

The two-role pattern of the research record: `establish_identity_governance`
binds the human actor to a login role only a person holds and the machine
actor to the engine's role (`ActorAssertionRestricted` /
`ActorAssertionAuthority`, refused by the runtime when the proposing login
is not the bound one). `AdmitAuthority` is the human's alone:
`admit_link`, `refuse_link`, `withdraw_admission`, `register_rule_version`
and `register_audit_signing_key` require it. `ProposeAuthority` is the
machine's alone: `register_subject`, `propose_link`, `record_unresolved`
require it. A proposal the human did not make cannot be admitted by the
machine; a link the rule did not surface cannot be admitted at all (the
human's remedy is a proposal under a new rule version, which is a frozen
amendment, as 019 amendment 1 was).

## Route report (Morpholog v0.0.13, `check -v`)

```
ok: identity/identity-register.morph
program: identity_register
  predicates: 12
  definitions: 0
  invariants: 14
  transformations: 9
  intents: 0
  derived claims: 0
  invariant checks: compiled
```

Eight declared invariants (proposals, unresolved records, admissions,
refusals and withdrawals each name what they refer to; an admitted link
was not refused) plus six the runtime generates from `unique by`. All
compile: no `or`, no defined calls, so `scripts/check-programmes` would
hold the programme to the compiled route as it does the TEC and Bill
records. Hash `sha256:312e6e56f3c9bb3a466679828199e2213f85529ed4af6c97c17af7ff1d87257c`.

## What the migration from files costs

Counted from 019's files as they stand tonight (rule versions v1 and v2):

| act | rows | who runs it |
|---|---|---|
| `establish_identity_governance` | 1 | the human, as `gm_human` |
| `register_rule_version` | 2 | the human |
| `register_audit_signing_key` | 1 (a new key, `identity-2026`) | the human |
| `register_subject` | 1,855 (1,375 copy names + 480 earlier names) | the machine, one batch |
| `propose_link` `#exact` / `#previous_name` | 3,031 (v1 1,302; v2 1,729) | the machine |
| `propose_link` `#candidate` | 527 (v1 195; v2 332) | the machine |
| `record_unresolved` | 199 (v1 73: 47 unresolved + 26 ambiguous; v2 126: 79 unresolved + 46 ambiguous + the identity guard) | the machine |
| `admit_link` | 93 (89 plain, 4 under the copy-date rule: two spellings × two holders) | the human |
| `refuse_link` | 28 | the human |

Build, on the record engine that TEC and Bill already share
(`grid_mysteries.record`: config, pinned client, marker-guarded transact,
witnessed checkpoint, verified pack): the programme with its controls
(refusals to prove: the machine admitting, the human proposing, admitting
a refused link, admitting twice, withdrawing what was never admitted), an
importer that reads the three files into the batches above, and the 019
runner reading its links through `claims_named` instead of the files.
About two days of session work; the sponsor's part is the six human acts
above and one batch of 121 admissions and refusals through the launch
pattern, under an hour. A new database `grid_mysteries_identity` and a
new signing key, backed up as the TEC key is.

Doctrine on dates: the record is not backfilled. Each row carries the date
the rule proposed or the person decided (30/09/2026) as data, and the
audit row carries the instant it was recorded; the record says both, as
the TEC engine's reproduction of 014 did. The three files stay in the
repository as the evidence of the 30/09 run; from the day the record is
live, the runner writes proposals to it and the person admits in it, and
the files are not written again.

## Decisions (the sponsor, 30/09/2026)

1. **Subjects are names only.** `kind` is `#printed_name` for every
   subject registered under this design; `#project_id` and `#row` wait for
   a later rule version and their own amendment.
2. **No hand proposals.** Proposals are the rule's alone
   (`ProposeAuthority`). A name the rule cannot surface waits for an
   amended rule, frozen as 019 amendment 1 was.
3. **No re-admission.** `LinkAdmitted` is unique by link; a withdrawn
   admission is final for that proposal. The route back is a fresh
   proposal under a new rule version.
4. **Digests in the record.** The rule of admission, the note and the
   evidence enter the record as digests; their text lives in the
   repository, as the declarations do.
