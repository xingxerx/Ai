import pathlib
import importlib
import traceback
import sys
import ast
import inspect
import asyncio

# Base directory of scripts (repo root where this file resides)
BASE_DIR = pathlib.Path(__file__).resolve().parent


def script_has_main(path: pathlib.Path) -> bool:
    """Return True if the module defines a top-level `main` function (sync or async)."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main":
                return True
    except Exception:
        pass
    return False


# Find .py files that define a main() function; exclude this launcher and modules with side effects or interactivity
EXCLUDE = {"main", "setup", "example"}
scripts = sorted(
    f.stem for f in BASE_DIR.glob("*.py")
    if f.stem not in EXCLUDE and script_has_main(f)
)

results = []

for name in scripts:
    try:
        print(f"\n▶ Running {name}...")
        mod = importlib.import_module(name)
        if hasattr(mod, "main") and callable(mod.main):
            if inspect.iscoroutinefunction(mod.main):
                asyncio.run(mod.main())
            else:
                ret = mod.main()
                # Support functions that return a coroutine
                if inspect.iscoroutine(ret):
                    asyncio.run(ret)
        results.append((name, "✅ Success"))
    except Exception as e:
        print(f"❌ Error in {name}: {e}")
        traceback.print_exc()
        results.append((name, f"❌ Failed: {type(e).__name__}"))

print("\n===== EXECUTION REPORT =====")
for script, status in results:
    print(f"{script}: {status}")

if any("❌" in s for _, s in results):
    sys.exit(1)