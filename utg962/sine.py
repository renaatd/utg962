import sys
from utg962 import Utg962

if len(sys.argv) != 5:
    print("Syntax: sine <channel> <frequency> <low> <high>", file=sys.stderr)
    exit(1)

utg = Utg962()
utg.set_sine(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
