# Watch reading — w-005-eir-response, read 2026-10-15

**Watch**: `w-005-eir-response` (005), resolving observation "NESO's
response to the EIR request of 2026-09-15 for TEC register vintages
2025-07-22 to 2026-05-19 (statutory due date)", holder NESO, due 2026-10-13
(opened in `morpholog/batches/110-forward-launch.v3.ndjson`).

**Outcome recorded**: `resolved`. NESO answered on the due date; this
reading records it two days late, after `scripts/check-record` reported the
watch overdue in CI on 2026-10-14 and 2026-10-15.

**What was read.** NESO's response letter, reference FOI/26/216, dated 13
October 2026, received by email from informationrights@neso.energy on
2026-10-13 15:32 UTC (Gmail id `1a135e5a76d73f80`, per the etrmbiz handover
`notes/2026-10-13-foi-26-216-handover.md`), held outside the repositories at
`~/data/neso-foi-26-216/FOI-26-216 - Response.pdf`, SHA-256
`c11095dc904d367bcb7434f4722689fca05502feaa69e11a53fa9406d475d495` (the
reading digest). It says, under the Environmental Information Regulations
2004: (1) the TEC Register archive is not on NESO's Data Portal at the date
of the letter, and the response provides "copies of all issues of the TEC
Register held in the archive that have a publication date between 23 July
2025 and 18 May 2026"; (2) it provides "copies of all issues of the TWR held
[that] have a publication date after 3 October 2025"; (3) "there is no
other version of the Transmission Works Register other than that which is
published on NESO's website", and CUSC 6.36.2's "Completion Date(s)" "is
provided on the TWR in the column 'MW Effective from'". The disclosure
itself is the zip beside the letter, `FOI-26-216 - TEC&TWR.zip`, SHA-256
`69a2943014b58a5dadde38ef918fea7eae7ee234234bc1078fcfa5fb4e9d9323`, 133
members: 83 TEC Register CSVs (`Q1 TEC/`) and 24 TWR reports (`Q2 TWR/`).

**Not read for this reading**: the members of the zip. Their pinning,
journalling and schema pass are the separate acquisition that this reading
releases (the 13/10 handover, steps 1 and 2), recorded in the TEC history
journal and the TWR journal with their own digests, not here.

**Next**: the watch is resolved. Whether the 83 copies close the 301-day
hole exactly, and what they change in 014, 020 and 021, is decided by those
investigations' own rules after the copies are journalled, never by this
reading.
