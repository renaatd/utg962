import sys
from utg962 import Utg962

if len(sys.argv) not in [5, 6]:
    print(
        "Syntax: ramp <channel> <frequency> <low> <high> [<symmetry>]", file=sys.stderr
    )
    exit(1)

if len(sys.argv) == 6:
    symmetry = float(sys.argv[5])
else:
    symmetry = 50

utg = Utg962()
utg.set_ramp(
    int(sys.argv[1]),
    float(sys.argv[2]),
    float(sys.argv[3]),
    float(sys.argv[4]),
    symmetry,
)
