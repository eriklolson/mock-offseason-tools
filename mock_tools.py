# Scaffold

# #!/usr/bin/env python3
# import importlib
# import sys

# AVAILABLE_MODULES = {
#     "chatgpt_sync": "chatgpt_sync.main",
#     "jira_sync": "jira_sync.main",
# }

# def list_modules():
#     print("Available modules:")
#     for i, key in enumerate(AVAILABLE_MODULES, start=1):
#         print(f"[{i}] {key}")

# def choose_interactively():
#     list_modules()
#     choice = input("Select a module to run: ").strip()
#     try:
#         index = int(choice) - 1
#         module_key = list(AVAILABLE_MODULES.keys())[index]
#     except (ValueError, IndexError):
#         print("❌ Invalid selection.")
#         sys.exit(1)
#     return module_key

# def run_module(name):
#     module_path = AVAILABLE_MODULES.get(name)
#     if not module_path:
#         print(f"❌ Unknown module: {name}")
#         list_modules()
#         sys.exit(1)
#     try:
#         mod = importlib.import_module(module_path)
#         if hasattr(mod, "main"):
#             mod.main()
#         else:
#             print(f"❌ Module '{name}' does not have a main() function.")
#     except Exception as e:
#         print(f"❌ Failed to run module '{name}': {e}")
#         raise

# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         selected = sys.argv[1]
#     else:
#         selected = choose_interactively()
#     run_module(selected)
