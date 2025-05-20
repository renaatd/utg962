import sys
from utg962 import Utg962

if len(sys.argv) != 4:
    print(
        "Syntax: load_arb <index> <ARB name> <filename>\n\n"
        "This script loads an arbitrary waveform from a text file into the UTG962. The\n"
        "file must contain lines with data points in the range -1.0...+1.0.\n"
        "Up to 4000 data points are supported. Lines beginning with # are ignored.\n\n"
        "Note: the outputs might switch briefly to ARB mode during upload.\n\n"
        "index: position of ARB in memory (0 or 1)\n"
        "ARB name: name of the ARB in memory\n"
        "filename: path to the file\n",
        file=sys.stderr,
    )
    exit(1)

utg = Utg962()
utg.load_arb_from_file(int(sys.argv[1]), sys.argv[2], sys.argv[3])
