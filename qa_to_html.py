# qa_to_html.py

import os
import glob
import json
from datetime import datetime, timezone
import requests
import http.client
from urllib.parse import urlencode

# --- Config ---
OUTPUT_DIR = "docs"
HTML_FILE = os.path.join(OUTPUT_DIR, "qa_summary.html")  # Für GitHub Pages
JSON_FILE = os.path.join(OUTPUT_DIR, "qa_summary.json")
INVALID_EVIDENCE = ["", "-", "tbd", "TBD", "none"]

# --- Ordner sicherstellen ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Markdown Dateien sammeln ---
def collect_files():
    return glob.glob("**/qa_*.md", recursive=True)

# --- Datei analysieren ---
def analyze(file):
    questions = 0
    open_questions = 0
    answer = None

    with open(file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Answer:"):
                questions += 1
                answer = line.split("Answer:")[1].strip()
            elif line.startswith("Evidence:"):
                evidence = line.split("Evidence:")[1].strip()
                if evidence in INVALID_EVIDENCE or (answer and answer.upper() == "NO"):
                    open_questions += 1
    return questions, open_questions

# --- JSON speichern ---
def save_json(report):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

# --- HTML generieren ---
def create_html(report):
    rows = ""
    trend_data = []

    for module in report["modules"]:
        name = module["file"]
        q = module["questions"]
        open_q = module["open"]

        status = "PASS"
        color = "green"
        if open_q > 0:
            status = "FAIL"
            color = "red"

        rows += f"""
        <tr>
        <td>{name}</td>
        <td>{q}</td>
        <td>{open_q}</td>
        <td style="color:{color}">{status}</td>
        </tr>
        """
        trend_data.append(open_q)

    chart_data = ",".join(str(x) for x in trend_data)

    pr_info = f"""
    <p><b>PR:</b> {report['pr']}</p>
    <p><b>Author:</b> {report['author']}</p>
    <p><b>Commit:</b> {report['commit']}</p>
    <p><b>Generated:</b> {report['time']}</p>
    """

    html = f"""
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: Arial; margin:40px; }}
table {{ border-collapse: collapse; width:70%; }}
th {{ background:#2c3e50; color:white; padding:10px; }}
td {{ padding:8px; border-bottom:1px solid #ddd; }}
</style>
</head>
<body>
<h1>QA Engineering Dashboard</h1>
{pr_info}
<h2>Module Status</h2>
<table>
<tr>
<th>Module</th>
<th>Questions</th>
<th>Open</th>
<th>Status</th>
</tr>
{rows}
</table>

<h2>Open Questions Trend</h2>
<canvas id="trendChart"></canvas>
<script>
const ctx = document.getElementById('trendChart');
new Chart(ctx, {{
type: 'bar',
data: {{
labels: [{",".join([f'"{m["file"]}"' for m in report["modules"]])}],
datasets: [{{
label: 'Open Questions',
data: [{chart_data}],
backgroundColor: 'rgba(255,99,132,0.6)'
}}]
}}
}});
</script>

</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def read_jira_config():
    with open("jira_config.yaml", "r", encoding="utf-8") as f:
        import yaml
        return yaml.safe_load(f)

# --- Jira Konfiguration ---
JIRA_HOST = "rb-tracker.bosch.com"
JIRA_BASE_PATH = "/tracker08-q"
JIRA_CREATE_ISSUE_ENDPOINT = f"{JIRA_BASE_PATH}/rest/api/2/issue/"

# --- Standard Header für Jira API ---
def get_jira_headers():
    token = os.getenv("JIRA_TOKEN")
    if not token:
        raise ValueError("JIRA_TOKEN environment variable is not set.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Python Script using http.client"
    }

# --- HTTP-Anfrage an Jira API ---
def execute_jira_request(method, path, headers, body=None):
    conn = None
    try:
        conn = http.client.HTTPSConnection(JIRA_HOST)
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        response_body = response.read().decode("utf-8")

        if response.status >= 400:
            raise http.client.HTTPException(f"HTTP {response.status}: {response.reason}\n{response_body}")

        return json.loads(response_body) if response_body else {}
    except Exception as e:
        print(f"❌ Fehler bei der Jira-Anfrage: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Jira Ticket erstellen ---
def create_jira_ticket(config, finding, file_name):
    headers = get_jira_headers()
    payload = {
        "fields": {
            "project": {"key": "TRIM"},
            "summary": f"Problem in {file_name}: {finding['Observation']}",
            "description": f"**Impact:** {finding['Impact']}\n\n**Recommendation:** {finding['Recommendation']}",
            "issuetype": {"name": "Bug"},
            "duedate": config['jira']['create_problem_ticket']['additional_fields']['due_date'],
            "customfield_26728": config['jira']['create_problem_ticket']['additional_fields']['cf[26728]'],
            "customfield_26726": config['jira']['create_problem_ticket']['additional_fields']['cf[26726]'],
            "customfield_31220": config['jira']['create_problem_ticket']['additional_fields']['cf[31220]'],
            "customfield_33921": config['jira']['create_problem_ticket']['additional_fields']['cf[33921]'],
        }
    }

    response = execute_jira_request("POST", JIRA_CREATE_ISSUE_ENDPOINT, headers, body=json.dumps(payload))
    if response and response.get('key'):
        print(f"✅ Jira-Ticket erstellt: {response.get('key')}")
    else:
        error_message = response.get('errorMessages', 'Unbekannter Fehler') if response else 'Keine Antwort vom Server'
        print(f"❌ Fehler beim Erstellen des Jira-Tickets für {file_name}: {finding['Observation']}")
        print(f"Fehlermeldung: {error_message}")

def extract_findings(file):
    findings = []
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        in_finding_section = False
        finding = {}
        for line in lines:
            line = line.strip()
            if line.startswith("## Finding"):
                in_finding_section = True
            elif in_finding_section:
                if line.startswith("**Observation:**"):
                    finding['Observation'] = line.split("**Observation:**")[-1].strip()
                elif line.startswith("**Impact:**"):
                    finding['Impact'] = line.split("**Impact:**")[-1].strip()
                elif line.startswith("**Recommendation:**"):
                    finding['Recommendation'] = line.split("**Recommendation:**")[-1].strip()
                    findings.append(finding)
                    finding = {}
    return findings

# --- Main ---
def main():
    files = collect_files()
    if not files:
        print("⚠️ Keine qa_*.md Dateien gefunden. Dashboard wird trotzdem erstellt.")

    modules = []
    config = read_jira_config()

    for file in files:
        q, open_q = analyze(file)
        modules.append({"file": os.path.basename(file), "questions": q, "open": open_q})

        findings = extract_findings(file)
        for finding in findings:
            create_jira_ticket(config, finding, os.path.basename(file))

    report = {
        "time": datetime.now(timezone.utc).isoformat(),
        "modules": modules,
        "pr": os.getenv("PR_NUMBER", "local"),
        "author": os.getenv("PR_AUTHOR", "unknown"),
        "commit": os.getenv("GITHUB_SHA", "local"),
    }

    save_json(report)
    create_html(report)
    print(f"✅ QA Dashboard erzeugt: {HTML_FILE}")
    print(f"✅ JSON Report erzeugt: {JSON_FILE}")

if __name__ == "__main__":
    main()