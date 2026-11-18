# Episode 4: Agile Testing Activities and Tracking

16:9 | 1920 × 1080 | 30 fps | 600 seconds
Voice: en-IN-NeerjaNeural, English (India). Measured narration fitted uniformly to the timeline.
Direction: navy, mint and lavender; Inter; risk-to-evidence diagrams; fictional examples.

## chapter-01 — Introduction (0.00s, 56.57s)
Narration: Agile teams need frequent visibility into testing progress, remaining risks and blocked work. Today we examine planning, execution tracking, defect management and stakeholder reporting. Imagine that stakeholders ask whether a customer-management release is ready. A dashboard says seventy percent of tests have passed. That number alone cannot answer the question. We need to know which features were tested, which risks remain and whether important failures are unresolved. In this lesson, treat tracking as a way to support a decision. Every chart should have a meaning and a next action. Our fictional release contains registration, profile editing and customer search. We will connect each feature to scenarios, results, defects and a concise release update.
Visual direction: QA progress dashboard.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-02 — Planning (56.57s, 62.27s)
Narration: For a CRM sprint with registration, profile updates and search, identify acceptance criteria and scenarios for each feature. Plan environments, accounts, sample data and integration dependencies before execution begins. Begin with registration. The team agrees that a valid new address creates an account, a duplicate address is handled safely, and an invalid address cannot complete registration. List the environment, build identifier and account data needed for each check. If outbound email is unavailable, mark email-confirmation scenarios as blocked rather than failed or passed. This distinction matters because a failure indicates observed incorrect behavior, while a blocked result indicates missing evidence. Planning dependencies early makes the dashboard easier to interpret later and gives the team time to restore missing capabilities.
Visual direction: Stories expanded into scenarios.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-03 — Execution status (118.83s, 63.77s)
Narration: Suppose forty test cases exist: twenty-eight passed, six failed, four blocked and two not run. The numbers are useful, but risk matters more than raw percentages. One failed payment test can outweigh several cosmetic failures. Calculate the illustrative status carefully. There are forty tests: twenty-eight passed, six failed, four blocked and two not run. Twenty-eight out of forty is seventy percent passed across the planned set. Twenty-eight out of thirty-four executed tests is approximately eighty-two percent. Both calculations can be mathematically correct but answer different questions. Label the denominator. More importantly, inspect the six failures: a broken account-ownership check may prevent release even if many visual checks pass. Do not compress blocked work, unexecuted work and failed behavior into a single reassuring percentage.
Visual direction: Bar chart of illustrative test statuses.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-04 — Defects (182.60s, 65.47s)
Narration: Record a concise title, environment, reproduction steps, expected behavior, actual behavior and evidence. Severity describes impact; priority describes urgency. Link defects to affected stories to maintain context. Write a defect that a colleague can reproduce. Use a title such as Duplicate registration returns an internal error on build forty-two. Specify the test environment, a synthetic existing address, the exact registration action, the expected safe response and the actual error. Attach sanitized evidence and link the relevant story. Severity describes the impact of the defect; priority expresses how urgently the team chooses to address it. They often influence each other but are not interchangeable. A small-looking visual issue might still be urgent before a time-sensitive demonstration, while its functional severity remains low.
Visual direction: Sample invalid-email defect ticket.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-05 — Metrics (248.07s, 64.40s)
Narration: Useful indicators include defect leakage, execution progress, cycle time, blocked tests and automated test stability. A high pass rate is not proof of adequate coverage. Use metrics to identify patterns rather than reward superficial numbers. Build a balanced dashboard. Show unresolved critical risks, blocked work, test execution and defect trends with enough context to explain changes. If execution falls because the test environment was unavailable, annotate that cause. If the pass rate improves because failing tests were removed, the apparent improvement is misleading unless the scope change is visible. For automation, track unstable checks separately so repeated reruns do not disguise unreliable feedback. Metrics are prompts for investigation. Choose a small set that helps the team decide what to fix, finish or investigate next.
Visual direction: Metric definitions and caution callouts.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-06 — Reporting (312.47s, 62.67s)
Narration: A good update answers: what was tested, what remains, what risks exist and what help is needed? For example: registration and profile testing are complete; search is underway; two critical defects remain; performance testing is blocked by test data. Turn the dashboard into a useful update. Registration and profile editing have been checked on the release candidate. Customer search remains partly blocked by incomplete test data. One critical authorization defect is open. The release decision needs either a verified fix or a clear scope change that removes the exposure. This message is stronger than listing how many tickets moved today. It connects completed work with remaining uncertainty. Include an owner and next step for the blocker so stakeholders understand how the uncertainty can be reduced rather than simply being informed that it exists.
Visual direction: Concise stakeholder status template.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-07 — Tool walkthrough (375.13s, 56.50s)
Narration: Open a story, review criteria, create test tasks, log linked defects, verify fixes and update quality status. Maintain traceability from requirements to results. Follow one story through its evidence. Start with the acceptance criteria. Link a set of checks, record their results against the build, create a linked defect for a failure and attach retest evidence after the fix. Then run any relevant regression checks before marking the work complete. These links let another team member reconstruct why the story was judged ready. The exact screens depend on the tracking product; the relationship among requirement, test, defect and evidence matters more than the tool. Avoid duplicating the same status manually in several places where it can drift.
Visual direction: Fictional Jira-style workflow.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-08 — Worked example (431.63s, 43.60s)
Narration: For your practice task, write a release update in four sentences. Say what was tested, what remains, which risk matters most and what help is needed. Use the forty-test example, but do not rely on the pass rate as your recommendation. A good answer could say that most registration scenarios pass, search data blocks four checks, a failed account-isolation scenario is critical, and the team needs a fix plus focused retesting. Now ask whether the release would become acceptable if five cosmetic failures were resolved while the authorization failure remained. The risk-based answer is still no.
Visual direction: Release dashboard
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-09 — A closer look (475.23s, 50.07s)
Narration: Here is a second numerical example. Yesterday the team planned forty checks and passed twenty-eight. Today it removes ten checks from scope and passes the same twenty-eight of the remaining thirty. The displayed pass rate rises dramatically, but no additional behavior was tested. That change may be legitimate if the release scope changed, yet the report must explain it. Record which feature or risk moved out of scope and who made the decision. Otherwise a chart can suggest improved product quality when only the denominator changed. A useful dashboard preserves the relationship between scope, execution and risk so readers can interpret movement rather than simply admire a higher percentage.
Visual direction: Release dashboard
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-10 — Verify the outcome (525.30s, 48.37s)
Narration: Track blocked work with the same care. If four checks need unavailable search data, record the data dependency and the person coordinating its restoration. Separate the age of the blocker from the time spent actively investigating. If the team can safely prepare synthetic data, describe what it must represent and how its suitability will be checked. Once the blocker is removed, update the result after execution; do not automatically convert Blocked to Passed. The absence of an obstacle is not evidence of correct behavior. This small reporting discipline prevents an optimistic workflow shortcut from becoming a false claim about what the team actually verified.
Visual direction: Release dashboard
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

## chapter-11 — Recap (573.67s, 26.33s)
Narration: Tracking exists to support decisions, not to generate paperwork. Knowledge check: why can a sprint with ninety-five percent passing tests still be unsafe to release? Subscribe to Tech at sixty for the next episode in this Agile Testing Masterclass. Practice the example with synthetic data, and share the most important risk you identified in the comments.
Visual direction: Risk-focused summary slide.
On-screen example: Release dashboard; steps: Plan scenarios | Track evidence | Report remaining risks; checks: Passed: 28 of 40 | Failed: 6 • Blocked: 4 | Not run: 2
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: A pass rate needs risk context.

