from analyzer_core import analyze_java_code
from report_utils import generate_report_text, save_report, save_pdf_report

def main():
    file_path = input("Enter Java file path: ").strip()
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    issues = analyze_java_code(code, file_path)
    report = generate_report_text(file_path, issues)
    print(report)
    save_report(report, file_path)

if __name__ == "__main__":
    main()
