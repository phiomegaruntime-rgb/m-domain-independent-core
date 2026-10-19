"""Load the actual adapter method without downloading any model or dependencies.

No translated reimplementation: the AST method body is compiled from the frozen
original/patched source and bound to a tiny holder with _pooling only.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import torch

ROOT = Path(__file__).resolve().parent


def load_pooling(which):
    source = (ROOT/(which+'_adapter.py')).read_text()
    tree = ast.parse(source)
    matches = [node for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef) and node.name == '_apply_pooling']
    assert len(matches) == 1
    method = matches[0]
    namespace = {'torch': torch}
    exec(compile(ast.Module(body=[method], type_ignores=[]), which+'_adapter.py', 'exec'), namespace)
    fn = namespace['_apply_pooling']
    holder = SimpleNamespace(_pooling='mean')
    return lambda h, mask, pooling=None: fn(holder, h, mask, pooling=pooling)
