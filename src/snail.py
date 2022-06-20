from vepar import *
import sys
import snailparser
import os

import util
import lekser


def justread(filename):
    filename = os.path.realpath(filename)
    with open(filename, 'r') as f:
        return f.read()


def preprocess_rek(filename, imported):
    directory = os.path.dirname(os.path.realpath(filename))
    filename = os.path.realpath(filename)
    # print(filename)
    imported.append(filename)
    with open(filename, 'r') as f:
        src = f.read()
        lines = []
        for line in src.splitlines():
            if line.startswith("import"):
                import_filename = line.split("import ")[1]
                import_filename = import_filename.split('"')[1]
                import_filename = directory + '/' + import_filename
                import_filename = os.path.realpath(import_filename)

                if import_filename not in imported:
                    other_preprocessed = preprocess_rek(
                        import_filename, imported)
                    lines.extend(other_preprocessed)
            else:
                lines.append(line)
        return lines


def preprocess(filename):
    lines = preprocess_rek(filename, [])
    return "\n".join(lines)


def main(*sysargs):
    filename = os.path.realpath(sysargs[0])
    # print('=== preprocessing ===')
    src = preprocess(filename)
    # src = justread(filename)
    program = snailparser.P(src)

    print('=== typechecking ===')
    rows = program.typecheck(filename)
    for ime, tip in rows:
        tip = util.token_str(tip)
        print(f'{ime.sadržaj}:  {tip}')
    print()

    print('=== pokretanje ===')
    program.izvrši(filename)


if __name__ == "__main__":
    main(sys.argv[1])
