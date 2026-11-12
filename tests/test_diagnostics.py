import unittest
from bugox import diagnose, redact_secrets


class DiagnosticTests(unittest.TestCase):
    def test_undefined_python_name(self):
        result = diagnose("File 'x.py', line 3\nNameError: name 'total' is not defined")
        self.assertEqual(result.category, "NameError")
        self.assertEqual(result.line_number, 3)

    def test_missing_dependency(self):
        self.assertEqual(diagnose("ModuleNotFoundError: No module named 'x'").category, "ModuleNotFoundError")

    def test_indentation(self):
        self.assertEqual(diagnose("IndentationError: unexpected indent").category, "IndentationError")

    def test_missing_key(self):
        self.assertEqual(diagnose("KeyError: 'user_id'").category, "KeyError")

    def test_javascript_reference(self):
        self.assertEqual(diagnose("ReferenceError: value is not defined\n at app.js:12:4").line_number, 12)

    def test_js_property_type_error(self):
        result = diagnose("TypeError: Cannot read properties of undefined (reading 'name')")
        self.assertEqual(result.category, "TypeErrorJS")

    def test_unknown_error_does_not_hallucinate(self):
        self.assertEqual(diagnose("Unusual service response").confidence, "unclassified")

    def test_empty_and_oversized(self):
        for input_text in ("", " ", "x" * 32769):
            with self.assertRaises(ValueError):
                diagnose(input_text)

    def test_token_redaction(self):
        text = "Authorization: Bearer SECRETSTRING\nNameError: name 'oops' is not defined"
        result = diagnose(text)
        self.assertNotIn("SECRETSTRING", result.matched_line)
        self.assertIn("[REDACTED]", redact_secrets(text))

    def test_sample_does_not_execute_code(self):
        result = diagnose("NameError: name '__import__(\"os\")' is not defined")
        self.assertEqual(result.category, "Unknown")


if __name__ == "__main__":
    unittest.main()
