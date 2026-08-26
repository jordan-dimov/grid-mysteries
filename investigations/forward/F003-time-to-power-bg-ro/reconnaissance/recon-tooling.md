# Reconnaissance: open-source tooling and evidential legitimacy of a CGMES → AC load flow → N-1 load-injection screen for BG/RO

Date: 2026-08-25. Target: Python 3.14.

Labels used throughout: **[V]** = verified today (package metadata via PyPI JSON, official docs fetched, or run locally in a scratch venv on Python 3.14.4); **[V-doc]** = verified from an official document but not exercised; **[U]** = unverified / inferred / from secondary sources. Local experiments were run in throwaway venvs under the scratchpad; nothing was installed into the project.

---

## 0. Bottom line

1. **The tool chain is technically legitimate and runnable on Python 3.14 today, with pypowsybl as the spine.** pypowsybl 1.16.1 (MPL-2.0, cp314 wheels) imports CGMES 2.4.15 and 3.0 including operational limits (PATL/TATL), runs OpenLoadFlow AC, and runs an N-1 security analysis reporting per-contingency convergence status, branch flows, bus voltages and limit violations. I exercised exactly the pipeline step "+100 MW at a load bus → AC LF → N-1 on all branches" on the bundled CGMES MicroGrid BE model and it worked end-to-end. [V]
2. **The evidential problem is the model, not the tool.** No real ESO EAD or Transelectrica CGMES model is publicly downloadable. The only realistic route to a real CGMES model covering BG and RO is ENTSO-E's TYNDP 2020 "input grid dataset" (CGMES 2.4.15, EQ/TP/SSH/SV, 25 CE files + boundary), which is issued to institutions *on request* through the STUM portal, with "more advanced data" under NDA. Its specification says the model is a **bus-branch, 220 kV-and-above model**: 110 kV is *not* represented in detail, loads are aggregated at the closest EHV node, and step-up transformers are usually absent. [V-doc] So the pipeline's "110 kV candidate buses" step has no legitimate CGMES substrate for either country from that source.
3. **The two capacity-map publications by the TSOs themselves are the cheapest kill/benchmark.** Transelectrica publishes an interactive connection-capacity map (400/220 kV, per RET zone, 2021/2025/2030, generation ≥5 MW) [V-doc via press]; ESO publishes a "free connection capacity" map for producers and consumers at webapps.eso.bg/joining/public/map [V: page exists, is a React/Azure-Maps app; content not read]. Any home-made screen must be positioned relative to these, and would in most respects be a weaker version of them.
4. **Dispatch uncertainty dominates any ranking.** A single solved SV state (or one TYNDP NT2025 snapshot) is one dispatch. A ranking of injection sites is only defensible as *conditional on the scenario set*, published with the scenario set, and only for the equipment classes whose limits are in the model.
5. **Effort for a minimal prototype, assuming a CGMES model in hand: ~8–15 engineering days** (details in §6). The dominant risks are (a) not obtaining a model, (b) model access terms forbidding publication of derived per-substation results, (c) missing 110 kV, (d) absent/partial limits producing silent non-detections.

---

## 1. pypowsybl (powsybl-core / OpenLoadFlow)

### Package facts [V, PyPI JSON 2026-08-25]
- Version 1.16.1, uploaded 2026-07-22; `requires_python >=3.10`; wheels cp310–**cp314**; licence **MPL-2.0**. GitHub `powsybl/pypowsybl` (pushed 2026-08-24, MPL-2.0), `powsybl/powsybl-core` (pushed 2026-08-25, MPL-2.0). Installed cleanly in a Python 3.14.4 venv via `uv pip install pypowsybl`. (Warning printed: `'opf' extra dependencies are not installed`; irrelevant here.)
- Architecture: Java (powsybl-core + OpenLoadFlow) compiled to a native library via GraalVM; no JVM install needed. [V-doc]

### Formats [V, queried at runtime]
- Import: `['BIIDM','CGMES','IEEE-CDF','JIIDM','MATPOWER','POWER-FACTORY','PSS/E','UCTE','XIIDM']`
- Export: `['AMPL','BIIDM','CGMES','JIIDM','MATPOWER','PSS/E','UCTE','XIIDM']`
- `pypowsybl.network.convert_from_pandapower` exists [V]; the reverse (pypowsybl → pandapower) does **not** exist — GitHub issue #895 "Convert pypowsybl network to pandapower" is open since 2024-11-18 with no PR [V-doc]. Route to pandapower/PyPSA is therefore via MATPOWER export (I exported MicroGrid BE to `.mat`, 1.4 kB [V]) → `pandapower.converter.from_mpc` → `pypsa.Network.import_from_pandapower_net` [U: not run], with the losses that implies (no limits in MATPOWER `rateA`? — actually MATPOWER carries rateA/B/C; whether powsybl writes PATL into rateA is [U]).

