# Prompt: Write the Customs App Engineering README

Please write an engineering README for the customs application we built as a proof-of-concept for FedEx. 

The audience is Wynford's engineering colleagues who are evaluating GenAI-Logic. The tone must be **factual and precise — no hype, no sales language**. It should be as short as practical while covering all the sections below.

---

## Structure

### 1. What Was Created
A concise list of the artifacts generated: API, Admin App, logic files, test suite, etc. Use actual filenames and paths where you can find them in this project.

### 2. Context Engineering Journey
Chronicle the 4 iterations that produced this app. For each step, use this structure:
- **What happened** (one sentence)
- **Why** (root cause — what was missing from Context Engineering)
- **Insight** (what this teaches about training AI for subsystem generation)
- **Action** (what was updated in Context Engineering)

The four steps:

**Step 0 — App built without GenAI-Logic context**
Context Engineering materials were not loaded. Claude built a working app using standard code generation — procedural logic in endpoints, no LogicBank rules.

**Step 1 — Context Engineering loaded, logic landed in the wrong place**
App rebuilt with GenAI-Logic context. Claude produced a Custom API but implemented business logic as procedural code in endpoints rather than declarative LogicBank rules. Context Engineering lacked explicit guidance on the Request Object Pattern.

**Step 2 — Context Engineering updated, subsystem generation exposed new gaps**
Context Engineering had been written for iterative micro-edits, not full subsystem generation. Claude produced data model errors (non-autonumber primary keys) and still defaulted to procedural code. Two gaps: no data model conventions, no explicit preference for rules over code.

**Step 3 — Production-ready app**
With updated Context Engineering, Claude generated a correct app on the first attempt: proper data model, declarative rules, clean architecture.

### 3. Testing
- How to run the Behave test suite
- What the Behave Logic Report shows: which rules fired per test, requirement → rule → execution trace
- Reference the actual test files in this project

### 4. Debugging
- How the logic log works: before/after values at commit time, full trace per transaction
- How to extract a clean logic log
- Reference the debug documentation

### 5. Maintenance
- Changing a rule: one edit, all entry paths inherit automatically
- No need to find insertion points or trace execution paths
- Contrast with procedural: show the line count difference if the data is in this project

### 6. AI Use and Determinism
- Rules execute deterministically at commit via SQLAlchemy events
- No inference, no variability — same input always produces same outcome
- All writes (API, test suite, Admin App, agents) pass through the same rule set
- No path can bypass enforcement

### 7. Bypass Impossibility
One short paragraph: rules fire on every write path by architectural necessity, not policy. This is the structural guarantee that makes AI-proposed changes safe to commit.

### 8. What This Is Not
Brief honest boundaries: not for read-only analytics, not for workflow orchestration, not for ML or complex algorithms. This builds engineering credibility.

### 9. A/B Result
5 declarative rules replaced 220 lines of procedural code with 2 bugs that even AI missed. Cite the actual comparison file in this project if it exists.

---

## Formatting notes
- Use `<details>` / `<summary>` collapsible sections for steps 0–3 in the Context Engineering section, so colleagues can scan headers and drill in
- Use actual filenames, paths, and curl commands from this project wherever possible
- No bullet points in prose sections — write in plain sentences
- End with one sentence: the bottom line for an engineering audience
