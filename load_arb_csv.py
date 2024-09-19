import sys
from utg962 import Utg962

if len(sys.argv) != 5:
    print(
        "Syntax: utg_load_arb <channel> <index> <ARB name> <filename>\n\n"
        "This script loads an arbitrary waveform from a CSV file into the UTG962. The\n"
        "CSV file should contain a single column of data points in the range -1.0...+1.0.\n"
        "Up to 4000 data points are supported.\n\n"
        "channel: output channel (1 or 2)\n"
        "index: position of ARB in memory (0 or 1)\n"
        "ARB name: name of the ARB in memory\n"
        "filename: path to the CSV file\n",
        file=sys.stderr,
    )
    exit(1)

utg = Utg962()
utg.load_arb_from_file(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4])
