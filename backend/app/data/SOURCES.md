# Data sources

Every figure used by verification checks is listed here. Re-check live official pages before relying on a number in counselling.

## Licensed recruiting agencies

- Source: BMET Recruiting Agents' Information System (RAIMS) via the Overseas Employment Platform.
- URLs: https://www.oep.gov.bd/agencies and https://raims.oep.gov.bd/agencies
- Retrieved: 24 Nov 2026
- Coverage: public snapshot stored in `licensed_agencies.json`. The live list is longer; a licence number that is **not** in this snapshot is reported as **unverifiable**, not as unlicensed.
- Status values used: Active, Expired, Cancelled — copied from the public table.

## Recruitment fee caps

- Legal basis: Overseas Employment and Migrants Act 2013, section 21 (government may set a maximum migration cost). https://bdlaws.minlaw.gov.bd/act-1131/section-43288.html
- Country table: BMET 2017 ceilings as reproduced by IOM, *Mapping of Recruitment Practices in Bangladesh* (2020), Table 2; also published by Bangladesh Bank Research Department (January 2019).
- URL: https://bangladesh.iom.int/sites/g/files/tmzbdl1006/files/documents/report-mapping-of-recruitment-practices-in-bangladesh_iom_jan-2020.pdf
- Retrieved: 24 Nov 2026
- Caveat: a later destination-specific programme can set a different approved amount. Unknown destinations are unverifiable.

## Salary benchmarks

- Qatar minimum wage: Law No. 17 of 2020 / ILO public summary.
- Other destination ranges: indicative public screening bands only, labelled as such in `salary_benchmarks.json`.
- FX table: rounded approximations for comparison, not a bank rate.
- Unmatched destination or role: unverifiable.

## Helplines

- BMET website https://bmet.gov.bd/ retrieved 24 Nov 2026: Probashbandhu 16135; from abroad +88 09610 102 030; BMET 02-49357972; 333; 999.
- Bangladesh Police - Hot Line Numbers: https://police.gov.bd (999, 109, 333).
- Ministry of Expatriates' Welfare and Overseas Employment: +880-2-41030444 (https://probashi.gov.bd).

## Knowledge Base & International Standards

- ILO Labour Migration: https://www.ilo.org/topics-and-sectors/labour-migration
- ILO International Labour Standards and Labour Migration: https://www.ilo.org/topics-and-sectors/labour-migration/international-labour-standards-and-labour-migration
- ILO Fair Recruitment: https://www.ilo.org/topics-and-sectors/fair-recruitment
- ILO Forced Labour, Modern Slavery and Trafficking in Persons: https://www.ilo.org/topics-and-sectors/forced-labour-modern-slavery-and-trafficking-persons
