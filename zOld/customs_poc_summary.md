# Teaching AI to Build Smart: The Context Engineering Journey

This is an engineering chronicle of the customs POC — a working implementation of CBSA PC 2025-0917 steel derivative goods surtax rules. It documents not just what was built, but how iterative Context Engineering (CE) refinements were the active ingredient that turned early AI failures into a production-ready result.

Context Engineering is the practice of curating and refining the knowledge given to AI so it produces architecturally correct output — not just code that compiles.

---

<details>
<summary><strong>Step 0 — App Built Without GenAI-Logic Context</strong></summary>

**What happened:** Claude built a working customs app using standard code generation — procedural logic in API endpoints, no LogicBank rules, no declarative enforcement.

**Why:** The GenAI-Logic Context Engineering materials were not loaded. Claude had no knowledge of the platform and defaulted to familiar patterns.

**Insight:** Without Context Engineering, AI cannot apply a platform it doesn't know exists. The output runs, but delivers none of GenAI-Logic's architectural value: no rule enforcement, no bypass protection, no code reduction. Knowing the framework is a hard prerequisite — not a nice-to-have.

**Action:** Loaded full GenAI-Logic Context Engineering materials before the next attempt.

</details>

---

<details>
<summary><strong>Step 1 — Context Engineering Loaded, But Logic Landed in the Wrong Place</strong></summary>

**What happened:** Claude rebuilt the app with GenAI-Logic context and produced a Custom API — but implemented all business logic as procedural code inside the endpoint rather than as declarative LogicBank rules.

**Why:** The CE materials described the platform but didn't yet give Claude explicit guidance on *where* calculations belong. Claude defaulted to writing code in endpoints because that's the most familiar pattern across frameworks. The **Request Object Pattern** — how LogicBank rules access row data during commit — was the missing piece.

**Insight:** Knowing a platform exists is not enough. CE must define architectural boundaries explicitly. "Use rules for calculations" is not sufficient instruction; you need to show the pattern concretely. The absence of a single worked example was enough to send AI down the wrong path.

**Action:** Updated CE to explain the Request Object Pattern and added an explicit directive: business logic calculations and constraints belong in LogicBank rules, not in endpoint code.

</details>

---

<details>
<summary><strong>Step 2 — CE Updated, But Subsystem Generation Exposed New Gaps</strong></summary>

**What happened:** Claude attempted a full rebuild and produced materially wrong results: data model errors (non-autonumber primary keys on join tables), and business logic still written as procedural code instead of declarative rules.

**Why:** The CE had been written to guide *iterative micro-edits* — small additions to an existing system. Generating an entire subsystem from scratch is a qualitatively different task and exposed two gaps:
1. No explicit data model conventions (autonumber PKs, foreign key patterns)
2. No unambiguous preference signal — when both procedural code and declarative rules *could* work, AI needs to be told which to prefer

**Insight:** CE guidance must match the scale of the task. Instructions written for one-line edits don't transfer automatically to subsystem generation. AI needs explicit advisories for data model conventions and a clear, unambiguous preference rule — not just architectural description.

**Action:** Updated CE with data model advisories (autonumber primary keys required, FK naming conventions) and an explicit rule: *when a calculation or constraint can be expressed in LogicBank, use a rule — not endpoint code.*

</details>

---

<details>
<summary><strong>Step 3 — Production-Ready App: Context Engineering Delivers</strong></summary>

**What happened:** With the updated CE, Claude generated a correct, complete customs implementation on the first attempt.

**What was built:**

- **`logic/logic_discovery/cbsa_steel_surtax.py`** — Declarative rules implementing CBSA PC 2025-0917:
  - `customs_value = quantity × unit_price`
  - `duty_amount = customs_value × duty_rate` (rate copied from `HSCodeRate` reference table)
  - `surtax_amount` — conditional on `ship_date ≥ 2025-12-26` and country of origin
  - `pst_hst_amount` — rate copied from province reference table
  - Order-level rollup sums for all line item amounts
  - Constraints: ship date cannot precede entry date; quantity and unit price must be positive

- **`test/api_logic_server_behave/features/cbsa_surtax.feature`** — 6 Behave scenarios covering surtax applicability, pre/post cutoff dates, non-surtax countries, multi-line rollup, and constraint enforcement

- **Admin App** — full CRUD at `/admin-app` for manual testing and business user workshopping

**A real bug that AI missed — and rules caught:** During development, one scenario produced a `TypeError` because the API delivered `datetime.datetime` objects while date comparisons expected `datetime.date`. The fix required a normalizing helper (`to_date()` in `cbsa_steel_surtax.py`). This is the kind of edge case that procedural code embeds silently in multiple places; in the rule-based version, one fix covered all entry paths.

**Value of Product (GenAI-Logic):** Declarative rules enforce all calculations regardless of entry point — API, test suite, Admin App, or direct database write. No path can bypass enforcement by architectural necessity.

**Value of Process (Context Engineering):** Each iteration captured a failure, extracted an insight, and encoded it as reusable guidance. Future projects start here — they don't repeat Steps 0–2.

</details>

---

## Bottom Line

Five declarative rules replaced the equivalent of 200+ lines of procedural code — and caught a type coercion bug that procedural implementations would have embedded silently across multiple call sites.

The CE investment compounds: every insight from failure becomes durable guidance that every future AI-assisted build inherits.

> **Product + Process = AI that builds maintainable systems, not just code that compiles.**
