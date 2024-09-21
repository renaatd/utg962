# utg962

utg962 is a simple Python module to control some features of a UNI-T UTG962E
- reset device
- output sine/square waves
- upload and output an arbitrary waveform from a text file
- capture the display

## Dependencies
- PyVISA
- Pillow
- a VISA backend supported by PyVISA, e.g. PyVISA-py or NI-VISA

## Examples
Channel 2: output a sine wave, 10 kHz, amplitude 5V
```
python sine.py 2 10000 -5 5
```

Load the staircase waveform from stair.txt in memory slot #0
```
python load_arb.py 1 0 staircase stair.txt
```

Channel 1: set this staircase waveform, 1 kHz, from 1V to 5V
```
python set_arb.py 1 0 1000 1 5
```

## See also
- Jarjuk's [UTG900](https://github.com/jarjuk/UTG900) and [ebench](https://github.com/jarjuk/ebench)