from P300_Preprocessor import P300_Preprocessor
from P300_FileLoader import P300_FileLoader
import numpy

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])


signal_pretext = 'owsa/trial 1/signal_'
stimulus_code_pretext = 'owsa/trial 1/stimulus_code_'
target_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_'

loader = P300_FileLoader(signal_pretext, stimulus_code_pretext, target_char)

x = P300_Preprocessor(
        loader.signal,
        loader.stimulus_code,
        target_char,
        CHARACTER_MATRIX,
        digitization_samples=128,
        end_window=128,
        extracted_channels=numpy.array([0, 1])
    ).plot()