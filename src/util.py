import os
import glob


def test_on(test, path='../primjeri'):
    for filename in glob.glob(os.path.join(path, '*.txt')):
        if filename.startswith('_'):
            continue
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            print(f"========= {filename} =========")
            test(f.read())
            print()
            print()


def get_test_dir():
    import sys
    if len(sys.argv) > 1:
        return '../' + sys.argv[1]
    else:
        return '../primjeri'
