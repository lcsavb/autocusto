import ast
import os

class VariableLister(ast.NodeVisitor):

    def __init__(self):
        self.variables = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
        self.generic_visit(node)

def list_variables_in_file(filename):
    with open(filename, 'r') as f:
        node = ast.parse(f.read())
        visitor = VariableLister()
        visitor.visit(node)
        return visitor.variables

def list_variables_in_directory(directory_path):
    all_variables = set()

    # Percorre todos os arquivos no diretório
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                all_variables.update(list_variables_in_file(file_path))

    return all_variables


print(list_variables_in_directory('.'))
