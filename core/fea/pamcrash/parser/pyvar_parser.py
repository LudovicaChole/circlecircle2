"""Numeric PYVAR assignments only; never execute embedded Python."""
import ast
import math
import operator
from core.fea.model.lsdyna.parameter import Parameter
from core.fea.parser import Parser


class PyvarParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('2020', '2023'), self._2020)

    def _2020(self, line_raw):
        if line_raw[:8].strip().endswith('/') or line_raw.startswith('NAME'):
            return
        if not line_raw.strip():
            return
        tree = ast.parse(line_raw.strip(), mode='exec')
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign):
            raise ValueError('PYVAR supports numeric assignments only')
        statement = tree.body[0]
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
            raise ValueError('PYVAR requires one variable name')
        def evaluate(node):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.Name):
                return self.dataframe.parameter[node.id].value
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                return evaluate(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
            operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                          ast.Div: operator.truediv}
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                return operations[type(node.op)](evaluate(node.left), evaluate(node.right))
            raise ValueError('PYVAR: unsupported numeric expression')
        result = evaluate(statement.value)
        if not math.isfinite(result):
            raise ValueError('PYVAR: nonfinite result')
        name = statement.targets[0].id
        self.dataframe.parameter[name] = Parameter('I' if type(result) is int else 'R', name, result)
