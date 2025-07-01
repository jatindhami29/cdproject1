import os
from fpdf import FPDF

def generate_report_text(file_path, issues):
    if not issues:
        return f"Static Analysis Report for: {file_path}\nNo issues found.\n"

    report_lines = [f"Static Analysis Report for: {file_path}", "=" * 50, ""]
    for issue in sorted(issues, key=lambda x: x['line']):
        report_lines.append(f"Line {issue['line']}: [{issue['type']}]")
        report_lines.append(f"Message: {issue['message']}")
        report_lines.append(f"Suggestion: {issue['suggestion']}")
        report_lines.append("-" * 50)
    return "\n".join(report_lines)

def save_report(report_text, original_file_path):
    report_path = os.path.splitext(original_file_path)[0] + "_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    return report_path

def save_pdf_report(report_text, original_file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in report_text.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)
    pdf_path = os.path.splitext(original_file_path)[0] + "_report.pdf"
    pdf.output(pdf_path)
    return pdf_path
