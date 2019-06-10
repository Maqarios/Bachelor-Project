import numpy
import matplotlib
import random
import os

from P300_GUI import P300_GUI
from P300_Preprocessor import P300_Preprocessor
from P300_SocketReceiver import P300_SocketReceiver
from P300_FileLoader import P300_FileLoader
from P300_Model import P300_Model
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])
matplotlib.rcParams.update({'figure.max_open_warning': 0})

class P300_Controller(object):
    
    def __init__(
            self,
            
            user_name,
            character_matrix,
            
            repetitions = 15,
            channels = 14
        ):
        
        self.user_name = user_name
        self.repetitions = repetitions
        self.channels = channels
        
        self.gui = P300_GUI(self, character_matrix, state_0_delay=100, state_1_delay=75)
        self.socket = P300_SocketReceiver(self)
        
        self.temp_repetitions = 0
    
    def train_session(
            self,
            plot = False
        ):
        
        target_char = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_', 36))
        
        path = 'user_data/' + self.user_name
        if not os.path.exists(path):
            os.mkdir(path)
        
        for i in range(100):
            path =  'user_data/' + self.user_name + '/' + str(i)
            if not os.path.exists(path):
                os.mkdir(path)
                break
        
        for index in numpy.arange(len(target_char)):
            
            row, column = self.search(target_char[index])
            self.gui.label_matrix[row, column].config(fg = 'white')
            
            print('Train Char:', target_char[index] + ', Required:', len(target_char) - index - 1)
            
            # Record
            signal, stimulus_code = self.record()
            
            if signal.shape[0] == 0 or stimulus_code.shape[0] == 0:
                print('Warning: Signal Is Not Received!')
                break
            
            # Save
            numpy.savetxt(path + '/signal_' + target_char[index] + '.txt', signal)
            numpy.savetxt(path + '/stimulus_code_' + target_char[index] + '.txt', stimulus_code)
            
            # Plot
            if(plot):
                P300_Preprocessor(
                        signal.reshape(1, -1, self.channels),
                        stimulus_code.reshape(1, -1),
                        target_char[index],
                        self.gui.character_matrix,
                        common_average_reference=0,
                        moving_average=0,
                        digitization_samples=128,
                        end_window=128
                    ).plot()
    
    def test_session(self):
        
        loader = P300_FileLoader(self.user_name)
        
        signal = loader.signal
        stimulus_code = loader.stimulus_code
        target_char = loader.loaded_characters
        
        preprocessor = P300_Preprocessor(
                signal,
                stimulus_code,
                target_char,
                CHARACTER_MATRIX,
                common_average_reference=1,
                moving_average=13,
                z_score=1,
                decimation=6,
                extracted_channels=numpy.arange(14),
                digitization_samples=128,
                start_window=0,
                end_window=102
            )
        
        X, y = preprocessor.calculate_reshape()
        model = P300_Model(LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto'))
        model.fit(X, y)
        
        print('Done! Self Accuracy:', model.calculate_accuracy(preprocessor.preprocessed_signal, loader.loaded_characters, CHARACTER_MATRIX))
        
        for i in range(5):
            
            signal, stimulus_code = self.record()
            
            if signal.shape[0] == 0 or stimulus_code.shape[0] == 0:
                print('Warning: Signal Is Not Received!')
                break
            
            signal = signal.reshape(1, -1, self.channels)
            stimulus_code = stimulus_code.reshape(1, -1)
            
            preprocessor = P300_Preprocessor(
                    signal,
                    stimulus_code,
                    'A',
                    CHARACTER_MATRIX,
                    common_average_reference=1,
                    moving_average=13,
                    z_score=1,
                    decimation=6,
                    extracted_channels=numpy.arange(14),
                    digitization_samples=128,
                    start_window=0,
                    end_window=102
                )
            
            preprocessor.preprocessed_signal = preprocessor.preprocessed_signal.reshape(12, -1)
            
            predicted_char = model.predict_character(preprocessor.preprocessed_signal, CHARACTER_MATRIX)
            print('Predicted:', predicted_char)
        
    
    def record(self):
        
        # Repetitions Per Epoch
        self.temp_repetitions = self.repetitions - 1
        
        # Start GUI Session
        self.gui.start_session()
        self.socket.start_record()
        
        while 1:
            
            # Update GUI
            self.gui.update()
            
            if self.gui.is_session == False:
                break
        
        return self.socket.end_record()
    
    # Search Function
    def search(self, char):
        
        indices = numpy.where(self.gui.character_matrix == char)
        row = indices[0][0]
        column = indices[1][0]
        
        return row, column


user_name = input('Enter User Name: ')
cntrlr = P300_Controller(user_name, CHARACTER_MATRIX, repetitions=15)
#cntrlr.train_session(plot=True)
cntrlr.test_session()

try:
    cntrlr.gui.close()
    cntrlr.socket.disconnect()
except:
    1