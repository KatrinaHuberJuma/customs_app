

Readme_context_engineering.md
60 lines

md

Custom App Readme

Working on this markdown to chronicle a series of changes

8:16 PM
Here are a few questions to help me understand what you're aiming for:

Q: What's your primary goal for this README?
A: Both, and highlight the importance of revising the CE (context engineering)

Q: Which version do you prefer as a starting point?
A: 1

Q: What would you like to improve or add? (Select all that apply)
A: I need to clarify the steps a bit

8:18 PM
Got it. Let me look at what you have and draft a cleaner version that gives equal weight to the context engineering iteration process and GenAI-Logic's value, while making the steps clearer.


Reading the uploaded README
One thing I want to clarify before drafting: in the current Version 1, Step 0 and Step 1 are grouped together under "Attempt 1," but they represent two distinct moments — first Claude tries without any GenAI-Logic context, then with context but still failing. Then Step 2 is a third attempt that also fails, followed by a retry that finally works.

Is that the correct sequence? And is the key point you want to emphasize that each CE revision was what unlocked the next improvement — i.e., the CE updates are the active ingredient, not just Claude trying again?

great point - that was my first issue.   Here are the exact steps:

Gen NOT-G/L 
this was because CE (Context Eng) not loaded, so the app got no value out of G/L (genai-logic)

Code in Custom API
Rebuilt app with CE, but quite poor -- most of the logic was in a Custom API

So, updated CE: use the Request Pattern

Bad Gen: very poor result Data Model errors (use autonum ids as pkey), not using Rules
this was because CE was designed for iterative micro-edits, not subsystem generation
So, updated CE with advisories for data model and preference for rules over code

Good app created with this CE

what I want is the steps summarized in the disclosure headers, explained below.  this makes it easy to present to client.

the explanation should highlight "insights" for training, and knowledge of the CE material

Show more
8:27 PM
Here's a revised draft:


Created a file, read a file
Each disclosure section now follows a consistent structure — What happened / Why / Insight / Action — so clients can scan the headers to get the arc, then drill into any step for the reasoning. The "Insight" block in each step is where the CE learning lives, making it easy to pull those out for training discussions.

A few things to review: does the framing of Step 2's "why" (CE designed for micro-edits, not subsystem generation) accurately reflect what you experienced? And do you want the bottom line to stay punchy like this, or expand it slightly for a client-facing context?

Readme context engineering
Document · MD 




Claude is AI and can make mistakes. Please double-check responses.
Readme context engineering · MD
Copy

# Teaching AI to Build Smart: The Context Engineering Journey

Context Engineering (CE) is the practice of curating and refining the knowledge we give AI so it produces architecturally correct results—not just code that runs. This chronicle shows how iterative Context Engineering updates transformed early failures into a production-ready system.

---

<details>
<summary><strong>Step 0: App Built Without GenAI-Logic Context</strong></summary>

**What happened:** Claude built a working customs application using standard code generation—procedural logic in API endpoints, no LogicBank rules, no declarative enforcement.

**Why:** The GenAI-Logic Context Engineering materials were not loaded. Claude had no knowledge of the platform, so it defaulted to familiar patterns.

**Insight:** Without Context Engineering, AI cannot apply a platform it doesn't know exists. The output compiles and runs, but delivers none of GenAI-Logic's architectural value—no rule enforcement, no bypass protection, no code reduction.

**Action:** Loaded full GenAI-Logic Context Engineering materials before the next attempt.

</details>

---

<details>
<summary><strong>Step 1: Context Engineering Loaded, But Logic Lands in the Wrong Place</strong></summary>

**What happened:** Claude rebuilt the app with GenAI-Logic context and produced a Custom API—but most of the business logic was implemented as procedural code inside the API endpoints rather than as declarative LogicBank rules.

**Why:** The Context Engineering materials described the platform but didn't yet give Claude clear guidance on *where* logic belongs. Claude defaulted to what it knows: writing code in endpoints.

**Insight:** Knowing a platform exists is not enough. Context Engineering must explicitly instruct AI on architectural boundaries—what belongs in rules versus endpoints. The **Request Object Pattern** (how LogicBank rules access row data) was the missing piece.

**Action:** Updated Context Engineering to explain the Request Object Pattern and clarify that business logic calculations belong in LogicBank rules, not endpoint code.

</details>

---

<details>
<summary><strong>Step 2: Context Engineering Updated, But Subsystem Generation Exposed New Gaps</strong></summary>

**What happened:** Claude attempted a full rebuild and produced poor results: data model errors (non-autonumber primary keys), and business logic still written as procedural code rather than declarative rules.

**Why:** The Context Engineering had been written to guide *iterative micro-edits*—small, incremental changes to an existing system. Generating an entire subsystem from scratch is a different task that exposed two gaps: (1) no explicit data model guidance, and (2) no clear preference signal telling Claude to favor rules over code when both could work.

**Insight:** Context Engineering must match the scale of the task. Guidance written for micro-edits doesn't transfer automatically to subsystem generation. AI needs explicit advisories for data model conventions and unambiguous direction to prefer declarative rules over procedural alternatives.

**Action:** Updated Context Engineering with data model advisories (autonumber primary keys required) and an explicit preference rule: *use LogicBank rules over endpoint code whenever calculations or constraints are involved.*

</details>

---

<details>
<summary><strong>Step 3: Production-Ready App — Context Engineering Delivers</strong></summary>

**What happened:** With the updated CE, Claude generated a complete, production-ready customs application on the first attempt: correct data model, declarative LogicBank rules enforcing all calculations, clean separation between API orchestration and rule enforcement.

**What it delivers:**
- **Custom API** — enables curl testing and automated validation
- **Admin App** — supports manual testing and business user workshopping
- **Declarative rules** — enforce customs values, duties, surtax, and provincial taxes regardless of entry point (API, test suite, or direct database access)
- **Zero bypass vulnerabilities** — 40X less code to maintain

**Value of Product (GenAI-Logic):** Generates infrastructure and enforces business logic declaratively = faster delivery, fewer defects, governed AI behavior.

**Value of Process (Context Engineering):** Each iteration captured a failure, extracted an insight, and encoded it as reusable guidance. Future projects inherit compressed expertise—they start at Step 3.

</details>

---

**Bottom Line:** Product + Process = AI that builds maintainable systems, not just code that compiles.
The CE investment compounds: every insight from failure becomes an asset for every future build.


## Appendix

Fed Claude desktop (smarter) draft 1, and asked it to revise with this prompt:

great point - that was my first issue.   Here are the exact steps:



0. Gen NOT-G/L 

this was because CE (Context Eng) not loaded, so the app got no value out of G/L (genai-logic)



1. Code in Custom API

Rebuilt app with CE, but quite poor -- most of the logic was in a Custom API



So, updated CE: use the Request Pattern



2. Bad Gen: very poor result

Data Model errors (use autonum ids as pkey), not using Rules





this was because CE was designed for iterative micro-edits, not subsystem generation

So, updated CE with advisories for data model and preference for rules over code



3. Good app created with this CE



what I want is the steps summarized in the disclosure headers, explained below.  this makes it easy to present to client.



the explanation should highlight "insights" for training, and knowledge of the CE material