# K0 Buyer Reality — Batch 02 (C16, C17, C18, C19)
Date: 2026-08-26. WebSearch budget exhausted at start; all evidence via WebFetch/curl on publisher URLs.

## C16 MCPD / specified generator permitting
- [V] gov.uk "Medium combustion plant and specified generators: environmental permits" (last updated 22 Jul 2024): "You will need to apply for a MCP or specified generator environmental permit (or both) if the regulations apply." Operator is the applicant. Emission limits are permit conditions.
- [V] gov.uk publication "Environmental permitting charging scheme" — EA Charging Scheme 2022, amendments up to 15 May 2026. PDF: https://assets.publishing.service.gov.uk/media/6a05f03922977ebc82cb3fcb/...pdf — fee lines for specified generator/MCP permits NOT YET EXTRACTED.
- Deadline guidance page (specified-generators-when-you-need-a-permit) 404 — need alternative URL.

- [V] gov.uk "Specified generator: when you need a permit" (last updated 1 Sep 2022): Tranche A >5MWth permitting 1 Oct 2019 / compliance 1 Jan 2025; Tranche A 1–5MWth permitting & compliance 1 Jan 2030; Tranche B from 1 Jan 2019/commissioning. CAVEAT: emergency backup generators excluded from SG rules if used only in emergencies, "You must not carry out more than 50 hours testing a year for each backup generator."
- [V] gov.uk "Medium combustion plant: when you need a permit" (last updated 9 Jul 2025): new MCP from 20 Dec 2018; existing >5MWth apply by 1 Jan 2024 / comply 1 Jan 2025; existing 1–5MWth apply by 1 Jan 2029 / comply 1 Jan 2030. No backup-generator hours exemption (only antique plant <500h excluded). => standby fleets ≥1MWth are in MCP scope.
- [V] EA Charging Scheme 2022 amendments to 15 May 2026 (PDF): 1.10.2 "Medium combustion plant site – requires dispersion modelling" permit application £6,798.90; 1.10.3 "does not require dispersion modelling" £2,105.06; SR2018 No.1 SG Tranche B low risk £229.40; subsistence 2.10.7 "MCP and/or specified generator comprising 1 combustion plant or generator" £355.00/yr, 2.10.11 (9–10 plants) £539.76/yr.
- [V] gov.uk application form "part B2.5 bespoke MCP and SG permit" published 26 Feb 2026.
- VERDICT C16: Class C (dated statutory permit deadlines, operator is applicant) + Class A (regulator fees, recurring subsistence). PASS.

## C17 ICP contestable works
- LR NERS URLs all 404 so far. Contracts Finder HTML search regex returned 0 — retry.

- [V] SSEN competition-in-connections page (fetched 26 Aug 2026): "If you have the appropriate NERS accreditation and have been engaged by a client to deliver their new connections, we can provide you with the necessary non-contestable services." Accreditation via LRQA. ICP Application "for an extended electricity network you wish to connect to our network and us to adopt".
- [N] LR/LRQA NERS fee schedule — all URL guesses 404. [N] Contracts Finder search (HTML search not filterable via GET; OCDS API has no keyword param).
- [V] LinkedIn guest search "HV Authorised Person" UK (26 Aug 2026): Clancy "Senior Authorised Person - 33kv & 132kv" Basingstoke (29 Jul 2026); Climate17 "SAP (11-132kv)" Castleford (21 Aug 2026); M Group Energy SAP Stevenage (16 Aug 2026); OCU SAP Shinfield (5 Aug 2026); Freedom SAP (22 Aug 2026) — ICP/contractor employers hiring 33/132kV SAPs = Class B at ICPs.

