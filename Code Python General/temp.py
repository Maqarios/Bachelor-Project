import numpy
import math

from P300_FileLoader import P300_FileLoader
from P300_Preprocessor import P300_Preprocessor
from P300_Model import P300_Model
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])

user_name = input('Enter User Name: ')

loader = P300_FileLoader(user_name)
i = math.floor(0.8 * len(loader.loaded_characters))

signal_train = loader.signal[:i]
stimulus_code_train = loader.stimulus_code[:i]
target_char_train = loader.loaded_characters[:i]

signal_test = loader.signal[i:]
stimulus_code_test = loader.stimulus_code[i:]
target_char_test = loader.loaded_characters[i:]

CAR = 1
MA = 13
ZS = 1
D = 6

preprocessor_train = P300_Preprocessor(
        signal_train,
        stimulus_code_train,
        target_char_train,
        CHARACTER_MATRIX,
        common_average_reference=CAR,
        moving_average=MA,
        z_score=ZS,
        decimation=D,
        extracted_channels=numpy.arange(14),
        digitization_samples=128,
        start_window=0,
        end_window=128
    )

preprocessor_test = P300_Preprocessor(
        signal_test,
        stimulus_code_test,
        target_char_test,
        CHARACTER_MATRIX,
        common_average_reference=CAR,
        moving_average=MA,
        z_score=ZS,
        decimation=D,
        extracted_channels=numpy.arange(14),
        digitization_samples=128,
        start_window=0,
        end_window=128
    )

preprocessor_train.plot()
preprocessor_test.plot()

X, y = preprocessor_train.calculate_reshape()
model = P300_Model(LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto'))
model.fit(X, y)
print(model.calculate_accuracy(preprocessor_test.preprocessed_signal, target_char_test, CHARACTER_MATRIX))