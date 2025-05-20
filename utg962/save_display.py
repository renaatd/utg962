import sys
from utg962 import Utg962

if len(sys.argv) != 2:
    print(
        "Syntax: save_display <filename>\n"
        "This script saves the display of the UTG962 to a file. Supported formats are BMP, PNG, TIFF and other formats supported by PIL.",
        file=sys.stderr,
    )
    exit(1)

utg = Utg962()
utg.save_display(sys.argv[1])
