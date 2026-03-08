# Software Quality Checklist (Automotive)

## Instructions
Every question must contain:
- Answer: YES or NO
- Evidence: link, commit, document, or explanation

If evidence is missing the PR will fail.

---

## 1. Requirements Traceability

**Q1:** Are all requirements traced to implementation?

Answer: YES

Evidence: Jira ticket SYS-1423 linking requirement to module.

---

## 2. Static Analysis

**Q2:** Has static analysis been executed?

Answer: YES

Evidence: SonarQube report: https://sonarqube.company/report/1234

---

## 3. Unit Tests

**Q3:** Are unit tests implemented for new logic?

Answer: YES

Evidence: Test file `test_brake_controller.cpp`

Coverage report: 87%

---

## 4. MISRA Compliance

**Q4:** Is the code compliant with MISRA rules?

Answer: YES

Evidence: Polyspace report attached to CI pipeline

---

## 5. Safety Impact

**Q5:** Does the change affect safety related functionality?

Answer: NO

Evidence: Module classified ASIL-A and unaffected.

---

## 6. Code Review

**Q6:** Has the code been reviewed by another developer?

Answer: YES

Evidence: GitHub review by @reviewername

---

## Finding

**Observation:** Describe any findings or observations here.

**Impact:** Describe the impact of the findings here.

**Recommendation:** Provide recommendations to address the findings.