### CGMES import (powsybl-core docs, stable) [V-doc]
Source: https://powsybl.readthedocs.io/projects/powsybl-core/en/stable/grid_exchange_formats/cgmes/import.html
- Versions: **CIM16 / CGMES 2.4.15 and CIM100 / CGMES 3.0**, detected from `CimCharacteristics.cimVersion`.
- Profiles: EQ is the structural profile; SSH, TP, SV are "operational data". One EQ with multiple SSH is supported through `Network.read()` then `network.update()`. Missing SSH/SV fall back to EQ defaults (`P0/Q0` → 0, `TargetP` → `GeneratingUnit.initialP`, tap → `normalStep`); i.e. *an EQ-only import loads but is not a realistic operating point*.
- Boundary: `iidm.import.cgmes.boundary-location` (EQBD/TPBD directory; default `<ITOOLS_CONFIG_DIR>/CGMES/boundary`); `iidm.import.cgmes.convert-boundary` (default false). Lines ending at a boundary TopologicalNode become **BoundaryLines** (dangling lines with an equivalent injection) if the other side is absent, or **TieLines** when both IGMs are present. `cgm-with-subnetworks` (default true) splits a CGM into per-IGM subnetworks; `Network.merge` and `get_sub_networks` exist on the Python object [V].
- **Boundary files are mandatory when the EQ references boundary BaseVoltages**: reloading powsybl's *own* MicroGrid BE CGMES export without the EQ_BD/TP_BD files failed with `PyPowsyblError: nominalVoltage not found for BaseVoltage ...` [V]. A real IGM will always need the matching ENTSO-E boundary set (the TYNDP 2020 spec names "Boundary v1164" [V-doc]).
- Node-breaker vs bus-branch both supported; `import-node-breaker-as-bus-breaker` forces bus-breaker.
- Limits: `CurrentLimit`, `ActivePowerLimit`, `ApparentPowerLimit`; PATL → `permanentLimit`, TATL → `temporaryLimits` with `acceptableDuration`. Limits are imported **only** for lines, tie lines, 2- and 3-winding transformers and boundary lines. `iidm.import.cgmes.missing-permanent-limit-percentage` (default 100) synthesises a PATL from the lowest TATL when PATL is absent. Verified on MicroGrid BE: 56 limit rows, `permanent_limit` plus `CL-0` (20 min) and `CL-1` (10 min) TATLs on lines, 2WT, 3WT and boundary lines [V].
- Caveats listed in the doc: substations merged across transformer ends; only 2/3-winding transformers; reduced DC model by default; missing minQ/maxQ for EquivalentInjections marked TODO.
- Full import parameter list obtained at runtime (25 params, e.g. `...post-processors`, `...source-for-iidm-id`, `...create-fictitious-switches-for-disconnected-terminals-mode`, `...use-detailed-dc-model`) [V].

### AC load flow (OpenLoadFlow) [V]
- `pypowsybl.loadflow.run_ac(network, parameters)`. `Parameters` attributes: `balance_type, component_mode, connected_component_mode, countries_to_balance, dc, dc_power_factor, dc_use_transformer_ratio, distributed_slack, hvdc_ac_emulation, phase_shifter_regulation_on, read_slack_bus, shunt_compensator_voltage_control_on, transformer_voltage_control_on, twt_split_shunt_admittance, use_reactive_limits, voltage_init_mode, write_slack_bus, provider_parameters`. Provider parameters include `maxNewtonRaphsonIterations`, `lowImpedanceThreshold`, `reactiveLimitsMaxPqPvSwitch`, `voltageRemoteControl`, `newtonRaphsonStoppingCriteriaType`, `slack*` etc. (~60+ names).
- Result: per-component `ComponentResult` with `status` (CONVERGED / MAX_ITERATION_REACHED / FAILED …), `iteration_count`, `reference_bus_id`, `distributed_active_power`. (Note: attribute is `reference_bus_id`, not `slack_bus_id`.) MicroGrid BE: converged in 3 iterations; after +100 MW at load `cb459405…`, 5 iterations with 101.3 MW distributed to slack [V].

