import os
import tempfile
from qa_to_html import collect_qa_markdowns, generate_html

def test_collect_qa_markdowns():
    with tempfile.TemporaryDirectory() as tmpdir:
        # QA Dateien erstellen
        file1 = os.path.join(tmpdir, "qa_test1.md")
        file2 = os.path.join(tmpdir, "qa_test2.md")
        with open(file1, "w") as f:
            f.write("Answer: YES\nEvidence: test1")
        with open(file2, "w") as f:
            f.write("Answer: NO\nEvidence: test2")

        files = collect_qa_markdowns(tmpdir)
        assert len(files) == 2
        assert file1 in files
        assert file2 in files

def test_generate_html_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "qa_test1.md")
        with open(file1, "w") as f:
            f.write("Answer: YES\nEvidence: test1")
        output_html = os.path.join(tmpdir, "summary.html")
        generate_html([file1], output_file=output_html)
        assert os.path.exists(output_html)
        with open(output_html) as f:
            content = f.read()
        assert "QA Checklist Summary" in content
        assert "qa_test1.md" in content
        assert "Answer: YES" in content