import numpy
import matplotlib
import random

from P300_GUI import P300_GUI
from P300_Preprocessor import P300_Preprocessor
from P300_SocketReceiver import P300_SocketReceiver

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])

class P300_Controller(object):
    
    def __init__(
            self,
            
            character_matrix,
            
            repetitions = 15,
            channels = 14
        ):
        
        
        self.repetitions = repetitions
        self.channels = channels
        
        self.gui = P300_GUI(self, character_matrix, state_0_delay=100, state_1_delay=75)
        self.socket = P300_SocketReceiver(self)
        
        self.temp_repetitions = 0
    
    def train_session(
            self,
            target_char,
            signal_pretext = 'signal_',
            stimulus_code_pretext = 'stimulus_code_',
            plot = False
        ):
        
        target_char = ''.join(random.sample(target_char, len(target_char)))
        
        for index in numpy.arange(len(target_char)):
            
            row, column = self.search(target_char[index])
            self.gui.label_matrix[row, column].config(fg = 'white')
            
            print('Train Char:', target_char[index])
            
            # Record
            signal, stimulus_code = self.record()
            
            if signal.shape[0] == 0 or stimulus_code.shape[0] == 0:
                print('Warning: Signal Is Not Received!')
                break
            
            # Save
            numpy.savetxt(signal_pretext + target_char[index] + '.txt', signal)
            numpy.savetxt(stimulus_code_pretext + target_char[index] + '.txt', stimulus_code)
            
            # Plot
            if(plot):
                matplotlib.pyplot.figure(index)
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


signal_pretext = 'owsa/trial 2/signal_'
stimulus_code_pretext = 'owsa/trial 2/stimulus_code_'
target_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_'

x = P300_Controller(CHARACTER_MATRIX, repetitions=15)

x.train_session(
        target_char,
        signal_pretext = signal_pretext,
        stimulus_code_pretext = stimulus_code_pretext,
        plot=True
    )

x.gui.close()
x.socket.disconnect()