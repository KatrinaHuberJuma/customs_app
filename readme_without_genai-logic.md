# NoGL.md — Engineering Analysis: `customs_appZ`

**Project**: customs_appZ (this project)  
**Reference (good impl)**: `customs_app`  
**Date**: February 26, 2026  
**Classification**: Candid retrospective — not marketing  
**Authored by**: Claude Sonnet 4.6, comparing two implementations built from the same prompt — one with GenAI-Logic Context Engineering loaded, one without

---

## TL;DR

This project was created from the customs prompt **without first loading `.github/.copilot-instructions.md`**. The AI had no awareness of GenAI-Logic architecture, the Request Pattern (ROP), or LogicBank declarative rules.

The result is a working application: the endpoint returns correct answers for its intended happy-path POST, the Admin UI runs, and the code is competent Flask. For a proof-of-concept with a single entry point, it would pass a demo. The problem is architectural, not functional — and it only surfaces under real-world conditions.

**One-line verdict**: Business logic lives in the wrong layer — in a fat API service — and is not enforced by the rules engine. `declare_logic.py` itself confirms this: `declare_logic_message = "ALERT:  *** No Rules Yet ***"`.

---

## Key Findings

1. **Zero declarative rules** — `declare_logic.py` still carries `"ALERT: *** No Rules Yet ***"`. The 13 `Rule.formula/sum/copy/constraint` declarations in `customs_app` have no counterpart here.

2. **~150 lines of business logic in the wrong layer** — `duty_calculator_service.py` performs tariff lookups, rate selection, and calculations. The `early_row_event` in `duty_calculations.py` then recalculates the same amounts from already-set fields — logic runs twice, in two places, neither governing the other.

3. **Missing requirements from the original prompt** — Provincial tax (HST/PST), surtax applicability by ship date (`>= 2025-12-26`), and multi-line order structure are all explicit in the prompt used for both projects; all are absent from this implementation. (Note: this comparison is only valid if both projects were built from the same prompt. The session transcript in `session_transcript.md` confirms this.)

4. **Enforcement gap** — Logic only fires via the one custom endpoint. Any insert via standard JSON:API, the Admin UI, test scripts, or future integrations bypasses tariff lookup entirely and stores whatever rates the caller provides.

5. **Schema design** — A flat single record per calculation vs. `customs_app`'s normalized `SurtaxOrder` / `SurtaxLineItem` / `ProvinceTaxRate` / `CountryOrigin` / `HSCodeRate` hierarchy.

---

## Demo vs. Enterprise-Class Architecture

**It is fair to call this a demo-class architecture. Here is why.**

The distinction is not about whether the code works for a happy-path POST — it does. The distinction is about what the architecture guarantees and what breaks under real-world conditions.

### What demo-class means here

**A demo-class implementation** is one where:
- The "business logic" is a procedure wired to a single entry point
- Correctness depends on every caller going through that one path
- Adding a new entry point (a second API, a test, an integration) requires manually duplicating or calling the logic
- The system has no shared enforcement layer — rules live in the service, not in the platform

This is exactly the structure here. The duty calculation logic is in `duty_calculator_service.py`. Nothing stops a caller from POSTing a `DutyCalculation` row directly via `/api/DutyCalculation` with a `duty_amount` of `0` and a `total_amount` of `0` — both will be stored as-is. The rules engine won't correct them because there are no rules.

**An enterprise-class implementation** is one where:
- Business logic is declared once, in a shared enforcement layer
- That layer fires on every transaction, regardless of entry point
- Adding a new entry point (API, test, admin, Kafka consumer) does not require porting logic
- Constraints, derivations, and validations are guaranteed to run at commit time

`customs_app` meets this bar. `customs_appZ` does not.

### The specific failure modes this creates

| Scenario | customs_appZ | customs_app |
|---|---|---|
| Admin UI user edits a `DutyCalculation` row | Amounts become stale/wrong — no rules re-fire | Rules re-derive all amounts automatically |
| Test data script inserts a row directly | Gets whatever values were hardcoded — no lookup | Rules derive correct amounts from reference data |
| A second API endpoint is added | Must re-implement or call the service explicitly | Inherits all rules automatically |
| Provincial tax requirement is added | Requires API code change + new endpoint logic | Add one `Rule.formula` in `cbsa_steel_surtax.py` |
| Auditor asks: "prove the calculation is always enforced" | Cannot — enforcement depends on one code path | Yes — LogicBank fires on every commit, traceable in logs |

### Why "demo" is the right word, not "wrong" or "broken"

