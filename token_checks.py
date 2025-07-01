#part of fallback mechanism  - includes line-based and character-level checks  
def find_additional_issues_from_tokens(tokens, java_code):
    issues = []
    lines = java_code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if (stripped.endswith('}') or stripped.endswith('{') or
            stripped.endswith(';') or not stripped or
            stripped.startswith('//') or stripped.startswith('*')):
            continue
        if not line.rstrip().endswith(';'):
            issues.append({
                'line': i,
                'type': 'Syntax Error',
                'message': "Missing semicolon",
                'suggestion': "Add semicolon at end of statement"
            })
    return issues

def find_missing_brackets(java_code):
    issues = []
    stack = []
    lines = java_code.split('\n')

    for line_num, line in enumerate(lines, 1):
        for char in line:
            if char == '{':
                stack.append(('{', line_num))
            elif char == '}':
                if not stack or stack[-1][0] != '{':
                    issues.append({
                        'line': line_num,
                        'type': 'Missing Bracket',
                        'message': "Unmatched closing brace '}'",
                        'suggestion': 'Add corresponding opening brace or remove this closing brace'
                    })
                else:
                    stack.pop()

    for brace, line_num in stack:
        issues.append({
            'line': line_num,
            'type': 'Missing Bracket',
            'message': f"Unmatched opening brace '{brace}'",
            'suggestion': 'Add corresponding closing brace'
        })
    return issues
