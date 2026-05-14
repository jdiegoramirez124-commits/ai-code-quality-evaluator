import ast
import subprocess
import tempfile
import os
import re


def evaluate_code(code: str, language: str = "python") -> dict:
    """Analyze Python code and return a structured quality report."""
    results = {
        "language": language,
        "lines_of_code": 0,
        "issues": [],
        "metrics": {},
        "score": 100,
        "verdict": ""
    }
    lines = [l for l in code.strip().splitlines() if l.strip()]
    results["lines_of_code"] = len(lines)

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        results["issues"].append({"severity": "CRITICAL", "message": f"Syntax error: {e}"})
        results["score"] = 0
        results["verdict"] = "CRITICAL — code does not compile"
        return results

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    result = subprocess.run(["python", "-m", "pyflakes", tmp_path], capture_output=True, text=True)
    os.unlink(tmp_path)
    for line in result.stdout.splitlines():
        clean = re.sub(r".+:\d+:\d*\s*", "", line).strip()
        if clean:
            results["issues"].append({"severity": "WARNING", "message": clean})
            results["score"] -= 10

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and len(node.id) == 1 and node.id not in "ijkxyn":
            results["issues"].append({"severity": "INFO", "message": f"Variable name too short: '{node.id}'"})
            results["score"] -= 3
        if isinstance(node, ast.FunctionDef):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                results["issues"].append({"severity": "INFO", "message": f"Function '{node.name}' has no docstring"})
                results["score"] -= 5
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            results["issues"].append({"severity": "WARNING", "message": "Bare 'except:' used — catch specific exceptions"})
            results["score"] -= 8
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                results["issues"].append({"severity": "INFO", "message": "print() found — consider using logging instead"})
                results["score"] -= 2

    result2 = subprocess.run(["python", "-m", "radon", "cc", "-s", "-"], input=code, capture_output=True, text=True)
    for l in result2.stdout.strip().splitlines():
        match = re.search(r'\((\d+)\)', l)
        if match:
            c = int(match.group(1))
            if c > 10:
                results["issues"].append({"severity": "WARNING", "message": f"High cyclomatic complexity ({c})"})
                results["score"] -= 8
            elif c > 5:
                results["issues"].append({"severity": "INFO", "message": f"Moderate complexity ({c})"})
                results["score"] -= 3

    results["score"] = max(0, results["score"])
    if results["score"] >= 85:
        results["verdict"] = "PASS — good quality code"
    elif results["score"] >= 60:
        results["verdict"] = "NEEDS REVIEW — issues found"
    else:
        results["verdict"] = "FAIL — insufficient quality"
    return results


def print_report(results: dict):
    """Print a formatted quality report to stdout."""
    print("=" * 55)
    print("   AI CODE QUALITY EVALUATOR — Report")
    print("=" * 55)
    print(f"  Language      : {results['language']}")
    print(f"  Lines of code : {results['lines_of_code']}")
    print(f"  Score         : {results['score']} / 100")
    print(f"  Verdict       : {results['verdict']}")
    if results["issues"]:
        print(f"\n  Issues found ({len(results['issues'])}):")
        print("  " + "-" * 40)
        for issue in results["issues"]:
            icon = {"CRITICAL": "[CRITICAL]", "WARNING": "[WARNING]", "INFO": "[INFO]"}.get(issue["severity"], "")
            print(f"  {icon} {issue['message']}")
    else:
        print("\n  No issues found.")
    print("=" * 55)
