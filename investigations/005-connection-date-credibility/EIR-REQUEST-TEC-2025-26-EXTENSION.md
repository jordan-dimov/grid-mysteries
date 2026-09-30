# EIR request FOI/26/216 — extension (draft, not sent)

**Drafted 2026-09-30** for the sponsor to send from his own address as a
reply on the existing thread (NESO's acknowledgement of 16 September 2026,
ref FOI/26/216, statutory due date 13 October 2026). It extends the request
of 15 September (`EIR-REQUEST-TEC-2025-26.md`) with two items that cost
NESO nothing new to locate: weekly copies for 2025-26 that its archive
holds, and CSV renderings of 2014 copies the archive already disclosed in a
spreadsheet format that no current reader opens. Sending is the sponsor's
act; nothing here has left the repository. The text is kept here so that
what was asked, and when, is on the record beside what arrives.

**The 31 copies of 2014 the request names** are the `.xls` files in the
tec-history journal (`data/raw/neso/tec-history/journal.ndjson`) that
`tec_register.read_vintage` cannot open (xlrd raises on their layout;
014's `SERIES.md` lists them as "not parsed"). The etrmbiz plan of
30/09/2026 says 24; a read of every `.xls` in the journal on 30/09/2026
finds 31 failing and 9 opening, of 40. The 31 are named below; the list is
from the journal, not from memory.

---

**To:** InformationRights@neso.energy  
**Subject:** RE: EIR request — archived TEC Register copies, 23 July 2025 to 18 May 2026 (Ref: FOI/26/216) — two additional items

Dear Information Rights team,

Thank you for your acknowledgement of 16 September (Ref: FOI/26/216). I
would like to add two items to that request. Both concern copies of the
TEC Register that NESO already holds in its archive (FOI/25/036;
FOI-24-0031), so I hope they can be answered within the same response. If
treating them as part of FOI/26/216 would delay the response due on 13
October, please answer the original items on time and log these two as a
new request.

4. **Every weekly (or twice-weekly) archived copy of the TEC Register
   dated between 1 January 2025 and the date of this request**, in the form
   held (xlsx or csv, one file per publication date). I understand NESO
   has released weekly copies for part of this period to at least one
   other requester in 2026; where a copy has already been disclosed, a
   pointer to the published response satisfies this item for that copy.
   Your response to FOI/26/175 (16 September 2026) states that the
   register "is published twice weekly", so the archive should hold
   roughly a hundred copies a year; the disclosures to date give me four
   copies for 2025 and two for 2026 after the 19 May extract. Item 1 of my
   original request (23 July 2025 to 18 May 2026) is contained in this
   item and is not withdrawn.

5. **CSV (or xlsx) renderings of the following 31 archived copies from
   2014**, which NESO disclosed under FOI-24-0031 as `.xls` files that
   current spreadsheet readers cannot open (the file structure is
   rejected as malformed by the open-source readers, and the copies are
   therefore unusable as disclosed). The copies are those dated:
   24 February; 28 February; 4, 11, 20, 25 and 28 March; 1, 8, 10, 17, 23,
   25 and 30 April; 13, 20 and 27 June; 11, 18 and 25 July; 1, 11, 15, 22
   and 29 August; 5, 12, 19 and 26 September; 17 and 24 October 2014. Any
   re-export from the original file to csv or xlsx would satisfy this
   item; no new information is sought.

Personal-data redactions as applied to the earlier disclosures are fine.
Electronic delivery preferred.

Yours faithfully,
Jordan Dimov, A115 Ltd, jdimov@a115.co.uk

---

## Notes for the sponsor

- **Why 1 January 2025 and not 23 July 2025.** The archive holds eight
  January 2025 copies, one for 21 March, one for 1 April, one for 1 July
  and one for 22 July 2025. If NESO's archive is twice weekly, February to
  July 2025 is as thin as the gap the original request names. Asking for
  the whole of 2025 to date in one item is cheaper than a third request.
- **The weekly files another requester obtained.** The etrmbiz note says a
  practitioner obtained weekly 2025-26 files; I did not find the
  disclosure on NESO's log (the log's search interface did not render on
  30/09/2026, and the 2026 responses I could read, FOI/26/141, /154, /173
  and /175, are other questions). The text above therefore asks for the
  copies without citing a reference, and offers NESO the pointer route.
  If you have the reference, add it to item 4.
- **On the fallback reader.** The plan also suggests parsing the 31 xls
  copies with a different reader. That is a code task outside this
  request and outside items A to E; LibreOffice's headless converter is
  the obvious candidate, and its output would be a derived rendering, not
  a disclosed copy, so it would carry its own provenance note.
- **What arrives enters the journal** as new rows with source `neso-foi`
  and is recomputed under 014's declaration; copies inside 014's regime
  break cannot change an old-regime row.
