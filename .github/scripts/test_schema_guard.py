import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

import schema_guard


def tree(root, body):
    path = pathlib.Path(root, "frameworks", "symfony", "7.yaml")
    path.parent.mkdir(parents=True)
    path.write_text(body)


class RemovedKeyTest(unittest.TestCase):
    def guard(self, published, candidate):
        with tempfile.TemporaryDirectory() as old, tempfile.TemporaryDirectory() as new:
            tree(old, published)
            tree(new, candidate)
            sys.argv = ["schema_guard.py", old, new]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = schema_guard.main()
            return code, out.getvalue()

    def test_dropping_the_php_cap_passes(self):
        code, out = self.guard('php:\n  min: "8.2"\n  max: "8.4"\n', 'php:\n  min: "8.2"\n')
        self.assertEqual(code, 0, out)

    def test_dropping_another_key_still_fails(self):
        code, out = self.guard('php:\n  min: "8.2"\n  max: "8.4"\n', 'php:\n  max: "8.4"\n')
        self.assertEqual(code, 1)
        self.assertIn("`php.min` was removed", out)


if __name__ == "__main__":
    unittest.main()
