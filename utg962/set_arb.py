import sys
from utg962 import Utg962

if len(sys.argv) != 6:
    print("Syntax: set_arb <channel> <index> <frequency> <low> <high>", file=sys.stderr)
    exit(1)

utg = Utg962()
utg.set_arb(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