### Security analysis [V]
- `sa.create_analysis()`, `add_single_element_contingency`, `add_single_element_contingencies(ids)`, `add_multiple_elements_contingency`, `add_monitored_elements(branch_ids=…, voltage_level_ids=…)` (also pre-/post-contingency variants), operator strategies/remedial actions (`add_switch_action`, `add_generator_active_power_action`, tap actions, `add_operator_strategy`). `run_ac()` / `run_dc()`.
- Results: `pre_contingency_result.status`, `post_contingency_results[id].status` (`CONVERGED` / `FAILED` / `NO_IMPACT` …), `limit_violations` (columns `subject_name, limit_type, limit_name, limit, acceptable_duration, limit_reduction, value, side`), `branch_results` (p1,q1,i1,p2,q2,i2,flow_transfer per contingency), `bus_results` (v_mag, v_angle per contingency).
- MicroGrid BE run (+100 MW, N-1 over 2 lines + 3 2WT + 1 3WT): pre CONVERGED; 4 post CONVERGED, 2 transformer contingencies `FAILED` (islanding in a 6-VL toy grid); zero violations because flows stayed below PATL (e.g. 72 A vs 1443 A). [V]
- IEEE-300 (411 branch contingencies): **1.35 s total, 3.3 ms/contingency**, 378 CONVERGED / 33 MAX_ITERATION_REACHED, 155,290 branch-result rows, 113,521 bus-result rows. [V]
- **Missing limits are silent.** IEEE-300 and IEEE-14 have zero operational limits; the SA runs, returns flows, and reports **zero violations**. Nothing flags "unmonitorable because unlimited". A screen must therefore explicitly compute limit coverage per branch (`get_operational_limits()`) and treat unlimited branches as *unassessed*, never as *secure*. [V] Powsybl-core docs confirm violations are only "if the computed value is greater than the maximum allowed value" [V-doc].
- Limit reductions (e.g. 95 % of PATL) and `IncreasedViolationsParameters` (flow-proportional / voltage thresholds to filter pre-existing violations) exist [V-doc].
- OLF SA parameters: `contingencyPropagation` (node-breaker only), `contingencyActivePowerLossDistribution` (how lost injection is re-dispatched after a contingency, follows `BalanceType`), `dcFastMode` (Woodbury) [V-doc]. Non-convergence is reported as status, not raised.
- Performance reference (powsybl-benchmark, single core, i7-13700H): per-contingency AC SA 6.9 ms (RTE 1888 buses), 19.5 ms (RTE 6515 buses), 636 ms (ENTSO-E RealGrid v3.0.3) [V-doc]. So a ~10 k-bus model with a few thousand contingencies is minutes, not hours. Memory caveat: pypowsybl issue #922 (open, 2024-12) — pegase9241 with ~14 k monitored elements × ~14 k contingencies exhausted 300 GB because full branch/bus result tables are materialised; workaround is batching contingencies and monitoring only nearby elements [V-doc]. For the intended screen (N-1 on *nearby* branches, monitored set small) this is a non-issue.

### Maturity assessment
Actively maintained (commits this week), used by RTE and in ENTSO-E/CGMES interoperability contexts [U: usage claim from general knowledge]. It is the only Python-accessible stack in this list that treats CGMES as a first-class native format with a conformity-oriented importer *and* has TATL-aware security analysis. Weakness: GraalVM black box, large result tables, no pandapower export.

---

## 2. pandapower

### Package facts [V]
- 3.5.4 (2026-07-08), `requires_python >=3.10`, classifiers to **3.14**, BSD; imported and ran on 3.14.4 including `pandapower.converter.cim.from_cim`; `lightsim2grid` 0.13.1 has cp314 wheels and imported [V].

### cim2pp [V-doc + V experiment]
- Docs: https://pandapower.readthedocs.io/en/latest/converter/cgmes.html — "CIM CGMES 2.4.15 or 3.0", profiles `eq, eq_bd, ssh, sv, tp, tp_bd, dl, gl`; `from_cim(file_list, cgmes_version='2.4.15'|'3.0'|'LTDS', convert_line_to_switch, create_measurements, create_tap_controller, run_powerflow, ignore_errors, use_sv_data_for_assets, …)`. "Developed and tested on Python 3.11." Buses from TopologicalNodes (bus-branch) or ConnectivityNodes (node-breaker); `origin_id` retained; DC (DCLineSegment/Cs/VsConverter), SVC, all tap-changer classes, OperationalLimitSet/CurrentLimit/VoltageLimit listed as supported. No explicit limitations section; the mapping CurrentLimit → `max_i_ka` is not documented.
- Experiment (powsybl-generated CGMES 2.4.15 of MicroGrid BE, EQ/TP/SSH/SV, no boundary files): conversion succeeded in 0.5 s → 11 buses, 7 lines, 3 trafo, 1 trafo3w, 5 wards, `max_i_ka` populated from CurrentLimit (1.443, 1.180, … kA — the PATL values) and TATL columns preserved as `CurrentLimit.value_*` / `OperationalLimitType.acceptableDuration_*` on trafo3w. [V]
- **But `pp.runpp` failed** on the converted net with `FloatingPointError: invalid value encountered in divide` in `_wye_delta` (3-winding transformer star-conversion), for `trafo_model='pi'`, `trafo3w_losses='star'`, and even with the trafo3w set `in_service=False`; dropping the trafo3w removed the slack. Additionally **no `ext_grid` / slack is created** (`gen.slack` all False) for either the BE model or a CGMES export of IEEE-300; after designating a slack manually the IEEE-300 case did not converge under NR (init flat/dc/results, 60–100 iterations). Root cause not diagnosed (could be powsybl-export vs cim2pp interpretation mismatch, e.g. tap/ratio conventions); the point for feasibility is that the **pandapower path from a real CGMES set is not turnkey** — expect converter debugging days. [V, narrow: one synthetic CGMES source]
- Issue #2110 "Unable to convert ENTSO-E CIM data into pandapower" (`KeyError: None` in `convert_to_pp`) closed without documented resolution [V-doc]. The cim2pp paper (Fraunhofer IEE, ETG 2023, IEEE 10173005) validates on "two benchmark data sets including an ENTSO-E test network" [V-doc abstract]; deviations not accessible.

