# QA Checklist Example

## Instructions
- Jede Frage muss beantwortet werden mit `Answer: YES` oder `Answer: NO`
- Evidence muss **nicht leer** sein (kein "-", "TBD", etc.)
- Coverage ≥ 80%, falls angegeben
- Jira Ticket, falls referenziert, muss korrekt formatiert sein

---

## 1. Requirements Traceability

**Q1:** Sind alle Anforderungen nachvollziehbar umgesetzt?

Answer: YES  
Evidence: Jira SYS-1423 verlinkt Requirement zum Modul

---

## 2. Static Analysis

**Q2:** Wurde statische Codeanalyse durchgeführt?

Answer: YES  
Evidence: SonarQube Bericht: https://sonarqube.company.com/report/1234

---

## 3. Unit Tests

**Q3:** Wurden Unit Tests für neue Logik implementiert?

Answer: YES  
Evidence: `test_brake_controller.cpp` enthält Tests  
Coverage: 87%

---

## 4. MISRA Compliance

**Q4:** Ist der Code MISRA-konform?

Answer: YES  
Evidence: Polyspace Bericht angehängt in CI Pipeline

---

## 5. Safety Impact

**Q5:** Hat die Änderung sicherheitsrelevante Funktionen beeinflusst?

Answer: NO  
Evidence: Modul ASIL-A klassifiziert, nicht betroffen

---

## 6. Code Review

**Q6:** Wurde der Code von einem anderen Entwickler geprüft?

Answer: YES  
Evidence: GitHub Review durch @reviewername

---

## 7. Jira Ticket Referenz

**Q7:** Ist ein Jira Ticket zu dieser Änderung vorhanden?

Answer: YES  
Evidence: Jira SYS-1423