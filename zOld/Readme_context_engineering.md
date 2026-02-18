Teaching AI to Build Smart: The Context Engineering Journey
<details> <summary><strong>Attempt 1: Wrong Approach</strong></summary>

Step 0: Claude builds customs app with regular code generation—procedural logic in endpoints, no LogicBank rules.

Step 1: Given GenAI-Logic context and prompted again. Claude codes a custom API but still misses the declarative pattern.

Result: Functions but fragile—bypass vulnerabilities, maintenance overhead.

Action: Context engineering materials updated with clearer architectural guidance.

</details> <details> <summary><strong>Iteration: Learning the Pattern</strong></summary>

Step 2: Claude tries again—generates more problematic code:

Data model uses wrong primary keys (not autonumber)
Still no use of declarative rules
Business logic scattered across endpoints
Result: Still not production-ready.

Action: Context engineering updated again with request object pattern examples, rule recognition guidance.

Step 2 (retry): Good app finally emerges—proper data model, declarative rules, clean architecture.

</details> <details> <summary><strong>The Deliverable: Production-Ready System</strong></summary>

What works:

Custom API enables curl testing and automated validation
Admin App provides manual testing and business user workshopping
Declarative rules enforce calculations regardless of entry point
Zero bypass vulnerabilities—40X less code to maintain
Value of Product (GenAI-Logic): Generates infrastructure + enforces business logic declaratively = faster delivery, fewer defects.

Value of Process (Context Engineering): Iterative refinement turns AI failures into reusable patterns—future projects benefit from compressed expertise.

</details>

Bottom Line: Product + Process = AI that builds maintainable systems, not just code that compiles.



# version2

Teaching AI to Build Smart: The Context Engineering Journey
<details> <summary><strong>The Wrong Path: Code That Works, Architecture That Doesn't</strong></summary>

Claude's first attempt used regular code generation to build the customs application. The app calculated duties and taxes correctly, but all the business logic lived in procedural code scattered across API endpoints. When we introduced GenAI-Logic context and prompted again, Claude built a custom API but still missed the core architectural principle: declarative rules should enforce business logic, not procedural endpoint code. The result worked for demos but created bypass vulnerabilities—any future code path could skip validation entirely. We updated the context engineering materials with clearer guidance about when to use rules versus endpoints.

</details> <details> <summary><strong>Iteration Teaches Patterns: From Failure to Understanding</strong></summary>

The next attempt revealed deeper misunderstandings. Claude generated a data model with incorrect primary keys and continued writing business logic as procedural code instead of declarative rules. The calculations existed, but in all the wrong architectural layers. We refined the context engineering materials again, this time adding explicit examples of the request object pattern and clearer recognition criteria for when calculations belong in LogicBank rules. With this enhanced context, Claude finally produced a production-ready application with proper data models, declarative rules handling all calculations, and clean separation between orchestration (endpoints) and enforcement (rules).

</details> <details> <summary><strong>The Deliverable: Speed Plus Quality</strong></summary>

The final system delivers value through multiple channels. The custom API enables automated curl testing for continuous validation. The Admin App provides manual testing and lets business users workshop requirements interactively. Most importantly, declarative rules enforce all calculations—customs values, duties, surtax, provincial taxes—regardless of whether data enters through the API, test suites, or direct database access. This eliminates bypass vulnerabilities while reducing code volume by 40X compared to procedural approaches.

The product (GenAI-Logic) generates working infrastructure and enforces business logic declaratively, enabling faster delivery with fewer defects. The process (context engineering) captures lessons from iteration, transforming AI failures into reusable architectural patterns that benefit every future project. Together, they enable AI to build maintainable systems instead of just code that compiles.

</details>