### Contingency tooling [V-doc]
- `pandapower.contingency.run_contingency(net, nminus1_cases)` (lines, trafo, trafo3w), `run_contingency_ls2g` (lightsim2grid; no trafo3w; flows valid only at from/hv side; requires contiguous bus index; differs when contingency islands the grid), `get_element_limits`, `report_contingency_results`. Outputs max/min loading %, max/min vm_pu per element over all cases, and which contingency caused the max. Non-convergence handling is coarser than powsybl (NaN rows) [U].
- Performance on ~10 k buses: no published number found; lightsim2grid fast path is the practical route (it is the engine Grid2Op uses on ~10 k-bus grids) [U]. Loading % on branches with NaN `max_i_ka` is NaN → same silent-gap risk as powsybl.

---

## 3. PyPSA and PyPSA-Eur

### PyPSA [V]
- 1.3.0 (2026-08-19), MIT, `>=3.11`, classifiers to 3.14; installed 1.2.4 in the scratch venv (resolver choice) and imported on 3.14.4.
- **No CGMES importer.** Only `import_from_pandapower_net()`; docs: "Not all pandapower data fields are supported. For instance, three-winding transformers, switches, `in_service` status and tap positions of transformers." [V-doc] The openmod thread (2023–24) confirms people write bespoke CGMES→PyPSA code because ENTSO-E BZR data used the standard "inconsistently" [V-doc].
- PyPSA does have a full Newton–Raphson AC power flow `n.pf()` with distributed slack, PV/PQ buses, tap ratios [V-doc], but **no contingency/N-1 framework, no TATL concept, no limit-violation reporting**; `s_nom` is an optimisation bound, not a monitored thermal rating. LOPF/linear optimisation is the wrong tool for AC/N-1 screening (linear DC, no voltage, no reactive power). PyPSA is appropriate only as the *scenario generator* (dispatch under future assumptions), feeding set-points into pypowsybl. That is a legitimate and arguably natural split.

### PyPSA-Eur OSM base network as an alternative substrate [V from the Zenodo files]
- Dataset: "Prebuilt Electricity Network for PyPSA-Eur based on OpenStreetMap Data", Zenodo 10.5281/zenodo.14144752, version 0.6; files `buses.csv, lines.csv, transformers.csv, links.csv, converters.csv`. Method paper: Xiong, Fioriti, Neumann, Riepin, Brown, "Modelling the high-voltage grid using open data for Europe and beyond", arXiv:2408.17178. Covers **≥ 200 kV only** ("220 kV to 750 kV" in the PyPSA-Eur doc); substations within 500 m merged; transformers between voltage levels at one site created synthetically; line `s_nom` from voltage × pandapower standard line type × circuits (e.g. `Al/St 240/40 4-bundle 380.0`, `Al/St 240/40 2-bundle 220.0`); validation vs ENTSO-E inventory at country level (ρ≈0.96 route length, ≈0.998 circuit length). Authors explicitly say detailed N-1 / precise power-flow use "requires further validation and testing" and that "only TSOs have access to the real grid data" [V-doc, WebFetch summary of paper].
- Counts I computed from v0.6 [V]:
  - **BG**: 113 buses (62 × 400 kV, 51 × 220 kV); 165 lines touching BG (92 × 400 kV, 73 × 220 kV; 124 single-, 41 double-circuit; 5,172 route-km); 12 transformers with synthetic `s_nom` ∈ {3575, 5363, 7150, 8938, 10725} MVA; 0 DC links. Median `s_nom`: 220 kV 492 MVA, 400 kV 1,787 MVA — **one generic type per voltage level, i.e. no real ratings**.
  - **RO**: 165 buses (101 × 220, 63 × 400, 1 × 750); 203 lines (113 × 220, 89 × 400, 1 × 750; 8,539 route-km); 22 transformers (synthetic s_nom 1788–8938 MVA); 0 DC links.
  - Cross-check: Transelectrica's own 2018 figures are 4,915 km 400 kV + 3,876 km 220 kV + 3 km 750 kV ≈ 8,794 km [V-doc, CIGRE 2018 national profile]; OSM gives 8,539 route-km — plausible at country level.
- What it lacks for this purpose: no 110 kV at all; no real line/transformer ratings (uniform assumptions); no load per bus or generator dispatch (PyPSA-Eur adds these by disaggregating national statistics with population/GDP keys, not metered substation loads); no switching topology; no tap data; no reactive equipment (shunts/reactors — ESO is installing 30–80 MVAr 110 kV shunt reactors [V-doc press]); transformer count (12 for BG) is far below reality (ESO: 297 substations, 32 "system" substations >15 GVA total transformation [V-doc ESO site]). It is a **topological** model good for aggregated planning, not an electrical model for connection screening.

---

## 4. Other tools

