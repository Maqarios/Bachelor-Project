import numpy
import matplotlib

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
        
        self.gui = P300_GUI(self, character_matrix)
        self.socket = P300_SocketReceiver(self)
        
        self.temp_repetitions = 0
    
    def train_session(self, target_char, plot = False):
        signal_session = numpy.empty((0))
        stimulus_code_session = numpy.empty((0))
        
        for index in numpy.arange(len(target_char)):
            
            row, column = self.search(target_char[index])
            self.gui.label_matrix[row, column].config(fg = 'white')
            
            # Record
            signal_epoch, stimulus_code_epoch = self.record()
            
            # Append
            signal_session, stimulus_code_session = self.append_epoch_into_session(
                    signal_session,
                    stimulus_code_session,
                    signal_epoch,
                    stimulus_code_epoch
                )
            
            # Plot
            if(plot):
                matplotlib.pyplot.figure(index)
                P300_Preprocessor(
                        signal_epoch.reshape(1, -1, self.channels),
                        stimulus_code_epoch.reshape(1, -1),
                        target_char[index],
                        self.gui.character_matrix,
                        common_average_reference=0,
                        moving_average=0,
                        digitization_samples=128,
                        end_window=100
                    ).plot()
        
        return signal_session, stimulus_code_session
    
    def append_epoch_into_session(
            self,
            signal_session,
            stimulus_code_session,
            signal_epoch,
            stimulus_code_epoch
        ):
        
        if (signal_session.shape[0] == 0) and (stimulus_code_session.shape[0] == 0):
            signal_session = numpy.reshape(signal_epoch, (1, -1, self.channels))
            stimulus_code_session = numpy.reshape(stimulus_code_epoch, (1, -1))
        
        else:
            # Determine Minimum
            final_index = min(signal_session.shape[1], signal_epoch.shape[0])
            
            # Clip
            signal_session = signal_session[:, : final_index, :]
            stimulus_code_session = stimulus_code_session[:, : final_index]
            signal_epoch = signal_epoch[ : final_index, :]
            stimulus_code_epoch = stimulus_code_epoch[ : final_index]
            
            # Reshape
            signal_epoch = numpy.reshape(signal_epoch, (1, -1, self.channels))
            stimulus_code_epoch = numpy.reshape(stimulus_code_epoch, (1, -1))
            
            # Append
            signal_session = numpy.append(signal_session, signal_epoch, axis = 0)
            stimulus_code_session = numpy.append(stimulus_code_session, stimulus_code_epoch, axis = 0)
        
        return signal_session, stimulus_code_session
    
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

x = P300_Controller(CHARACTER_MATRIX, repetitions=5)
signal, stimulus_code = x.train_session('A')
numpy.savetxt('signal_A', signal[0])
numpy.savetxt('stimulus_code_A', stimulus_code[0])

x.gui.close()
x.socket.disconnect()