## C18 Market facilitator asset registration
- [V] Ofgem decision "Elexon will be the market facilitator delivery body", 29 Jul 2024. Para 3.19: "We will however be placing licence obligations on DNOs and NESO to adopt the outputs specified by the market facilitator." Para 4.7 Phase 2: BSC modification for "ongoing governance, operation and funding"; Phase 3: Distribution Licence and ESO Licence changes.
- [V] Elexon news 1 Sep 2025: rules "will be backed by conditions which Ofgem will insert into the licenses of the NESO and DSOs to require compliance"; "BSC Parties will be required to fund market facilitator activity and in September 2025 a Modification will be raised"; "begin operations in December 2025".
- [V] Elexon governance page (fetched 26 Aug 2026): "NESO and DNOs are required to follow the Flexibility Market Rules through their licences, while Elexon's obligations are enforced through the BSC." Implementation Monitoring Procedure checks SO compliance.
- [V] Elexon FMAR page: "will be a single, central 'one-stop shop' through which aggregators register flexible assets"; "initially focus on smaller scale assets (under 1MW)"; "formally consulted on in September 2026". CAVEAT: register not live; today registration is per-SO.
- VERDICT C18: Class C (licence obligations on DNOs/NESO; BSC-funded Elexon function) — PASS; Class B for Elexon (BSC-party-funded programme, SAB oversees "delivery plans, budgets").

- [V] SSEN CiC Code of Practice page: "approved by Ofgem in June 2015" with "an implementation date of October 2015"; "governs the way in which DNOs provide input services to facilitate competition in the electricity connections distribution market".
- [V] LRQA NERS page (https://www.lrqa.com/en/utilities/national-electricity-registration-scheme-ners/): "technical assessment of the service providers who elect to be assessed for accreditation for contestable works"; operates "on behalf of the UK Distribution Network Operators (DNOs)". Fees [N].
- [V] Aureos SAP advert (LinkedIn, ~19 Aug 2026): "switching, isolation, earthing, PTW, SFT ... on SSEN and private networks ... up to 132kV"; "tender/bid support, and financial management (valuations, invoicing)".
- VERDICT C17: Class A (developer→ICP spend) established structurally via DNO + Ofgem-approved CoP (Oct 2015) + accreditation scheme; Class B strongly evidenced at ICPs (dated 33/132kV SAP hiring). No individual buyer contract notice retrieved [N]. PASS.

## C19 (cont.)
- [V] LinkedIn "Senior Authorised Person" UK (26 Aug 2026): QinetiQ SAP Amesbury (25 Aug 2026) — private-network owner hiring directly; Southern Water SAP Brighton (23 Aug 2026); EMCOR UK "Authorised Person Day Shift" Glasgow £40,000 (15 Aug 2026): "manage the day to day running of the Permit office ... issue work permits ... carry out Authorised person duties".
- [N] Data-centre-named HV AP job spec: Microsoft CE Technician (20 Aug 2026) mentions generators/CMMS but no HV AP/switching text; reed/totaljobs/cv-library searches returned no DC-specific AP advert.
- VERDICT C19: Class B (operators and FM/HV contractors employ APs/SAPs specifically for HV authorisation/switching on private networks; dated adverts) + Class C-lite (HTM 06-03 'should appoint', guidance). PASS; DC-specific owner not directly evidenced.
- [V] NHS England HTM 06-03 (21 May 2021, updated 11 Oct 2023) PDF: 4.34 "An Authorising Engineer (HV) should be appointed in writing by the Designated Person on behalf of the Management"; 4.35 appointed "for no longer than five years"; 4.54 Management "should appoint their own Authorised Person (HV)". Guidance status; applies to "all healthcare facilities containing a high voltage electrical system".
- Elexon pages found: /what-we-do/about-our-services/market-facilitator-for-distributed-flexibility/ ; 2025-09-01 "Elexon consults on market facilitator rules and governance arrangements"; 2025-10-22 consultations on flexibility market rules. Not yet fetched.

## C19 HV authorisation at private networks
- [V] reed.co.uk "95 HV Authorised Person Jobs" (26 Aug 2026): NG Bailey SAP Lancaster; Owen Daniels SAP HV Wrexham £55-65k (23 Jul); Rise Technical "HV SAP (33kV)" Manchester £60-70k (27 Jul). Sector of end-client not shown; data-centre-specific advert not yet found.
- HTM 06-03 URL 404 — need correct URL. Contracts Finder "Authorising Engineer" search: retry.
