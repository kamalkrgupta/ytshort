# Episode 6: Four Agile Testing Quadrants

16:9 | 1920 × 1080 | 30 fps | 600 seconds
Voice: en-IN-NeerjaNeural, English (India). Measured narration fitted uniformly to the timeline.
Direction: navy, mint and lavender; Inter; risk-to-evidence diagrams; fictional examples.

## chapter-01 — Introduction (0.00s, 59.23s)
Narration: The Agile Testing Quadrants help select complementary tests. The dimensions are business-facing versus technology-facing and supporting development versus critiquing the product. They are not sequential stages. Start with a delivery rule: orders above a defined qualifying amount receive free shipping. A developer can test the calculation, a product specialist can clarify what counts toward the amount, a customer can explore whether the message is understandable, and an engineer can measure checkout under load. These are complementary views of quality. The quadrants organize the questions so a team notices gaps. They do not prescribe a testing order or assign exclusive ownership to particular job titles. Use the model as a conversation aid and adapt the examples to the risks of the feature you are building.
Visual direction: Labeled four-quadrant matrix.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-02 — Quadrant 1 (59.23s, 59.80s)
Narration: Technology-facing tests that support development include unit and component tests. A shopping-cart unit test can verify a subtotal or discount calculation. These automated checks offer fast, focused technical feedback. For quadrant one, isolate a shipping calculation. Suppose the agreed rule gives free delivery when the discounted subtotal is at least one thousand rupees. A low-level test checks nine hundred and ninety-nine, one thousand and one thousand and one. Each test runs without opening a browser or contacting a real payment service. When one fails, the feedback points closely to the calculation. Such tests support development by making small changes easier to evaluate. They still cannot tell us whether the team chose the correct threshold or whether the customer understands the final total.
Visual direction: Unit-test code and results.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-03 — Quadrant 2 (119.03s, 64.37s)
Narration: Business-facing tests that support development include acceptance examples. For free delivery above a threshold, clarify whether taxes and discounts count. Agree on examples and use them to verify the business rule. Quadrant two makes the business rule explicit. Ask whether taxes, gift cards and discount reductions affect eligibility. Use a concrete example: a basket worth eleven hundred receives a two-hundred-rupee discount, leaving a qualifying subtotal of nine hundred. Under our fictional rule, free shipping does not apply. Product, development and testing participants should agree on that result before implementation. The example can become an acceptance check, but the conversation is valuable even before automation exists. An executable scenario with an ambiguous expected result will simply automate an unresolved business question.
Visual direction: Given–When–Then delivery example.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-04 — Quadrant 3 (183.40s, 60.87s)
Narration: Business-facing tests that critique the product include exploratory and usability testing. A checkout button may function correctly yet be difficult to find. Realistic exploration reveals problems that predefined checks can miss. In quadrant three, explore the actual customer journey. Add items until shipping becomes free, then apply a coupon that lowers the subtotal below the threshold. Does the page explain why shipping reappeared? Does the total update consistently? Try keyboard navigation and a smaller display. You might find that every calculation is correct while the message leaves people confused. Record the situation, the user's difficulty and the effect on completing checkout. Exploration critiques the product by following observations and questions that a predefined rule check may never have considered.
Visual direction: Checkout usability observation.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-05 — Quadrant 4 (244.27s, 65.10s)
Narration: Technology-facing tests that critique the product include performance, security, reliability and scalability testing. Evaluate behavior under heavy traffic, unauthorized access attempts and system failures. Quadrant four examines technical qualities. A promotion may send many shoppers through the same calculation and checkout services at once. Define a realistic load model and an agreed response-time target before judging the result. Investigate errors, resource use and recovery as well as average response time. Security testing might check that one customer cannot modify another customer's basket. Reliability testing might simulate a temporary dependency failure. These activities require appropriate environments and authorization. A single passing scan or load run is evidence about the tested conditions, not proof that every technical risk is eliminated.
Visual direction: Load-testing metrics and security checks.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-06 — Combined example (309.37s, 64.70s)
Narration: For payments, quadrant one tests calculations; quadrant two verifies business outcomes; quadrant three explores interrupted payment journeys; quadrant four checks concurrency, resilience and security. The quadrants work together. Map a payment feature across all four views. Quadrant one checks fee and total calculations. Quadrant two uses examples of successful, declined and refundable payments. Quadrant three explores interrupted journeys, confusing messages and unexpected navigation. Quadrant four examines concurrent requests, access control and resilience. Some checks can reasonably fit more than one discussion because intent matters. Do not spend a meeting arguing about the perfect quadrant label while a duplicate-charge risk remains untested. The model succeeds when it helps the team ask a missing question and choose an effective way to investigate it.
Visual direction: Payment feature mapped to four quadrants.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-07 — Worked example (374.07s, 50.03s)
Narration: Avoid treating the matrix as four equal budgets. A simple internal tool and a public payment platform face different risks. One feature may need extensive security investigation; another may need more usability exploration. Automation also crosses the model. Unit tests are commonly automated, acceptance checks may be automated, and performance tools can automate technical experiments. Human judgment remains necessary when deciding what the results mean and what to investigate next. Describe the risk, select an appropriate activity and identify the evidence you want. Then use the quadrant model to check whether an important perspective has been missed.
Visual direction: Checkout & delivery
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-08 — Guided practice (424.10s, 49.43s)
Narration: For your practice task, take a password-reset feature and propose one activity for each quadrant. A possible low-level check verifies token-expiry calculations. A business example specifies what happens when an expired link is opened. Exploratory testing investigates whether recovery messages are understandable and accessible. Technical investigation examines unauthorized token reuse and behavior under a controlled request spike. Explain why each activity exists, rather than only naming a category. Finish by answering the lesson question: response times during a traffic spike belong naturally in the technology-facing critique represented by quadrant four.
Visual direction: Checkout & delivery
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-09 — A closer look (473.53s, 52.37s)
Narration: Use a gap-finding exercise to test whether the quadrants are helping. A team has hundreds of calculation checks and dozens of acceptance scenarios, but customers still abandon checkout because discount messages are confusing. Adding another calculation check may be inexpensive, yet it does not address the reported problem. The missing evidence concerns people using the integrated product. A purposeful exploratory or usability session can investigate the message, timing and effect on the customer's task. Conversely, a beautifully usable checkout can still fail under a promotion's traffic. The model encourages complementary investigation; strong coverage of one perspective should not make another perspective invisible.
Visual direction: Checkout & delivery
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-10 — Verify the outcome (525.90s, 49.23s)
Narration: Do not confuse a quadrant with a tool or an owner. The same browser framework might automate an acceptance example supporting development or collect evidence for a technical experiment. A developer can participate in exploratory testing, and a tester can help design low-level checks. Ask what question the activity answers and when its feedback is useful. For a new payment feature, list the risks first, choose activities second and use the matrix third to inspect balance. If an activity crosses a boundary, describe its purpose clearly and move on. The useful outcome is a better plan, not a perfectly categorized spreadsheet with unresolved customer risks.
Visual direction: Checkout & delivery
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

## chapter-11 — Recap (575.13s, 24.87s)
Narration: Use the quadrants to balance business and technical risks. Knowledge check: which quadrant addresses response times during a traffic spike? Subscribe to Tech at sixty for the next episode in this Agile Testing Masterclass. Practice the example with synthetic data, and share the most important risk you identified in the comments.
Visual direction: Quadrant summary.
On-screen example: Checkout & delivery; steps: Q1: unit & component | Q2: acceptance examples | Q3 + Q4: critique product; checks: Q1 • Calculation | Q2 • Business rule | Q3 • Usability | Q4 • Load
Motion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: Four perspectives, complementary evidence.

