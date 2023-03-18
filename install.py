from sys import executable
from subprocess import check_call

dependencies = [
    'pygame'
]

if __name__ == "__main__":
    for dependency in dependencies:
        check_call([executable, '-m', 'pip', 'install', dependency])
