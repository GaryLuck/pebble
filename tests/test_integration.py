import unittest
import subprocess
import os
import sys

class TestIntegration(unittest.TestCase):
    def run_pebble(self, filename):
        # We assume tests are run from repo root or tests dir.
        # Let's find pebble.py relative to this file.
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pebble_cli = os.path.join(base_dir, 'pebble.py')
        filepath = os.path.join(base_dir, 'tests', 'integration', filename)

        env = os.environ.copy()
        env['PYTHONPATH'] = base_dir # Ensure pebble package is found

        result = subprocess.run(
            [sys.executable, pebble_cli, filepath],
            capture_output=True,
            text=True,
            env=env
        )
        return result

    def test_fib(self):
        res = self.run_pebble('fib.pebble')
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertEqual(res.stdout.strip(), "55")

    def test_strings(self):
        res = self.run_pebble('strings.pebble')
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertEqual(res.stdout.strip(), "hello world")

    def test_arrays(self):
        res = self.run_pebble('arrays.pebble')
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertEqual(res.stdout.strip(), "60")

if __name__ == '__main__':
    unittest.main()
