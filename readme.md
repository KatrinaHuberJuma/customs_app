# Customs Surtax POC — Engineering README

**Audience:** Technical GenAI-Logic evaluators

**Project:** CBSA Steel Derivative Goods Surtax calculator, built as a proof-of-concept.

Source: [`https://github.com/KatrinaHuberJuma/customs_app`](https://github.com/KatrinaHuberJuma/customs_app)

**Run Instructions:** at end

## Overview

### TL;DR - Enterprise Governance and Speed

The goal of this POC was to explore whether GenAI-Logic added significant value.  Our findings:

* An Enterprise-class system ensured *by architecture:* Governable Quality, Full-Featured

  * Logic reuse over all paths, by data-oriented rules enforced on commit
  * Full-featured Enterprise class (APIs for all objects, with enterprise features such as pagination, filtering, etc), logic enabled
* A several week effort became 30 minutes

<br>

### Two Creation Prompts

#### Subsystem Prompt
The subsystem was created by providing the following prompt to Copilot:

```text
Create a fully functional application and database for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order under subsection 53(2) and paragraph 79(a) of the Customs Tariff program code 25267A to calculate duties and taxes including provincial sales tax or HST where applicable when hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' and create runnable ui with examples from Germany, US, Japan and China" this prompt created the tables in db.sqlite.
```

#### Tests Prompt
```text
create behave tests from CBSA_SURTAX_GUIDE.md
```

<br>

### Results: system, test suite and report

#### System: API, Database, Logic, Admin App

![app](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-vibe/customs/app_screenshot.png?raw=true)


#### Test Suite and Report

The GenAI-Logic `create` command builds test services and Context Engineering. These enable the LLM to generate tests that proved the code worked, as well as elucidate the logic through readable test reports.


![behave rpt](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-vibe/customs/behave_report_git.png?raw=true)

### GenAI-Logic Architecture: Logic Automation + AI

The underlying architecture is a combination of key elements:

#### Generative AI - but that's not enough

Used extensively to create - and iterate - the system.  This occurs in the IDE, not at runtime.  

But GenAI alone is not enough.  AI pattern matching struggles with dependencies, as shown in the A/B Test (see end)

<br>

#### Logic Automation (engines for rules, api...)

The core GenAI-Logic [software architecture](https://www.genai-logic.com/product/architecture) consists of:

* Runtime Engines for logic, api, admin app and data access
* CLI Services to create projects, rules, etc


![arch](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-vibe/customs/Core-Architecture.png?raw=true)

<br>

#### Context Engineering: Automation Aware AI

GenAI-Logic projects are [AI-Enabled](https://apilogicserver.github.io/Docs/Project-AI-Enabled/): each project contains extensive Context Engineering (markdown files) that enable AI to understand and create Logic Automation components.  

For example, markdown files explain rule syntax, so AI can translate NL Logic into declarative rules.


##### Highly Leveraged; Support Recommended

As part of your project, you can extend Context Engineering.  We did so in this project (see section 2).

Such extensions require extensive architectural background, so training and support are recommended.

<br>

#### Runtime Architecture: Container, Governed AI

The resultant projects are standard containers.  Deploy without fees.  Sample scripts are provided for Azure.

Execution does *not* use probabilistic AI services *except* for explict AI Rules; these results are strictly governed by deterministic rules at commit time


---

## 1. Project Contents

The following artifacts were generated and are present in this repository.

**Data layer** — `database/models.py` contains auto-generated SQLAlchemy models for `SurtaxOrder`, `SurtaxLineItem`, `HSCodeRate`, `CountryOrigin`, and `ProvinceTaxRate`. The schema follows standard autonumber primary key conventions.

**Business logic** — `logic/logic_discovery/cbsa_steel_surtax.py` contains 16 declarative rules: 8 formula rules for line-item calculations (customs value, duty, surtax, PST/HST, total), 5 sum rules rolling up line totals to order-level fields, 1 formula rule for surtax applicability (date and country checks), and 3 constraints (ship date validation, positive quantity, positive unit price). The file is auto-loaded at startup by `logic/logic_discovery/auto_discovery.py`.

**REST API** — The JSON:API server runs at `http://localhost:5656/api/`. Custom API endpoints are co-located in `api/api_discovery/` and auto-loaded by `api/api_discovery/auto_discovery.py`. No manual registration is required.

**Admin UI** — A full CRUD interface is available at `http://localhost:5656/admin-app` for manual testing and business user workshopping.

**Test suite** — `test/api_logic_server_behave/features/cbsa_surtax.feature` defines 7 Behave scenarios covering: surtax-applicable orders, pre-cutoff (no surtax) orders, non-surtax countries, multi-line rollups, and three constraint violations. Step implementations live in `test/api_logic_server_behave/features/steps/`.  

**Test Report** - the test suite creates logs we use to create a report.  To see the **report**, [click here](test/api_logic_server_behave/reports/Behave%20Logic%20Report.md).

**Reference data loader** — `load_cbsa_data.py` populates HS codes, countries, and provincial tax rates from CBSA PC 2025-0917.

<br>

---

## 2. Context Engineering Revision: Subsystem Creation

This app was built across several iterations. Each iteration revealed a specific gap in Context Engineering (CE) — the curated knowledge given to the AI before generation. The gaps and their fixes are documented below.


### No GenAI-Logic CE → poor "Fat API" architecture

**What happened:** 
Claude built a working customs application using standard Python code generation. 

**Why:** The GenAI-Logic Context Engineering materials were not loaded. Claude had no knowledge of the platform and defaulted to standard, familiar patterns.

**Insight:** Without Context Engineering, an AI cannot apply a framework it doesn't know exists. The result is a good demo: compiles and runs.  ***It does not deliver an Enterprise-class architecture***, as described below.

<br>

#### Demo API (no filtering, pagination, etc)

No Enterprise-class API with filtering, sorting, pagination, optimistic locking, etc.

<br>

#### Unshared, Path-specific logic (Quality Issues)

Logic embedded in a single path - not automatically shared

<br>

#### Procedural - Manual Ordering (with bugs)

Logic is *procedural* with explicit ordering.  **AI uses pattern matching to order execution, which can fail for business logic** - to see the A/B study, [**click here**](logic/procedural/declarative-vs-procedural-comparison.md).

> This in fact did occur in our example

<br>

### No Rules, Poor Data Model ( → CE fixes)
So, we loaded the Context Engineering, and re-built.

**What happened:** 
Claude attempted a full rebuild and produced poor results on two dimensions: 
1. data model errors (non-autonumber primary keys for `SurtaxOrder` and `SurtaxLineItem`) and 
2. business logic still written as procedural code rather than declarative rules.

**Why:** The Context Engineering had been written to guide iterative micro-edits to an existing project — small additions and corrections one at a time. Generating a complete subsystem from scratch is a different task that exposed two separate gaps. First, CE contained no explicit data model conventions, so Claude improvised primary key patterns. Second, CE described rules but did not provide an unambiguous preference signal: when both procedural code and declarative rules are valid Python, Claude will default to procedural without a clear directive.

**Insight:** Context Engineering must match the scale of the generation task. Guidance written for incremental editing does not transfer automatically to greenfield subsystem generation. Subsystem generation requires: (1) explicit data model conventions (e.g., autonumber integer PKs), and (2) an unambiguous preference directive — not just "rules are available" but "use a rule whenever a calculation or constraint is involved."

**Action:** Updated Context Engineering to 
1. add a data model advisory (integer autonumber primary keys required) and 
2. an explicit preference rule: use `Rule.*` declarations over endpoint code for any calculation, derivation, copy, or constraint.


<br>

### Proper app generated correctly on first attempt


**What happened:** 
With the revised CE in place, Claude generated a complete, correct customs application in a single pass: proper autonumber data model, 16 declarative LogicBank rules enforcing all calculations, clean separation between API routing and rule enforcement, and a Behave test suite with requirement-to-rule traceability.

**Why it worked:** Every previous failure mode had been addressed: platform awareness (Step 0), data model conventions and rule preference signal (Step 1).

**Insight:** Context Engineering learning compounds. Each prior failure encoded a reusable correction. Any future project that loads this CE material starts at Step 2 — the failures were compressed into training assets, not wasted effort.

**What this means for evaluation:** The product (GenAI-Logic) provides the architectural value. The process (Context Engineering iteration) determines whether the AI can reach that architecture reliably. Both matter.


<br>

> Key Takeaway: GenAI-Logic is a combination of infrastructure (API, Rules Engine), and AI.  Leveraging AI requires Context Engineering.  <br><br>This can enable major changes without a product re-release, but strong support/background is required.

<br>

---

## 3. Test Creation From Rules

**Behave** is a Python BDD (Behavior-Driven Development) test framework. Tests are written in plain English using **Gherkin** syntax (`Given / When / Then`), making them readable by non-engineers.

`Scenario: Surtax applies for post-cutoff ship date`
  `Given a SurtaxOrder for Germany to Ontario with ship_date 2026-01-15`
  `When a line item is added with hs_code 7208.10.00 quantity 1000`
  `Then the line item surtax_amount is 125000.00`

Each step maps to a Python function in `features/steps/`. GenAI-Logic adds a **Behave Logic Report** on top (`behave_logic_report.py`) that traces which rules fired per scenario — turning tests into living requirements documentation (requirement → rule → execution).

To run the Behave test suite, start the server first, then execute:

```bash
cd test/api_logic_server_behave
python behave_run.py
```

The Behave Logic Report (`test/api_logic_server_behave/behave_logic_report.py`) produces a per-scenario trace showing which rules fired, in what order, and with what before/after values. This creates a direct requirement → rule → execution traceability chain. 

For example, the scenario `Surtax applies for post-cutoff ship date with surtax country` in `features/cbsa_surtax.feature` traces through the `determine_surtax_applicability` formula rule, the `calculate_surtax_amount` formula rule, the `copy_pst_hst_rate` formula rule, and all five sum rules up to the order totals — all triggered by a single line-item insert.

<br>

---

## 4. Debugging: Standard IDE, Logging

The LogicBank logic log records before- and after-values for every attribute touched during a transaction commit. Rules in `logic/logic_discovery/cbsa_steel_surtax.py` emit structured log messages using `logic_row.log()` — for example:

```
Surtax Amount: 125000.0 (Applicable: True)
PST/HST Rate: 0.1625
Surtax Applicable: True (Ship Date: 2026-01-15, Date Check: True, Country Check: True, Cutoff: 2025-12-26)
```

To extract a clean logic trace for a specific transaction, set the log level to `DEBUG` in `config/logging.yml` and filter on the `logic_logger` name. The debug documentation for logic traces is in `docs/logic/readme.md`. The `test_date_fix.sh` script at the project root demonstrates extracting and validating specific logic log output.

<br>

---

## 5. Maintenance: Automated Reuse and Ordering

Changing a rule requires editing one declaration in `logic/logic_discovery/cbsa_steel_surtax.py`. The engine recomputes the dependency graph at startup and applies the change to every write path automatically — insert, update, delete, and foreign key reassignment. There is no need to find insertion points, trace execution paths, or audit every API endpoint.

The contrast with procedural code is quantified in `logic/procedural/declarative-vs-procedural-comparison.md`. For an equivalent order management system, the procedural approach produced 220+ lines of code with 2 critical bugs (missed cases for FK reassignment). The declarative approach produced 5 rules with 0 bugs. The customs system in this POC has 16 rules. An equivalent procedural implementation would require explicit handling of every combination of line-item insert, quantity update, price update, HS code change, country change, and ship date update — each requiring code changes in multiple functions.

<br>

---

## 6. AI Use: Human In the Loop, Determinism

While the system was *created* using AI, that was authoring only.  The expectation is that developers remain the ***human in the loop*** to verify the rules, and debug them.

The created Rules in `logic/logic_discovery/cbsa_steel_surtax.py` execute **deterministically** at transaction commit time via SQLAlchemy ORM events. There is no inference, no sampling, and no variability: given the same input state, the same output is always produced. 

All writes to the database — through the REST API, through the Behave test suite, through the Admin UI at `/admin-app`, or through any agent or script — pass through the identical rule set. The execution order is computed once at startup from the declared dependency graph, not from code paths at runtime.

### AI Rules Also Supported - With Governance
The system does support AI rules - rules that call AI at runtime (though not used here).  Importantly, these are subjected to this same governance:

> AI may propose values, but rules determine what commits.

<br>

---

## 7. Automatic Invocation - Code *Cannot* Bypass Rules

Rules fire by architectural necessity, not by policy. The LogicBank engine hooks into SQLAlchemy's `before_flush` and `before_commit` events at the ORM layer, below Flask and below any API handler. There is no write path to the database that does not pass through the same hooks. 

You cannot bypass enforcement by calling a different endpoint, using a different HTTP method, writing a new API service, or modifying the database through a workflow step. This is the structural property that makes AI-proposed logic changes safe to commit: a rule change that passes validation is automatically enforced everywhere, with no additional wiring.

<br>

---

## 8. What GenAI-Logic Is Not

The rules engine enforces data integrity at write time. It is not a tool for read-only analytics or reporting — SQL views, BI tools, or direct query optimization are appropriate there. 

It is not a workflow orchestration engine: multi-step approval processes, long-running sagas, and external system coordination belong in tools like Temporal or Airflow. It does not replace complex algorithms — machine learning models, graph traversal, or combinatorial optimization are pure Python problems. 

Rules solve one specific problem well: ensuring that defined data relationships are always true, across every write path, automatically.

<br>

---

## 9. A/B Result

For the foundational order management case, 5 declarative rules replaced 220+ lines of AI-generated procedural code, and the procedural version contained 2 critical bugs that were only discovered through directed prompting:
* one for `Order.customer_id` reassignment (old customer balance not decremented) and 
* one for `Item.product_id` reassignment (unit price not re-copied from new product)

The full experiment, including the original procedural code and the AI's own analysis of why it failed, is documented in `logic/procedural/declarative-vs-procedural-comparison.md`.  (tL;DR: pattern-matching AI deals poorly with complex dependencies common to business logic).

---

**Bottom line:** The customs POC demonstrates that GenAI-Logic delivers correct, maintainable business logic — and that getting an AI to generate it correctly requires Context Engineering to be as precise about architecture as it is about syntax.

<br>

## Run Instructions

Load under 16.01.39, windows or mac.

Start the server, and enter a SurTax Order:

* Country Origin: China
* Province: ON
* Order Number: <any unique>

And a SurTaxLineItem:

* Line #: 1
* Quantity: 1
* Price: 10000
* HS Code: < the first>

ReQuery, and Verify Total Amount Due: 14125

<br>

### To Recreate

```bash
genai-logic genai --using=samples/prompts/genai_demo.prompt
```

This creates a 1-table project, and opens it.

Then, in the opened project:

1. Establish your venv
2. Initialize Copilot (*Please load `.github/.copilot-instructions.md`*)
3. Enter the prompt above