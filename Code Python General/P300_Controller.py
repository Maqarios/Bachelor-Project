import numpy
import matplotlib
import math

from P300_GUI import P300_GUI
from P300_Preprocessor import P300_Preprocessor
from P300_SocketReceiver import P300_SocketReceiver

class P300_Controller(object):
    
    def __init__(
            self,
            
            character_matrix,
            
            repetitions = 15,
            channels = 14,
            start_sample = 410,
            end_sample = 910,
            samples_per_seconds = 128,
            start_delay = 2.5,
            state_0_delay = 0.6,
            state_1_delay = 0.2,
            end_delay = 1.0,
            
            bg = 'black',
            fg = 'grey',
            color_array = numpy.array(['red', 'green', 'blue']),
            font = 'Courier 10',
            
            IP = '127.0.0.1',
            PORT = 54123,
            BUFFER_SIZE = 1024
        ):
        
        self.gui = P300_GUI(
                self,
                character_matrix,
                font = font,
                bg = bg,
                fg = fg,
                color_array = color_array
            )
        
        self.socket = P300_SocketReceiver(
                self,
                IP,
                PORT,
                BUFFER_SIZE = BUFFER_SIZE
            )
        
        self.repetitions = repetitions
        self.channels = channels
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.samples_per_seconds = samples_per_seconds
        self.start_delay = start_delay
        self.state_0_delay = state_0_delay
        self.state_1_delay = state_1_delay
        self.end_delay = end_delay
        
        self.start_samples_count = math.floor(self.start_delay * self.samples_per_seconds)
        self.state_0_samples_count = math.floor(self.state_0_delay * self.samples_per_seconds)
        self.state_1_samples_count = math.floor(self.state_1_delay * self.samples_per_seconds)
        self.end_samples_count = math.floor(self.end_delay * self.samples_per_seconds)
        
        self.temp_repetitions = 0
    
    def __del__(self):
        del self.gui
        del self.socket
        del self
    
    def mainloop(self):
        while 1:
            self.gui.update()
    
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
                    ).plot(
                        average_channels=True
                    )
        
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
         
        # Clear Buffer
        self.socket.flush()
        
        # Variable Initialization
        signal = numpy.empty((0, self.channels))
        stimulus_code = numpy.empty((0))
        self.temp_repetitions = self.repetitions - 1
        
        # Start Delay
        message = ''
        message_counter = 0
        while 1:
            
            # Update GUI
            self.gui.update()
            
            # Add Message To Previous Message
            message += self.socket.receive().decode('utf-8')
            
            # Split Message & Read First Part
            temp_message = message.split('\r\n')
            data = numpy.fromstring(temp_message[0], dtype = numpy.float, sep=',')[2 : 2 + self.channels]
            
            if data.shape[0] == self.channels:
                
                # Save Data
                signal = numpy.append(signal, data.reshape(1, self.channels), axis = 0)
                stimulus_code = numpy.append(stimulus_code, self.gui.stimulus_code + 1)
                
                if len(temp_message) == 1:
                    message = ''
                else:
                    message = temp_message[1]
                
                message_counter += 1
                if message_counter == self.start_samples_count:
                    break
        
        # Start GUI Session
        self.gui.start_session()
        self.gui.state_0()
        
        message = ''
        message_counter = 0
        while 1:
            
            # Update GUI
            self.gui.update()
            
            # Add Message To Previous Message
            message += self.socket.receive().decode('utf-8')
            
            # Split Message & Read First Part
            temp_message = message.split('\r\n')
            data = numpy.fromstring(temp_message[0], dtype = numpy.float, sep=',')[2 : 2 + self.channels]
            
            if data.shape[0] == self.channels:
                
                # Save Data
                signal = numpy.append(signal, data.reshape(1, self.channels), axis = 0)
                stimulus_code = numpy.append(stimulus_code, self.gui.stimulus_code + 1)
                
                if len(temp_message) == 1:
                    message = ''
                else:
                    message = temp_message[1]
                
                message_counter += 1
                if message_counter == self.state_0_samples_count:
                    self.gui.state_1()
                elif message_counter == self.state_0_samples_count + self.state_1_samples_count:
                    message_counter = 0
                    if self.gui.intensification_order_index < self.gui.intensification_order.shape[0]:
                        self.gui.state_0()
                    elif self.temp_repetitions != 0:
                        self.temp_repetitions -= 1
                        self.gui.start_session()
                        self.gui.state_0()
                    else:
                        break
        
        # Start Delay
        message = ''
        message_counter = 0
        while 1:
            
            # Update GUI
            self.gui.update()
            
            # Add Message To Previous Message
            message += self.socket.receive().decode('utf-8')
            
            # Split Message & Read First Part
            temp_message = message.split('\r\n')
            data = numpy.fromstring(temp_message[0], dtype = numpy.float, sep=',')[2 : 2 + self.channels]
            
            if data.shape[0] == self.channels:
                
                # Save Data
                signal = numpy.append(signal, data.reshape(1, self.channels), axis = 0)
                stimulus_code = numpy.append(stimulus_code, self.gui.stimulus_code + 1)
                
                message = ''
                if len(temp_message) > 1:
                    for index in numpy.arange(1, len(temp_message)):
                        message += temp_message[index]
                
                message_counter += 1
                if message_counter == self.end_samples_count:
                    break
        
        return signal, stimulus_code
    
    # Search Function
    def search(self, char):
        
        indices = numpy.where(self.gui.character_matrix == char)
        row = indices[0][0]
        column = indices[1][0]
        
        return row, column