| Tool | CGMES | AC PF / N-1 | Python 3.14 | Licence | Assessment |
|---|---|---|---|---|---|
| **GridCal / VeraGrid** (SanPen, eRoots) | Import/export CGMES 2.4.15 and 3.0 (README) [V-doc]; demonstrated CGMES v3 in an ENTSO-E interoperability report (Oct 2024) [U, from search snippet] | NR, HELM, etc.; contingency analysis via full PF and PTDF/LODF [V-doc] | PyPI `GridCalEngine` 5.4.1 (2026-02) and `VeraGrid` 6.5.6 list only classifier 3.10, `requires_python >=3.8`, no binary wheels; not tested [V metadata] | MPL-2.0 | Credible second opinion / cross-check engine; repo renamed to VeraGrid (pushed 2026-08-25, 590 stars). CGMES conformity status unverified. |
| **PowerModels.jl / PowerModelsSecurityConstrained.jl** | **No** — parsers are Matpower `.m`, PSS/E v33 `.raw`, JSON only [V-doc] | SCOPF (ARPA-E GOC style) — optimisation, heavier than screening | Julia | BSD | Would need powsybl → MATPOWER/PSS/E export; only worth it if SC-OPF (redispatch-aware capacity) is wanted later. |
| **CIMpy** (sogno-platform) | CGMES 2.4.15 RDF/XML ↔ Python objects; no power flow [V-doc] | none | PyPI 1.1.0 (2024-06), classifiers ≤3.11; repo last push 2025-03 [V] | Apache-2.0 | Useful only for inspecting/patching raw CGMES; not a pipeline component. |
| **cgmes2pgm_converter + power-grid-model** (SOPTIM / LF Energy) | CGMES 2.4 and 3.0 via a **SPARQL triplestore** (Fuseki) — not files; DC replaced by loads; "intentionally kept small… demonstration" [V-doc] | PGM: fast PF/state estimation; N-1 by batch updates [U] | PGM 1.13 `>=3.12` py3 wheel [V] | Apache-2.0 | Built for state estimation, not screening; too much plumbing. |
| **OpenDSS** | no | distribution | — | — | Irrelevant. |
| **MATPOWER conversions** | via powsybl `MATPOWER` export [V]; pandapower `from_mpc`/`to_mpc` [V-doc] | — | — | — | Fine as an interchange for topology/impedances; TATLs, tap tables and node-breaker detail are lost [U on rateA mapping]. |

Conclusion: nothing displaces pypowsybl for the CGMES→AC→N-1 core; GridCal/VeraGrid is the best independent cross-check if the project wants a second solver on the same CGMES files.

---

## 5. Evidential assessment

### 5.1 What a CGMES model actually carries
Facts from the ENTSO-E TYNDP 2020 dataset specification (v0.01, March 2021) [V-doc, text-extracted]:
- Format CGMES 2.4.15; "All TSOs have provided the CGMES profiles EQ, TP, SSH, SV. So, a solved model is provided." Boundary v1164. Continental Europe model: 18,881 lines, 270 AC tie-lines; 95,425 CurrentLimit and 33,020 VoltageLimit objects over the CE IGMs; class table includes `OperationalLimitSet/Type`, `RatioTapChanger`, `PhaseTapChanger*`, `ConformLoad`, `SynchronousMachine`, generating-unit types, `ControlArea`.
- "The models submitted for 2025 Refgrid are aggregated bus branch models with the generation and load connected to the nearest High Voltage node." "All elements connected at 220 kV and above are modelled explicitly. Representation of the non-radial 150 kV, 132 kV and 110 kV shall be represented at the 220-kV level. Branches and substations of the network under the 220-kV voltage level shall not be represented in detail. Loads shall be aggregated at the closest EHV node… Embedded generation shall be represented as generation connected to the next EHV-HV node." "The step-up transformers are not usually represented." Substations "usually represented as one busbar per substation". HVDC as equivalent injections. Reactive limits "only Qmin, Qmax as a function of rated P". Thermal ratings of AC lines: required (ticked).
- Bulgaria and Romania are in the CE balance tables (BG: 10,986 MW installed, 6,018 MW generated, 5,292 MW load, +610 MW export; RO: 20,392 / 9,928 / 8,282 / +1,474) and in the violation table (BG 0/0/0). Oddity: the per-TSO CGMES class-count table as text-extracted lists 24 columns (AL…SK, incl. RO) **without a BG column**, while the portal says "25 CGMES files" for CE. Whether BG is a separate IGM or was folded into another column in extraction is [U]; must be checked on the actual dataset.
- Access: ENTSO-E "on-line application portal for network datasets" — datasets "available to institutions (universities, registered associations, companies, etc.) either as standard material upon simple request; or for more advanced data, upon request, with a specific description and signature of a Non-Disclosure-Agreement"; must "comply with legal provisions regarding grid safety, data publication limitations in all countries and confidentiality of third party (connected customers)". TYNDP 2020 via https://www.entsoe.eu/stum/ (request form; organisational e-mail required); TYNDP 2016/2018 via networkdataset@entsoe.eu. [V-doc] Licence text for republication of derived results: **not found** [U] — this must be read before any publication of per-substation findings.
- TYNDP 2024 download page offers scenario data, "Line data including reference grid", "List of nodes" — **no CGMES/nodal model** [V-doc]. TYNDP 2020 scenario page: scenario data only (CC-BY 4.0) [V-doc].
- ENTSO-E BZR/LMP study (2022): CE+IE nodal model of ~25,000 nodes (3,747 ≥380 kV; 7,639 at 111–220 kV; 13,847 ≤110 kV), 22,000 lines, 25,000 CNECs (BG 243, RO 269 N-1 CNECs requested below 380 kV), built on the TYNDP 2020 CGM + TSO data; "380/220 kV grid… extensively modelled". Publication: LMP results, flows, constraints/shadow prices and "Input Files.zip" are direct downloads; the "Network grid model used for LMP study" is listed as published but has **no direct link** — obtain via STUM request; Nordic grid data explicitly confidential. [V-doc] This is the second candidate source, and the ≤110 kV node count suggests BG/RO 110 kV *might* be present there — [U], to be verified by request.
- Operational (D-2/intraday) IGMs/CGMs exchanged under the CGM methodology are not public [U, no public source found; consistent with the confidentiality language above].
- Public CGMES test sets: ENTSO-E conformity models (MicroGrid, MiniGrid, SmallGrid, RealGrid — synthetic/anonymised), QoCDC test models, CommonData v2, ReliCapGrid ("Nine Realms", CC-BY-SA-4.0, EQ/SSH/SV/TP + NC profiles incl. Contingency/AssessedElement) [V-doc]. Good for building and testing the pipeline; zero evidential value for BG/RO.

