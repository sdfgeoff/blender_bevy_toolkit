import pytest
import sys

res = pytest.main([])

if res == pytest.ExitCode.OK:
    sys.exit(0)