This pattern is completely normal and acceptable for:
- A proof of concept where only one UI/API exists
- A throwaway script
- A system where the single endpoint is the only ever intended entry point

It becomes a liability when the system is expected to grow, handle multiple clients, be maintained by others, or be audited — which is precisely the use case CBSA customs compliance implies. Regulatory compliance systems are among the clearest cases where "logic enforced from one place, callable from anywhere" is not optional.

The GenAI-Logic platform was built specifically to address this. The failure here is not that the AI wrote bad code — the code is competent Flask. The failure is that the AI wrote Flask code onto a platform that provides something better, because it didn't know the platform existed.

---

## 1. Root Cause

The prompt was good. It contained all the signals for a rules-based, Request Pattern implementation:

| Signal in prompt | What it implies |
|---|---|
| "calculate duties and taxes" | Computed fields → `Rule.formula` |
| "when hs codes, country, value is given" | Request fields → ROP table |
| "provincial sales tax or HST where applicable" | Conditional tax → `Rule.formula` with lookup |
| "ship date >= 2025-12-26" | Conditional surtax applicability → `Rule.formula` |
| CBSA / Customs Tariff compliance domain | Audit trail requirement |

Without context from `.copilot-instructions.md`, the AI defaulted to the most familiar pattern: **build business logic inside the API endpoint**. This is correct for generic Flask development, but wrong for GenAI-Logic.

---

## 2. Logic Architecture: Where the Rules Live

### customs_appZ (this project) — Logic in API layer

```
api/api_discovery/duty_calculator_service.py   ← 179 lines  (logic IS here)
logic/logic_discovery/duty_calculations.py     ← early_row_event  (procedural, not declarative)
logic/declare_logic.py                         ← "ALERT: *** No Rules Yet ***"
```

**`duty_calculator_service.py`** performs:
1. Database lookups (HS code, origin country, destination country, tariff rate)
2. Business decisions (which tariff applies, rate selection)
3. Record creation with pre-computed rate values
4. `session.flush()` comment: "Trigger business logic calculations"
5. Response assembly with full breakdown

Then `duty_calculations.py` fires an `early_row_event` that **recalculates the same amounts** from the already-populated rate fields — redundant execution, with logic running twice in two different places, neither governing the other.

### customs_app (reference) — Logic in rules layer

```
api/api_discovery/     ← only boilerplate stubs (new_service.py etc.)
logic/logic_discovery/cbsa_steel_surtax.py   ← 13 declarative rules
logic/declare_logic.py                       ← routes to logic_discovery (correct)
```

`cbsa_steel_surtax.py` uses:
- `Rule.formula` — derives `customs_value`, `duty_amount`, `surtax_amount`, `pst_hst_amount`, `total_amount`, `surtax_applicable`
- `Rule.copy` — copies `duty_rate` and `surtax_rate` from `HSCodeRate` parent
- `Rule.sum` — rolls up 5 line-item fields to `SurtaxOrder` totals
- `Rule.constraint` — validates ship date, quantity, unit price

**Zero business logic in any API file.**

---

## 3. Declarative vs. Procedural Rule Count

| | customs_appZ | customs_app |
|---|---|---|
| Declarative `Rule.*` statements | **0** | **13** |
| Lines of procedural logic in API | **~150** (service body) | **0** |
| `early_row_event` (procedural) | 1 (recalculates what API already set) | 1 (surtax applicability, justified) |
| `Rule.sum` rollups | 0 | 5 |
| `Rule.copy` from parent | 0 | 2 |
| `Rule.constraint` validation | 0 | 3 |

The `early_row_event` in `duty_calculations.py` is not wrong in principle, but here it is redundant — the API already computed and stored `duty_amount`, `tax_amount`, and `total_amount` before the row was flushed. The event just overwrites the same values.

---

## 4. Schema Design

### customs_appZ

```
Country
HSCode
TariffRate          ← lookup: hs_code + origin_country + destination + date range
DutyCalculation     ← flat single-row record per calculation
Customer / Product / Order / Item   ← basic_demo tables (unrelated to customs)
```

Problems:
- **Flat single record** — no line item / order hierarchy. One calculation = one row.
- **No provincial tax table** — the prompt explicitly asked for "provincial sales tax or HST where applicable". This is completely absent from the schema and the code.
- **Rates copied into record by API** — `duty_rate` and `additional_tax` are set by the service from `TariffRate` lookup, not derived by rules from a parent relationship.
- **No `surtax_applicable` flag** — ship date cutoff logic from the prompt (`>= 2025-12-26`) is not modeled.
- **basic_demo tables are present** — `Customer`, `Product`, `Order`, `Item`, `ProductSupplier` are in the database from the base project and have no relationship to the customs functionality.