### 5.2 What conversion typically loses
- pypowsybl keeps: limits (PATL/TATL), tap changers, node-breaker topology, boundary/tie-line semantics, control areas, SV state (as initial values) [V]. Loses/flattens: 3-winding transformer per-winding details are re-modelled, EquivalentInjection Q limits (TODO), detailed DC unless enabled.
- pandapower keeps PATL as `max_i_ka` and TATLs as extra columns, but loses powsybl-style violation semantics; slack is not set; 3WT handling fragile [V].
- PyPSA loses 3WT, switches, in_service, tap positions [V-doc] — and all limit semantics beyond `s_nom`.
- MATPOWER/PSS-E loses TATL, tap tables, node-breaker, boundary semantics [U on specifics].

### 5.3 Is N-1 on a partial model meaningful?
- On a 220 kV-and-above bus-branch model: N-1 of 400/220 kV lines and 400/220 transformers is meaningful **for those elements**, with two structural caveats: (i) lost 110 kV parallel paths — non-radial 110 kV is represented only as an equivalent at 220 kV, so post-contingency redistribution through the 110 kV mesh is either missing or approximated by the equivalent; (ii) the 400/110 and 220/110 transformer level — the most common binding constraint for a 50–150 MW connection at a 110 kV substation — is exactly what the model aggregates away. The screen can say something about *transmission-level headroom near an EHV node*, nothing about *the 110 kV substation itself*.
- Limit coverage: pypowsybl silently ignores unlimited branches. The screen must publish, per candidate, the share of nearby branches with PATL (and TATL) defined; conclusions apply only within that set.
- Merged vs. single IGM: a BG IGM alone with boundary injections fixes interconnector flows at the SSH values; contingencies on tie-lines and loop-flow effects through RO/RS/GR/MK/TR need the merged CGM (the TYNDP dataset is delivered as an assembled CE model, so this is available) [V-doc].

