import sys
from pathlib import Path

# make tools/demo.py importable as `tools_demo` for the end-to-end tests
TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("tools_demo", TOOLS / "demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sys.modules["tools_demo"] = mod
