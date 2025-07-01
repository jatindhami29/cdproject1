from javalang import parse, tokenizer
from javalang.tree import *
from javalang.parser import JavaSyntaxError
from collections import defaultdict

from token_checks import find_additional_issues_from_tokens, find_missing_brackets


def analyze_java_code(java_code, file_path):
    issues = []

    try:
        tree = parse.parse(java_code)
    except JavaSyntaxError as e:
        line = getattr(getattr(e, 'at', None), 'line', 4)
        issues.append({
            'line': line,
            'type': 'Syntax Error',
            'message': e.description,
            'suggestion': 'Check Java syntax rules'
        })
        
        # fallback mechanism 
        try:    
            tokens = list(tokenizer.tokenize(java_code))
            issues += find_additional_issues_from_tokens(tokens, java_code)
        except:
            pass
        issues += find_missing_brackets(java_code)
        return issues

    issues += find_unused_variables(tree)
    issues += find_undeclared_variables(tree, java_code)
    issues += find_type_mismatches(tree)
    issues += find_missing_brackets(java_code)
    issues += find_security_issues(tree)
    issues += check_method_calls(tree)

    try:
        tokens = list(tokenizer.tokenize(java_code))
        issues += find_additional_issues_from_tokens(tokens, java_code)
    except:
        pass

    return issues


def find_unused_variables(tree):
    issues = []
    variable_usage = defaultdict(lambda: {'declared': False, 'used': False, 'line': 0})

    for path, node in tree.filter(VariableDeclarator):
        var_name = node.name
        variable_usage[var_name]['declared'] = True
        variable_usage[var_name]['line'] = node.position.line if node.position else 0

    for path, node in tree.filter(MemberReference):
        if node.member in variable_usage:
            variable_usage[node.member]['used'] = True

    for var_name, usage in variable_usage.items():
        if usage['declared'] and not usage['used']:
            issues.append({
                'line': usage['line'],
                'type': 'Unused Variable',
                'message': f"Variable '{var_name}' is declared but never used",
                'suggestion': 'Remove the variable if unused or use it in your code'
            })

    return issues


def find_undeclared_variables(tree, java_code):
    issues = []
    declared_vars = set()
    lines = java_code.split('\n')

    if tree:
        for path, node in tree.filter(VariableDeclarator):
            declared_vars.add(node.name)

    for i, line in enumerate(lines, 1):
        if '=' in line and '==' not in line:
            right_side = line.split('=')[1].split(';')[0]
            words = right_side.replace('+', ' ').replace('-', ' ').replace('*', ' ').split()
            for word in words:
                if (word.isidentifier() and word not in declared_vars and
                    not word[0].isdigit() and word not in ['true', 'false', 'null']):
                    issues.append({
                        'line': i,
                        'type': 'Undeclared Variable',
                        'message': f"Variable '{word}' used but not declared",
                        'suggestion': 'Declare the variable before use'
                    })

    return issues


def find_type_mismatches(tree):
    issues = []
    for path, node in tree.filter(Assignment):
        if hasattr(node, 'expressionl') and hasattr(node, 'value'):
            left_type = get_expression_type(node.expressionl)
            right_type = get_expression_type(node.value)
            if left_type and right_type and left_type != right_type:
                line = node.position.line if node.position else 0
                issues.append({
                    'line': line,
                    'type': 'Type Mismatch',
                    'message': f"Type mismatch in assignment: {left_type} vs {right_type}",
                    'suggestion': 'Ensure both sides of the assignment have compatible types'
                })
    return issues


def get_expression_type(expr):
    if isinstance(expr, Literal):
        if '"' in expr.value:
            return 'String'
        if expr.value in ('true', 'false'):
            return 'boolean'
        if expr.value.isdigit():
            return 'int'
    elif isinstance(expr, MemberReference):
        return 'Object'
    return None


def find_security_issues(tree):
    issues = []

    for path, node in tree.filter(Literal):
        if isinstance(node.value, str) and 'password' in node.value.lower():
            line = node.position.line if node.position else 0
            issues.append({
                'line': line,
                'type': 'Security Issue',
                'message': "Potential hardcoded password detected",
                'suggestion': 'Store passwords in secure configuration or environment variables'
            })

    for path, node in tree.filter(MethodInvocation):
        if node.member.lower() in ('executequery', 'executeupdate'):
            for arg in node.arguments:
                if isinstance(arg, BinaryOperation) and arg.operator == '+':
                    line = node.position.line if node.position else 0
                    issues.append({
                        'line': line,
                        'type': 'Security Issue',
                        'message': "Potential SQL injection vulnerability",
                        'suggestion': 'Use prepared statements or parameterized queries'
                    })

    return issues


def check_method_calls(tree):
    issues = []
    method_declarations = set()

    for path, node in tree.filter(MethodDeclaration):  #Gets all defined method names.
        method_declarations.add(node.name)

    for path, node in tree.filter(MethodInvocation):     # Gets all method calls.
        if node.member not in method_declarations:
            line = node.position.line if node.position else 0
            issues.append({
                'line': line,
                'type': 'Undefined Method',
                'message': f"Method '{node.member}' is called but not defined",
                'suggestion': 'Implement the method or check for typos'
            })

    return issues
