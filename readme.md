# Customs Surtax POC — Engineering README

**Audience:** Engineering colleagues evaluating GenAI-Logic
**Project:** CBSA Steel Derivative Goods Surtax calculator, built as a proof-of-concept for FedEx

![app](images/app_screenshot.png)

## Creation

The subsystem was created by providing the following prompt to Copilot:

```text
Create a fully functional application and database for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order under subsection 53(2) and paragraph 79(a) of the Customs Tariff program code 25267A to calculate duties and taxes including provincial sales tax or HST where applicable when hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' and create runnable ui with examples from Germany, US, Japan and China" this prompt created the tables in db.sqlite.
```

---

## 1. What Was Created

The following artifacts were generated and are present in this repository.

**Data layer** — `database/models.py` contains auto-generated SQLAlchemy models for `SurtaxOrder`, `SurtaxLineItem`, `HSCodeRate`, `CountryOrigin`, and `ProvinceTaxRate`. The schema follows standard autonumber primary key conventions.

**Business logic** — `logic/logic_discovery/cbsa_steel_surtax.py` contains 16 declarative rules: 8 formula rules for line-item calculations (customs value, duty, surtax, PST/HST, total), 5 sum rules rolling up line totals to order-level fields, 1 formula rule for surtax applicability (date and country checks), and 3 constraints (ship date validation, positive quantity, positive unit price). The file is auto-loaded at startup by `logic/logic_discovery/auto_discovery.py`.

**REST API** — The JSON:API server runs at `http://localhost:5656/api/`. Custom API endpoints are co-located in `api/api_discovery/` and auto-loaded by `api/api_discovery/auto_discovery.py`. No manual registration is required.

**Admin UI** — A full CRUD interface is available at `http://localhost:5656/admin-app` for manual testing and business user workshopping.

**Test suite** — `test/api_logic_server_behave/features/cbsa_surtax.feature` defines 7 Behave scenarios covering: surtax-applicable orders, pre-cutoff (no surtax) orders, non-surtax countries, multi-line rollups, and three constraint violations. Step implementations live in `test/api_logic_server_behave/features/steps/`.  

**Test Report** - the test suite creates logs we use to create a report.  To see the **report**, [click here](test/api_logic_server_behave/reports/Behave%20Logic%20Report.md).

**Reference data loader** — `load_cbsa_data.py` populates HS codes, countries, and provincial tax rates from CBSA PC 2025-0917.



---

## 2. Context Engineering Journey

This app was built across four iterations. Each iteration revealed a specific gap in Context Engineering (CE) — the curated knowledge given to the AI before generation. The gaps and their fixes are documented below.

<details>
<summary><strong>Step 0 — App built without GenAI-Logic context</strong></summary>

**What happened:** Claude built a working customs application using standard Python code generation — procedural logic embedded in API endpoints, no LogicBank rules, no declarative enforcement.

**Why:** The GenAI-Logic Context Engineering materials were not loaded. Claude had no knowledge of the platform and defaulted to familiar patterns.

**Insight:** Without Context Engineering, an AI cannot apply a framework it doesn't know exists. The result compiles and runs, but delivers none of the architectural value: no rule enforcement, no bypass protection, no code reduction relative to hand-written procedural code.

**Action:** Loaded the full GenAI-Logic Context Engineering materials (`.github/.copilot-instructions.md`) before the next generation attempt.

</details>

<details>
<summary><strong>Step 1 — Context Engineering loaded; logic landed in the wrong place</strong></summary>

**What happened:** Claude rebuilt the app with GenAI-Logic context and produced a Custom API service, but implemented the business calculations as procedural code inside the endpoint handlers rather than as declarative LogicBank rules.

**Why:** The Context Engineering described that rules exist but did not give Claude explicit guidance on architectural boundaries — specifically, that calculations belong in `logic/logic_discovery/` as `Rule.*` declarations, not as Python code executing inside a Flask route. The Request Object Pattern (how LogicBank rule functions receive `row`, `old_row`, and `logic_row`) was absent from the CE materials.

**Insight:** Knowing a framework exists is not sufficient. Context Engineering must explicitly specify where each category of code belongs. Without a concrete pattern showing the rule function signature and the separation between API orchestration and rule enforcement, AI defaults to writing business logic where it last saw similar code — in endpoint handlers.

**Action:** Updated Context Engineering to document the Request Object Pattern, show a worked example of a formula rule with `row` / `old_row` / `logic_row` parameters, and state explicitly that business calculations and constraints belong in `logic/logic_discovery/` rules, not in API endpoint code.

</details>

<details>
<summary><strong>Step 2 — Context Engineering updated; subsystem generation exposed new gaps</strong></summary>

**What happened:** Claude attempted a full rebuild and produced poor results on two dimensions: data model errors (non-autonumber primary keys for `SurtaxOrder` and `SurtaxLineItem`) and business logic still written as procedural code rather than declarative rules.

**Why:** The Context Engineering had been written to guide iterative micro-edits to an existing project — small additions and corrections one at a time. Generating a complete subsystem from scratch is a different task that exposed two separate gaps. First, CE contained no explicit data model conventions, so Claude improvised primary key patterns. Second, CE described rules but did not provide an unambiguous preference signal: when both procedural code and declarative rules are valid Python, Claude will default to procedural without a clear directive.

**Insight:** Context Engineering must match the scale of the generation task. Guidance written for incremental editing does not transfer automatically to greenfield subsystem generation. Subsystem generation requires: (1) explicit data model conventions (e.g., autonumber integer PKs), and (2) an unambiguous preference directive — not just "rules are available" but "use a rule whenever a calculation or constraint is involved."

