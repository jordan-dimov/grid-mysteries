# O4 — written question to ESO EAD (draft, to be sent by the sponsor)

Declared in `KILL-DECLARATION.md` as the fourth forcing observation. Sending it
is a human action; this file only fixes the wording so the question asked is
the one declared, and adds one clarification the O2 instrument needs.

**To:** ЕСО ЕАД, дирекция „Присъединяване“ / пресцентър  
**Subject (BG):** Запитване по данни за присъединяване на центрове за данни  
**Subject (EN):** Data request — data-centre connection opinions and their outcomes

---

Уважаеми колеги,

A115 Ltd провежда публично документирано изследване („Grid Mysteries“) на
процеса по присъединяване на големи потребители към преносната мрежа.
Позоваваме се на данните, предоставени от ЕСО на Economic.bg (12.08.2026):
9 330 MW заявления и инвестиционни намерения за центрове за данни към
03.08.2026 г., от които 5 535 MW намерения, а останалите — с издадени
становища.

Бихме били благодарни за следната агрегирана информация по тримесечия,
считано от 01.01.2025 г., без идентифициране на отделни заявители:

1. брой и обща мощност (MW) на издадените становища за обекти „център за
   данни“;
2. брой и мощност на становищата, чийто едногодишен срок е изтекъл, без да е
   поискан предварителен договор;
3. брой и мощност на становищата, преминали в предварителен договор, и
   съответно в договор за присъединяване;
4. разпределение по мрежов район (МЕР) или по ниво на напрежение.

Отделно, във връзка с публичната „ESO Map“ (webapps.eso.bg/joining/public/map):

5. потвърждение, че „Оставащ капацитет за присъединяване“ се изчислява като
   общ капацитет минус сумата на редовете за резервиран капацитет, и на кой
   етап (становище / предварителен договор / договор) един обект започва да се
   включва в резервирания капацитет;
6. значението на полетата `opinion`, `pd` и `contract` във всеки ред
   (брой обекти или MW);
7. дали данните от картата могат да се използват повторно за изследователски
   и публикационни цели с позоваване на ЕСО, и дали се съхраняват исторически
   състояния.

Резултатите ще бъдат публикувани в агрегиран вид; ще предоставим проекта на
публикацията на ЕСО преди публикуването.

С уважение,  
[име, длъжност], A115 Ltd, [адрес, e-mail, телефон]

---

*English summary of the seven items for the record:* (1) count and MW of
data-centre opinions issued per quarter since 2025-01-01; (2) count and MW
lapsed at the one-year mark without a preliminary-contract request; (3) count
and MW converted to preliminary contract and to connection contract; (4) split
by grid region or voltage level; (5) confirmation that "remaining" = total −
Σ reserved rows and at which stage an object enters the reserved rows; (6)
meaning of the `opinion` / `pd` / `contract` sub-fields (object counts or MW);
(7) re-use terms for the map data and whether historical states are kept.

**Reading rule, fixed now:** items 2–3 are the direct measurement of S2
(lapse vs conversion). Refusal or silence is recorded as "eligible,
unpublished" (L7), not as evidence either way.

**Verified before sending (2026-08-26, one 400 kV record, four voltage
levels):** "remaining" = total − Σ reserved rows holds exactly; on the one row
with populated sub-fields, `opinion + pd + contract ≠ powerMw`, so item 6 is a
genuine unknown.
