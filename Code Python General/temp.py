import numpy
from P300_Preprocessor import P300_Preprocessor
import matplotlib.pyplot as plt

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])




# -------------------------------------------- CONTROLLER -------------------------------------------- #
# -------------------------------------------- ########## -------------------------------------------- #

char = 'A'
signal = numpy.loadtxt('signal_' + char + '.txt')
stimulus_code = numpy.loadtxt('stimulus_code_' + char + '.txt')

x = P300_Preprocessor(
        signal.reshape(1, -1, 14),
        stimulus_code.reshape(1, -1),
        char,
        CHARACTER_MATRIX,
        common_average_reference=0,
        end_window=128,
        digitization_samples=128
    )
plt.plot(x.preprocessed_signals[0, 0, :, 0])
plt.plot(x.preprocessed_signals[0, 3, :, 0])
plt.legend(['P300', 'Non-P300'])