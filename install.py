from sys import executable
from subprocess import check_call

dependencies = [
    'pygame',
    'python-decouple',
    'neat-python',
    'dill',
    'graphviz',
    'matplotlib'
]

if __name__ == "__main__":
    check_call([executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    for dependency in dependencies:
        check_call([executable, '-m', 'pip', 'install', dependency])
