import sys
from utg962 import Utg962

if len(sys.argv) not in [5, 6]:
    print("Syntax: square <channel> <frequency> <low> <high> [<duty>]", file=sys.stderr)
    exit(1)

if len(sys.argv) == 6:
    duty_cycle = float(sys.argv[5])
else:
    duty_cycle = 50

utg = Utg962()
utg.set_square(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), duty_cycle)
