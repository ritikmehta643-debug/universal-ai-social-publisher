import unittest
import sys
from pathlib import Path

def run_all_tests():
    test_dir = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(test_dir), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    print("\n✅ All Universal AI Publisher backend tests passed successfully!")

if __name__ == "__main__":
    run_all_tests()
