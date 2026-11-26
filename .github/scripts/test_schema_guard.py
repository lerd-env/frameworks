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

    def test_dropping_the_create_command_passes(self):
        code, out = self.guard('create: composer create-project x/y\nname: lumen\n', 'name: lumen\n')
        self.assertEqual(code, 0, out)

    def test_dropping_another_key_still_fails(self):
        code, out = self.guard('php:\n  min: "8.2"\n  max: "8.4"\n', 'php:\n  max: "8.4"\n')
        self.assertEqual(code, 1)
        self.assertIn("`php.min` was removed", out)


class StarterIndexTest(unittest.TestCase):
    ENTRY = '{"name": "filament", "label": "Filament", "framework": {"name": "laravel", "min": "11"}}'

    def failures(self, entry, body):
        with tempfile.TemporaryDirectory() as root:
            index = pathlib.Path(root, "frameworks", "index.json")
            index.parent.mkdir(parents=True)
            index.write_text('{"frameworks": [], "starters": [' + entry + ']}')
            if body is not None:
                path = pathlib.Path(root, "starters", "laravel", "filament.yaml")
                path.parent.mkdir(parents=True)
                path.write_text(body)
            return schema_guard.index_failures(root)

    def test_an_entry_matching_its_file_passes(self):
        body = 'starter: filament\nlabel: Filament\nframework:\n  name: laravel\n  min: "11"\nrequire:\n  - filament/filament\n'
        self.assertEqual(self.failures(self.ENTRY, body), [])

    def test_an_entry_without_a_file_fails(self):
        out = self.failures(self.ENTRY, None)
        self.assertEqual(len(out), 1)
        self.assertIn("starters/laravel/filament.yaml", out[0])

    def test_an_entry_disagreeing_with_its_file_fails(self):
        body = 'starter: filament\nlabel: Filament\nframework:\n  name: laravel\n  min: "12"\nrequire:\n  - filament/filament\n'
        out = self.failures(self.ENTRY, body)
        self.assertEqual(len(out), 1)
        self.assertIn("framework", out[0])


if __name__ == "__main__":
    unittest.main()
