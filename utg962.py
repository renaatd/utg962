import io
import pyvisa
import struct
from PIL import Image
from typing import List


class UtgError(Exception):
    pass


class Utg962:
    # Fixed header for arbitrary waveform data. MAX/MIN are used by the UTG962
    # to scale the data. RATEPOS/RATENEG must be present and are also vertical
    # scale factors (V/LSB), but they seem to be unused.
    ARB_HEADER = (
        b"VPP:0\r\n"
        + b"OFFSET:0\r\n"
        + b"RATEPOS:0\r\n"
        + b"RATENEG:0\r\n"
        + b"MAX:32767\r\n"
        + b"MIN:-32767\r\n"
    )
    ARB_HEADER_INTRO = bytes(f"[HEAD]:{len(ARB_HEADER)}\r\n", "ascii")

    def __init__(self):
        """Connect to the first UTG962 device found."""
        rm = pyvisa.ResourceManager()
        self.inst = None
        for pattern in ["?*::0x6656::0x0834::?*", "?*::26198::2100::?*"]:
            all_utg962 = rm.list_resources(pattern)
            if len(all_utg962) != 0:
                self.inst = rm.open_resource(all_utg962[0])
                break
        if not self.inst:
            raise UtgError("No UTG962 devices found")

    def reset(self) -> None:
        """Reset the UTG962 to factory defaults."""
        self.inst.write("*RST;:SYSTEM:LOCK OFF")

    def save_display(self, filename: str) -> None:
        """Save the display of the UTG962 in a format supported by PIL, e.g. PNG/BMP/TIFF."""
        # Hide lock status, read display data, hide lock status again
        self.inst.write(":SYSTEM:LOCK OFF;:DISP?;:SYSTEM:LOCK OFF")
        data = self.inst.read_binary_values(
            datatype="B",
            is_big_endian=False,
            header_fmt="ieee",
            expect_termination=True,
        )
        # This list of bytes is a BMP file with incorrect RGB order and flipped horizontally.
        # Parse it using PIL and save it to a file after correction.
        with Image.open(io.BytesIO(bytes(data))) as img:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            r, g, b = img.split()
            img = Image.merge("RGB", (g, r, b))
            img.save(filename)

    def load_arb_from_list(
        self, arb_index: int, arb_name: str, data: List[float]
    ) -> None:
        """Load an arbitrary waveform in the UTG962 at the specified index.

        arb_index: index of the waveform in the UTG962 memory, 0 or 1
        arb_name: name of the arbitrary waveform as shown in the UTG962 display
        data: list of data points in range -1.0...+1.0. Up to 4000 data points are supported.

        Note: the channels might temporarily change mode during the upload.
        """
        self._validate_arb_index(arb_index)
        if min(data) < -1.0 or max(data) > 1.0:
            raise UtgError("Data points must be in the range -1.0...+1.0")
        data_length = len(data)
        if data_length < 1:
            raise UtgError("At least one data point required")
        if data_length > 4000:
            raise UtgError("Too many data points, max 4000 allowed")

        scaled_data = [int(32767 * x) for x in data]
        binary_data = struct.pack(f"<{data_length}h", *scaled_data)
        data_intro = bytes(f"[DATA]:{data_length}\r\n", "ascii")

        # Channels might switch to ARB when uploading a waveform via :WARB. Save the current mode.
        wav_chan1 = self.inst.query(":CHAN1:BASE:WAV?")
        wav_chan2 = self.inst.query(":CHAN2:BASE:WAV?")

        self.inst.write(f":WARB{arb_index+1}:CARRIER {arb_name}")
        self.inst.write_raw(
            self.ARB_HEADER_INTRO + self.ARB_HEADER + data_intro + binary_data
        )
        # Restore the mode for both channels. Doing this in one write seems to be unreliable.
        self.inst.write(f":CHAN1:BASE:WAV {wav_chan1}")
        self.inst.write(f":CHAN2:BASE:WAV {wav_chan2}")
        self.inst.write(":SYSTEM:LOCK OFF")

    def load_arb_from_file(self, arb_index: int, arb_name: str, filename: str) -> None:
        """Load an arbitrary waveform from a text file in the UTG962.

        arb_index: index of the waveform in the UTG962 memory, 0 or 1
        arb_name: name of the arbitrary waveform as shown in the UTG962 display
        """
        with open(filename, "r") as f:
            lines = f.readlines()
        data = [float(line.strip()) for line in lines if not line.startswith("#")]
        self.load_arb_from_list(arb_index, arb_name, data)

    def set_arb(
        self, channel: int, arb_index: int, frequency: float, low: float, high: float
    ) -> None:
        """Set a channel to an arbitrary waveform (previously loaded) and enable the output.

        arb_index: index of the waveform in the UTG962 memory, 0 or 1
        min: minimum voltage of the waveform, corresponding with -1.0
        max: maximum voltage of the waveform, corresponding with +1.0
        """
        self._validate_channel(channel)
        self._validate_arb_index(arb_index)
        self._validate_frequency(10e6, frequency)
        self.inst.write(
            f":CHAN{channel}:BASE:WAV ARB;" + f":CHAN{channel}:ARB:SOUR EXT"
        )
        if self.inst.query(f":CHAN{channel}:ARB:SOUR?")[:3] != "EXT":
            raise UtgError("Setting ARB can only after at least one waveform is loaded")
        self.inst.write(
            f":CHAN{channel}:ARB:IND {arb_index};"
            + f":CHAN{channel}:BASE:FREQ {frequency};"
            + f":CHAN{channel}:BASE:LOW {low};"
            + f":CHAN{channel}:BASE:HIGH {high};"
            + f":CHAN{channel}:OUTP ON;"
            + f":SYSTEM:LOCK OFF"
        )

    def set_ramp(
        self, channel: int, frequency: float, low: float, high: float, symmetry: float
    ) -> None:
        """Set a channel to a ramp (sawtooth) and enable the output."""
        self._validate_channel(channel)
        self._validate_frequency(400e3, frequency)
        self._validate_symmetry(symmetry)
        self.inst.write(
            f":CHAN{channel}:BASE:WAV RAMP;"
            + f":CHAN{channel}:BASE:FREQ {frequency};"
            + f":CHAN{channel}:BASE:LOW {low};"
            + f":CHAN{channel}:BASE:HIGH {high};"
            + f":CHAN{channel}:RAMP:SYMM {symmetry};"
            + f":CHAN{channel}:OUTP ON;"
            + f":SYSTEM:LOCK OFF"
        )

    def set_sine(self, channel: int, frequency: float, low: float, high: float) -> None:
        """Set a channel to a sine wave and enable the output."""
        self._validate_channel(channel)
        self._validate_frequency(60e6, frequency)
        self.inst.write(
            f":CHAN{channel}:BASE:WAV SIN;"
            + f":CHAN{channel}:BASE:FREQ {frequency};"
            + f":CHAN{channel}:BASE:LOW {low};"
            + f":CHAN{channel}:BASE:HIGH {high};"
            + f":CHAN{channel}:OUTP ON;"
            + f":SYSTEM:LOCK OFF"
        )

    def set_square(
        self,
        channel: int,
        frequency: float,
        low: float,
        high: float,
        duty_cycle: float = 50.0,
    ) -> None:
        """Set a channel to a square wave and enable the output."""
        self._validate_channel(channel)
        self._validate_frequency(20e6, frequency)
        self.inst.write(
            f":CHAN{channel}:BASE:WAV SQU;"
            + f":CHAN{channel}:BASE:FREQ {frequency};"
            + f":CHAN{channel}:BASE:LOW {low};"
            + f":CHAN{channel}:BASE:HIGH {high};"
            + f":CHAN{channel}:BASE:DUTY {duty_cycle};"
            + f":CHAN{channel}:OUTP ON;"
            + f":SYSTEM:LOCK OFF"
        )

    def set_output(self, channel: int, on: bool) -> None:
        """Enable or disable the output of a channel."""
        self._validate_channel(channel)
        state = "ON" if on else "OFF"
        self.inst.write(f":CHAN{channel}:OUTP {state};:SYSTEM:LOCK OFF")

    def _validate_arb_index(self, arb_index: int) -> None:
        if arb_index not in [0, 1]:
            raise UtgError("ARB index must be 0 or 1")

    def _validate_channel(self, channel: int) -> None:
        if channel not in [1, 2]:
            raise UtgError("Channel must be 1 or 2")

    def _validate_frequency(self, limit: float, frequency: float) -> None:
        if frequency < 0 or frequency > limit:
            raise UtgError(f"Frequency must be in range 0-{limit} Hz")

    def _validate_symmetry(self, symmetry: float) -> None:
        if symmetry < 0 or symmetry > 100:
            raise UtgError(f"Symmetry must be in range 0-100%")
