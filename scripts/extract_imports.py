import json
import ast
import sys
import re


def extract_packages(nb_path):
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    pkgs = set()
    for cell in nb.get('cells', []):
        # Handle both old and new nbformat where code cells may be under 'cell_type' or 'cell_type'
        if cell.get('cell_type') != 'code':
            continue
        src_list = cell.get('source') or cell.get('input') or []
        if isinstance(src_list, list):
            src = ''.join(src_list)
        else:
            src = str(src_list)

        try:
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        pkgs.add(n.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        pkgs.add(node.module.split('.')[0])
        except Exception:
            # Fallback regex (less accurate)
            for m in re.finditer(r'(?m)^[ \t]*(?:from|import)\s+([\w\.]+)', src):
                pkgs.add(m.group(1).split('.')[0])
    return sorted(pkgs)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_imports.py path/to/notebook.ipynb", file=sys.stderr)
        sys.exit(1)
    nb_path = sys.argv[1]
    pkgs = extract_packages(nb_path)
    for p in pkgs:
        print(p)