### 5.4 Dispatch uncertainty and site ranking
- A CGMES SV is one operating point (TYNDP 2020: NT2025 market-simulation snapshot, one hour). Thermal headroom at a node is a function of the full injection vector; for the BG/RO region the dominant drivers are Maritsa-East thermal dispatch, Kozloduy, Danube/Iron Gates hydro, Dobrudzha/Dobrogea wind, southern PV, and net export to GR/TR/RS/MK (BG exported 610 MW in the snapshot; RO 1,474 MW) [V-doc figures; drivers U]. Changing these plausibly re-orders sites: a site that is "fine" under high-export summer PV may be the first to bind under winter peak with low wind, and vice-versa.
- Defensible design: define a small, pre-declared scenario set (e.g. 4–8 dispatch cases spanning season × RES × export direction), run the identical screen for each, and report **rank stability** (how often a site is in the top-k, worst-case headroom, first binding element and its class). A single-snapshot ranking is not publishable as a ranking; it is publishable as "in snapshot X, adding 100 MW at node Y first violates element Z under contingency C".
- Voltage: 110 kV reactive support (ESO's planned 30–80 MVAr reactors) is exactly the equipment the EHV model omits; voltage conclusions at 110 kV are therefore unsupported.

### 5.5 Is 110 kV in a TSO CGMES model for BG/RO, and what does that imply?
- **Bulgaria**: ESO EAD owns and operates 110 kV as part of the transmission grid — 15,384 km of HV lines, of which ~65 % 110 kV, 18 % 220 kV, 17 % 400 kV; 297 substations, 261 of them stepping down to MV [V-doc bg.wikipedia, 2022 figures; primary ESO annual report not fetched → treat the split as U]. ESO's TYNDP 2025–2034 is dominated by 110 kV/MV substation and transformer upgrades and new 400/110 kV substations (Svoboda, General Toshevo 2, Dobrich 2, Pleven 3) [V-doc press summaries]. So ESO *has* a full 110 kV model internally, but the ENTSO-E planning IGM it submits is 220 kV+ by specification; whether ESO's operational IGM includes 110 kV is [U].
- **Romania**: Transelectrica operates 750/400/220 kV; 110 kV is DSO (2018 CIGRE profile: TSO 400 kV 4,915 km, 220 kV 3,876 km, 750 kV 3 km, 110 kV only 40 km; DSO ≤110 kV 337,500 km) [V-doc]. DSO dispatch centres manage the 110 kV network [V-doc, search snippet from Transelectrica page]. A Transelectrica CGMES model will not carry the DSO 110 kV network except as equivalents; 110 kV candidate buses in RO are simply not the TSO's connection points — 50–150 MW loads in RO connect at 110 kV to a DSO (Electrica/E-Distribuție/Delgaz/etc.) whose models are not public at all.
- Implication: "candidate 110 kV buses" is only modellable for BG, and even there only if a 110 kV-inclusive model is obtained (not the TYNDP dataset). For RO the legitimate candidates are 400/220 kV substations (which is also the level of Transelectrica's own capacity map).

### 5.6 What the output can and cannot say
Can say (given a solved, limit-bearing 220 kV+ model and a declared scenario set):
- For each candidate EHV node and each scenario: whether +50/+100/+150 MW converges, the first binding element and limit type (PATL vs which TATL), post-contingency worst loading and lowest voltage among *monitored, limited* elements, and the contingencies that fail to converge.
- A relative ordering of EHV nodes **within the scenario set**, with its stability across scenarios, and the limit-coverage caveat per node.
- Falsifiable statements of the form "in model M (digest…), scenario S, adding 100 MW at node N causes element E to exceed its PATL under contingency C" — precisely the kind of narrow claim the project doctrine wants.

Cannot say:
- Anything about available connection capacity at a specific 110 kV substation (transformer rating, 110 kV mesh, reactive support) — in RO structurally, in BG absent a 110 kV model.
- "Capacity is available" — the TSO's connection process includes queued requests (Transelectrica's map explicitly nets off "existing connection requests in various stages of processing" [V-doc]), planned outages, dynamic/seasonal ratings, short-circuit and stability checks, and the TSO's internal N-1 policy (which elements, which TATL durations, remedial actions), none of which the public model reproduces.
- Anything dated later than the model vintage: a TYNDP 2020 NT2025 snapshot is a 2020-vintage view of 2025; it excludes projects and contains assumed ones. Comparison to ESO/Transelectrica capacity maps (2025/2030) is therefore only indicative.
- Savings/costs or "best site" in an economic sense.

The intellectually honest framing is: *an independent, reproducible reconstruction of transmission-level headroom near EHV nodes, published with its model digest, scenario set, limit coverage and falsifiers — to be compared against the TSOs' published capacity maps*, not a substitute for them.

---

## 6. Effort estimate and risks

Assumptions: a CGMES model (TYNDP 2020 CE or LMP-study grid model) with boundary set is obtained; pypowsybl as the engine; PyPSA only if scenario generation is wanted.

| Step | Days | Notes |
|---|---|---|
| Model acquisition (STUM request, terms review, digest + provenance record) | 1–2 active (+ weeks of waiting) | Read licence; decide what can be published (per-node results vs aggregates). |
| CGMES import, boundary configuration, sanity checks (islands, limit coverage, comparison of SV vs re-solved LF) | 2–3 | Expect boundary/ID quirks; verify BG IGM presence. |
| Candidate selection (EHV nodes in BG/RO from `get_voltage_levels`/`get_substations`, geo-tagging if GL profile present) | 1 | |
| Injection + AC LF + N-1 on nearby branches (k-hop neighbourhood), metrics extraction, limit-coverage accounting | 2–3 | Batching to keep result tables small. |
| Scenario set (manual re-dispatch of SSH set-points: seasonal load scaling, RES, export) | 2–4 | PyPSA-driven dispatch adds 3–5 more days; probably not for a prototype. |
| Tests on ENTSO-E conformity models / ReliCapGrid, fixtures, rendering, write-up | 2–3 | |
| **Total** | **~10–16 days** (minimal: ~8) | |

Main risks, in order of probability × impact:
1. **No model, or model with unpublishable terms** — kills the CGMES track outright; fallback is the OSM/PyPSA-Eur topology, which cannot support the claims in §5.6 at all (uniform ratings, no loads).
2. **110 kV absent** — the pipeline as specified ("110 kV buses") is not achievable from any obtainable CGMES for RO and almost certainly not for BG; scope must be restated to 400/220 kV nodes before data is touched (pre-declaration discipline).
3. **Limit sparsity / silent non-detection** — must be measured and published; otherwise "no violation" is meaningless.
4. **Snapshot dependence** — a single-SV ranking will be falsified by the first different dispatch; scenario set must be pre-declared.
5. **Tool fragility outside pypowsybl** — cim2pp needed manual slack and failed on a 3WT in my test; PyPSA import drops 3WT/switches/taps. Keep pandapower/PyPSA out of the evidential path; use them (or VeraGrid) only as cross-checks.
6. **Memory** on full-CGM N-1 with full monitoring (issue #922) — mitigated by neighbourhood monitoring and batching.
7. **Model vintage** — TYNDP 2020 is a 2020 view; the 2025/2030 TSO capacity maps and ESO's 2025–2034 plan already differ; every result must be time-stamped to the model, not to today.

Cheapest kill before building anything: (a) request the TYNDP 2020 CE dataset and confirm on receipt that a BG IGM exists and which voltage levels it contains; (b) read the ESO and Transelectrica capacity maps and decide whether a reconstruction can add anything beyond reproducibility of their claims.

---

## Sources (fetched/used)
- pypowsybl PyPI JSON: https://pypi.org/pypi/pypowsybl/json ; GitHub https://github.com/powsybl/pypowsybl ; issue #895 https://github.com/powsybl/pypowsybl/issues/895 ; issue #922 https://github.com/powsybl/pypowsybl/issues/922
- powsybl-core CGMES import: https://powsybl.readthedocs.io/projects/powsybl-core/en/stable/grid_exchange_formats/cgmes/import.html ; security analysis: https://powsybl.readthedocs.io/projects/powsybl-core/en/latest/simulation/security/index.html ; OLF SA parameters: https://powsybl.readthedocs.io/projects/powsybl-open-loadflow/en/latest/security/parameters.html ; benchmarks: https://github.com/powsybl/powsybl-benchmark
- pypowsybl user guide (network / loadflow / security): https://powsybl.readthedocs.io/projects/pypowsybl/en/stable/user_guide/
- pandapower PyPI JSON; cim2pp docs https://pandapower.readthedocs.io/en/latest/converter/cgmes.html ; contingency docs https://pandapower.readthedocs.io/en/latest/contingency.html ; issue #2110 https://github.com/e2nIEE/pandapower/issues/2110 ; cim2pp paper https://ieeexplore.ieee.org/document/10173005
- PyPSA docs: https://docs.pypsa.org/stable/user-guide/import-export/ , https://docs.pypsa.org/stable/user-guide/power-flow/ ; openmod thread https://forum.openmod.org/t/pypsa-and-the-cim-cgmes-does-it-make-sense-to-go-down-this-road/5033
- PyPSA-Eur base network: https://pypsa-eur.readthedocs.io/en/v2025.07.0/data-base-network.html ; Zenodo 10.5281/zenodo.14144752 (v0.6 files analysed locally); paper arXiv:2408.17178
- GridCal/VeraGrid: https://github.com/SanPen/GridCal (redirects to VeraGrid), PyPI GridCalEngine/VeraGrid JSON
- PowerModels parser: https://lanl-ansi.github.io/PowerModels.jl/stable/parser/
- CIMpy: https://github.com/sogno-platform/cimpy ; cgmes2pgm: https://github.com/SOPTIM/cgmes2pgm_converter
- ENTSO-E TYNDP 2020 dataset specification (PDF, text-extracted): https://eepublicdownloads.entsoe.eu/clean-documents/CIM_documents/Grid_Model_CIM/TYNDP_2020_ENTSO-E_dataset_specificationv01.pdf
- ENTSO-E network datasets portal: https://www.entsoe.eu/publications/statistics-and-data/ ; request form https://stum.entsoe.eu ; CGMES library https://www.entsoe.eu/data/cim/cim-for-grid-models-exchange/ ; ReliCapGrid https://github.com/entsoe-tso/relicapgrid/
- ENTSO-E BZR page https://www.entsoe.eu/network_codes/bzr/ ; LMP data news https://www.entsoe.eu/news/2022/09/06/entso-e-publishes-locational-marginal-pricing-data-items-as-part-of-bidding-zone-review-study/ ; LMP report PDF (text-extracted) https://eepublicdownloads.entsoe.eu/clean-documents/Publications/Market%20Committee%20publications/ENTSO-E%20LMP%20Report_publication.pdf
- TYNDP 2024 downloads https://2024.entsos-tyndp-scenarios.eu/download/ ; TYNDP 2020 downloads https://2020.entsos-tyndp-scenarios.eu/download-data/
- Romania: CIGRE 2018 national profile (PDF, text-extracted) https://www.cigre.org/userfiles/files/Community/NC/2018_National-power-system_Romania.pdf ; Transelectrica capacity map https://web.transelectrica.ro/harti_crd_tel/ and press https://www.energynomics.ro/en/transelectrica-has-launched-its-grid-connection-capacity-map/
- Bulgaria: ESO site https://www.eso.bg/?en= ; ESO connection map https://webapps.eso.bg/joining/public/map/ ; bg.wikipedia ESO article; TYNDP 2025–2034 summaries https://cms.law/en/bgr/legal-updates/bulgaria-s-electricity-system-expects-major-investments-for-400kv-and-110kv-networks-over-next-decade , https://ivlawfirm.com/en/highlights-from-the-transmission-network-development-plan/
