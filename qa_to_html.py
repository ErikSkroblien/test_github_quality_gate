import os
import glob
import json
import re
from datetime import datetime

OUTPUT_DIR = "docs"
HTML_FILE = os.path.join(OUTPUT_DIR, "qa_summary.html")
JSON_FILE = os.path.join(OUTPUT_DIR, "qa_summary.json")

INVALID_EVIDENCE = ["", "-", "tbd", "TBD", "none"]


def collect_files():
    return glob.glob("**/qa_*.md", recursive=True)


def analyze(file):

    questions = 0
    open_questions = 0

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:

        line = line.strip()

        if line.startswith("Answer:"):
            questions += 1
            answer = line.split(":")[1].strip()

        if line.startswith("Evidence:"):
            evidence = line.split("Evidence:")[1].strip()

            if evidence in INVALID_EVIDENCE or answer == "NO":
                open_questions += 1

    return questions, open_questions


def load_previous():

    if not os.path.exists(JSON_FILE):
        return None

    with open(JSON_FILE) as f:
        return json.load(f)


def save_json(report):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(JSON_FILE, "w") as f:
        json.dump(report, f, indent=2)


def create_html(report, previous):

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

body {{
font-family: Arial;
margin:40px;
}}

table {{
border-collapse: collapse;
width:70%;
}}

th {{
background:#2c3e50;
color:white;
padding:10px;
}}

td {{
padding:8px;
border-bottom:1px solid #ddd;
}}

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


def main():

    files = collect_files()

    modules = []

    for file in files:

        q, open_q = analyze(file)

        modules.append(
            {
                "file": os.path.basename(file),
                "questions": q,
                "open": open_q,
            }
        )

    report = {
        "time": datetime.utcnow().isoformat(),
        "modules": modules,
        "pr": os.getenv("PR_NUMBER", "local"),
        "author": os.getenv("PR_AUTHOR", "unknown"),
        "commit": os.getenv("GITHUB_SHA", "local"),
    }

    previous = load_previous()

    save_json(report)

    create_html(report, previous)


if __name__ == "__main__":
    main()