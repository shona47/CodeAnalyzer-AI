import unittest
import sys
import os
import time

# Ensure we can import analyzer
sys.path.append(os.getcwd())
import analyzer

class TestAnalyzer(unittest.TestCase):

    def test_python_valid(self):
        code = "print('Hello, AI')"
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'success')
        self.assertIn('Hello, AI', result['output'])
        self.assertEqual(len(result['errors']), 0)
        self.assertIn('metadata', result)

    def test_python_syntax_error(self):
        code = "print('forgot closing paren"
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_SYNTAX)
        self.assertEqual(result['errors'][0]['type'], 'SyntaxError')

    def test_python_runtime_error_div_zero(self):
        code = "x = 1 / 0"
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_RUNTIME)
        self.assertEqual(result['errors'][0]['type'], 'ZeroDivisionError')

    def test_python_security_import(self):
        code = "import os\nos.system('echo hack')"
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_SECURITY)
        self.assertIn('forbidden pattern', result['errors'][0]['message'])

    def test_python_security_eval(self):
        code = "eval('print(1)')"
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_SECURITY)

    def test_python_timeout(self):
        code = "while True: pass"
        start = time.time()
        result = analyzer.analyze_code(code, 'python')
        duration = time.time() - start
        
        # It should take at least 2 seconds (timeout) but not indefinitely
        self.assertTrue(duration >= 2.0)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_RUNTIME)
        self.assertEqual(result['errors'][0]['type'], 'TimeoutError')

    def test_c_valid(self):
        if not shutil.which("gcc"):
            print("Skipping C tests: GCC not found")
            return
        code = "#include <stdio.h>\nint main() { printf(\"Hello C\"); return 0; }"
        result = analyzer.analyze_code(code, 'c')
        self.assertEqual(result['status'], 'success')
        self.assertIn('Hello C', result['output'])

    def test_c_compilation_error(self):
        if not shutil.which("gcc"): return
        code = "int main() { return 0 " # Missing brace and semi
        result = analyzer.analyze_code(code, 'c')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['category'], analyzer.CAT_COMPILATION)

    def test_code_length_limit(self):
        code = "print('a')" * 200 # 200 * 10 = 2000 chars > 1000
        result = analyzer.analyze_code(code, 'python')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['errors'][0]['type'], 'CodeLengthExceeded')

if __name__ == '__main__':
    import shutil # Check for C tests
    unittest.main()