### customs_app

```
ProvinceTaxRate     ← lookup by province_code
CountryOrigin       ← includes surtax_applicable flag per country
HSCodeRate          ← base_duty_rate + surtax_rate per HS code
SurtaxOrder         ← header: ship_date, country, province, totals
SurtaxLineItem      ← line items: hs_code, qty, price → all amounts derived
```

Properly normalized. Rules propagate changes up and down automatically. Adding a line item recalculates the order totals. Changing a province code recalculates all PST/HST. None of this requires API changes.

---

## 5. Enforcement Scope: When Does Logic Fire?

This is the critical architectural difference.

**customs_appZ**: Logic fires only when a client POSTs to `/api/DutyCalculatorEndpoint/CalculateDuty`. If a row is inserted via:
- Standard JSON:API (`POST /api/DutyCalculation`)
- Direct SQLAlchemy (test data, scripts, admin)
- Any future integration

...the `early_row_event` will fire (recalculating from whatever `duty_rate` / `additional_tax` values were provided), but the tariff lookup, rate selection, and surtax determination **do not run**. The caller must supply correct rate values manually or get wrong answers.

**customs_app**: Rules fire on every transaction that touches `SurtaxOrder` or `SurtaxLineItem`, from any entry point — API, test data loader, Admin UI, future integrations. This is LogicBank's core value proposition, and this project actually uses it.

---

## 6. Missing Requirements

The prompt asked for several things that `customs_appZ` did not deliver:

| Requirement from prompt | customs_appZ | customs_app |
|---|---|---|
| Provincial sales tax / HST | ❌ Not implemented | ✅ `ProvinceTaxRate`, `Rule.formula` |
| Surtax applicability by ship date | ❌ Not modeled | ✅ `Rule.formula` on `surtax_applicable` |
| Multi-line customs entries | ❌ Single flat record | ✅ `SurtaxOrder` / `SurtaxLineItem` |
| Country-level surtax flag (USMCA exemptions) | ❌ Hardcoded in `TariffRate` data | ✅ `CountryOrigin.surtax_applicable` |
| Runnable UI with examples | ✅ Admin UI auto-generated (works) | ✅ Admin UI auto-generated (works) |
| Germany, US, Japan, China examples | ✅ Test data present | ✅ Test data present |

---

## 7. What "No Rules" Costs

Because there are no `Rule.sum` rollups, there is no order-level total to display or validate — there is only ever one calculation record per API call.

Because there are no `Rule.constraint` rules, invalid data (negative values, future ship dates) can be stored without error.

Because there is no `Rule.formula` for `surtax_applicable`, the ship date cutoff from the regulation (`>= 2025-12-26`) is ignored in this implementation.

The `declare_logic_message = "ALERT:  *** No Rules Yet ***"` line was left in `declare_logic.py` by the code generator. It is accurate.

---

## 8. The Request Pattern Missed

The prompt was a textbook Request Pattern (ROP) candidate:

> "calculate [outputs] when [inputs] is given"

The correct architecture:
1. `DutyCalculation` table with request fields (`hs_code_id`, `origin_country_id`, `value_amount`, `province_code`, `ship_date`)
2. `early_row_event` performs lookups and populates response fields (`duty_rate`, `duty_amount`, `surtax_applicable`, `pst_hst_amount`, `total_amount`)
3. API is a thin wrapper: parse request → insert row → return committed row

Instead, the API **is** the business logic, and the table is just a persistence afterthought.

The session transcript (`session_transcript.md`) documents that this was recognized retrospectively during the same session that created the project, and the pattern was used correctly in `customs_app`.

---

## 9. Summary

| Dimension | customs_appZ | customs_app |
|---|---|---|
| Logic location | API service (wrong layer) | `logic/logic_discovery/` (correct) |
| Rule type | Procedural `early_row_event` | Declarative `Rule.formula/sum/copy/constraint` |
| Declarative rules | 0 | 13 |
| API lines doing business logic | ~150 | 0 |
| Provincial tax modeled | No | Yes |
| Surtax date cutoff enforced | No | Yes |
| Multi-line orders | No | Yes |
| Logic fires on all entry points | No | Yes |
| Missing requirements | 3 of 4 core | 0 |

This is what the platform produces when the AI does not know what platform it is working with. The application runs, the endpoint returns answers, and the Admin UI works — but the architectural contract of GenAI-Logic (logic in rules, enforced everywhere) is entirely absent.
