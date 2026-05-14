import sys
sys.path.insert(0, "/content/ai-code-quality-evaluator")
from evaluator import evaluate_code

def test_syntax_error_returns_zero_score():
    result = evaluate_code("def foo(: pass")
    assert result["score"] == 0

def test_clean_code_passes():
    clean = '''
def add(first_number, second_number):
    """Return the sum of two numbers."""
    return first_number + second_number
'''
    result = evaluate_code(clean)
    assert result["score"] >= 85

def test_bare_except_penalized():
    code = '''
def risky():
    try:
        pass
    except:
        pass
'''
    result = evaluate_code(code)
    severities = [i["severity"] for i in result["issues"]]
    assert "WARNING" in severities

def test_score_never_negative():
    terrible = '''
def f(a,b,c,d,e):
    try:
        pass
    except:
        pass
'''
    result = evaluate_code(terrible)
    assert result["score"] >= 0