**Action:** Updated Context Engineering to add a data model advisory (integer autonumber primary keys required) and an explicit preference rule: use `Rule.*` declarations over endpoint code for any calculation, derivation, copy, or constraint.

</details>

<details>
<summary><strong>Step 3 — Production-ready app generated correctly on first attempt</strong></summary>

**What happened:** With the revised CE in place, Claude generated a complete, correct customs application in a single pass: proper autonumber data model, 16 declarative LogicBank rules enforcing all calculations, clean separation between API routing and rule enforcement, and a Behave test suite with requirement-to-rule traceability.

**Why it worked:** Every previous failure mode had been addressed: platform awareness (Step 0), architectural placement (Step 1), data model conventions and rule preference signal (Step 2).

**Insight:** Context Engineering compounds. Each prior failure encoded a reusable correction. Any future project that loads this CE material starts at Step 3 — the failures were compressed into training assets, not wasted effort.

**What this means for evaluation:** The product (GenAI-Logic) provides the architectural value. The process (Context Engineering iteration) determines whether the AI can reach that architecture reliably. Both matter.

</details>

---

## 3. Testing

To run the Behave test suite, start the server first, then execute:

```bash
cd test/api_logic_server_behave
python behave_run.py
```

The Behave Logic Report (`test/api_logic_server_behave/behave_logic_report.py`) produces a per-scenario trace showing which rules fired, in what order, and with what before/after values. This creates a direct requirement → rule → execution traceability chain. For example, the scenario `Surtax applies for post-cutoff ship date with surtax country` in `features/cbsa_surtax.feature` traces through the `determine_surtax_applicability` formula rule, the `calculate_surtax_amount` formula rule, the `copy_pst_hst_rate` formula rule, and all five sum rules up to the order totals — all triggered by a single line-item insert.

---

## 4. Debugging

The LogicBank logic log records before- and after-values for every attribute touched during a transaction commit. Rules in `logic/logic_discovery/cbsa_steel_surtax.py` emit structured log messages using `logic_row.log()` — for example:

```
Surtax Amount: 125000.0 (Applicable: True)
PST/HST Rate: 0.1625
Surtax Applicable: True (Ship Date: 2026-01-15, Date Check: True, Country Check: True, Cutoff: 2025-12-26)
```

To extract a clean logic trace for a specific transaction, set the log level to `DEBUG` in `config/logging.yml` and filter on the `logic_logger` name. The debug documentation for logic traces is in `docs/logic/readme.md`. The `test_date_fix.sh` script at the project root demonstrates extracting and validating specific logic log output.

---

## 5. Maintenance

Changing a rule requires editing one declaration in `logic/logic_discovery/cbsa_steel_surtax.py`. The engine recomputes the dependency graph at startup and applies the change to every write path automatically — insert, update, delete, and foreign key reassignment. There is no need to find insertion points, trace execution paths, or audit every API endpoint.

The contrast with procedural code is quantified in `logic/procedural/declarative-vs-procedural-comparison.md`. For an equivalent order management system, the procedural approach produced 220+ lines of code with 2 critical bugs (missed cases for FK reassignment). The declarative approach produced 5 rules with 0 bugs. The customs system in this POC has 16 rules. An equivalent procedural implementation would require explicit handling of every combination of line-item insert, quantity update, price update, HS code change, country change, and ship date update — each requiring code changes in multiple functions.

---

## 6. AI Use and Determinism

Rules in `logic/logic_discovery/cbsa_steel_surtax.py` execute deterministically at transaction commit time via SQLAlchemy ORM events. There is no inference, no sampling, and no variability: given the same input state, the same output is always produced. All writes to the database — through the REST API, through the Behave test suite, through the Admin UI at `/admin-app`, or through any agent or script — pass through the identical rule set. The execution order is computed once at startup from the declared dependency graph, not from code paths at runtime.

---

## 7. Bypass Impossibility

Rules fire by architectural necessity, not by policy. The LogicBank engine hooks into SQLAlchemy's `before_flush` and `before_commit` events at the ORM layer, below Flask and below any API handler. There is no write path to the database that does not pass through the same hooks. You cannot bypass enforcement by calling a different endpoint, using a different HTTP method, writing a new API service, or modifying the database through a workflow step. This is the structural property that makes AI-proposed logic changes safe to commit: a rule change that passes validation is automatically enforced everywhere, with no additional wiring.

---

## 8. What This Is Not

The rules engine enforces data integrity at write time. It is not a tool for read-only analytics or reporting — SQL views, BI tools, or direct query optimization are appropriate there. It is not a workflow orchestration engine: multi-step approval processes, long-running sagas, and external system coordination belong in tools like Temporal or Airflow. It does not replace complex algorithms — machine learning models, graph traversal, or combinatorial optimization are pure Python problems. Rules solve one specific problem well: ensuring that defined data relationships are always true, across every write path, automatically.

---

## 9. A/B Result

For the foundational order management case, 5 declarative rules replaced 220+ lines of AI-generated procedural code, and the procedural version contained 2 critical bugs — one for `Order.customer_id` reassignment (old customer balance not decremented) and one for `Item.product_id` reassignment (unit price not re-copied from new product) — that were only discovered through directed prompting. The full experiment, including the original procedural code and the AI's own analysis of why it failed, is documented in `logic/procedural/declarative-vs-procedural-comparison.md`.

---

**Bottom line:** The customs POC demonstrates that GenAI-Logic delivers correct, maintainable business logic — and that getting an AI to generate it correctly requires Context Engineering to be as precise about architecture as it is about syntax.
