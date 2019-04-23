import numpy
import tkinter
import random
import socket
import _thread
import EmotivSocket

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])



# -------------------------------------------- GUI -------------------------------------------- #
class P300_GUI(object):
    
    def __init__(
            self,
            controller,
            character_matrix,
            font = 'Courier 10',
            bg = 'black',
            fg = 'grey',
            color_array = numpy.array(['red', 'green', 'blue']),
            start_delay = 2500,
            state_0_delay = 100,
            state_1_delay = 75,
            end_delay = 2000
        ):
        
        # Instance Variables
        self.controller = controller
        self.character_matrix = character_matrix
        self.font = font
        self.bg = bg
        self.fg = fg
        self.color_array = color_array
        self.start_delay = start_delay
        self.state_0_delay = state_0_delay
        self.state_1_delay = state_1_delay
        self.end_delay = end_delay
        
        self.is_session = False
        self.stimulus_code = -1
        
        # Tkinter Initialization
        self.root = tkinter.Tk()
        self.root.title('On-Screen BCI Keyboard')
        self.root.attributes('-topmost', True)
        
        # Label Initialization
        self.label_matrix = numpy.empty(self.character_matrix.shape, dtype = tkinter.Label)
        for row in numpy.arange(self.character_matrix.shape[0]):
            for column in numpy.arange(self.character_matrix.shape[1]):
                self.label_matrix[row, column] = tkinter.Label(self.root, text = self.character_matrix[row, column], bg = self.bg, fg = self.fg, font = self.font)
                self.label_matrix[row, column].grid(row = row, column = column)
        self.root.geometry('%dx%d+500+0' % (self.label_matrix[0, 0].winfo_reqwidth() * self.label_matrix.shape[1], self.label_matrix[0, 0].winfo_reqheight() * self.label_matrix.shape[0]))
    
    def __del__(self):
        self.close()
        del self
    
    # Update GUI
    def update(self):
        self.root.update()
    
    # Close GUI
    def close(self):
        self.root.destroy()
    
    # Color Reset
    def reset_colors(self):
        for row in numpy.arange(self.character_matrix.shape[0]):
            for column in numpy.arange(self.character_matrix.shape[1]):
                self.label_matrix[row, column].config(bg = self.bg, fg = self.fg)
    
    # Session Run
    def start_session(self):
        
        # Set Session State To True
        self.is_session = True
        
        # Intensification Order Initialization
        columns = numpy.arange(self.label_matrix.shape[1])
        numpy.random.shuffle(columns)
        
        rows = numpy.arange(self.label_matrix.shape[0]) + self.label_matrix.shape[1]
        numpy.random.shuffle(rows)
        
        self.intensification_order = numpy.append(columns, rows)
        print(self.intensification_order)
        
        # Chosen Intensification Initialization
        self.intensification_order_index = 0
        self.stimulus_code = -1
        
        # Sleep for 2.5s Then Start
        self.root.after(self.start_delay, self.state_0)
    
    def repeat_session(self):
        
        # Decrease Repetitions
        self.controller.temp_repetitions -= 1
        
        # Intensification Order Initialization
        columns = numpy.arange(self.label_matrix.shape[1])
        numpy.random.shuffle(columns)
        
        rows = numpy.arange(self.label_matrix.shape[0]) + self.label_matrix.shape[1]
        numpy.random.shuffle(rows)
        
        self.intensification_order = numpy.append(columns, rows)
        print(self.intensification_order)
        
        # Chosen Intensification Initialization
        self.intensification_order_index = 0
        self.stimulus_code = -1
        
        # Start Immediately
        self.state_0()
    
    # Session End
    def end_session(self):
        self.is_session = False
        
    # State Where Row / Column Is Intensified For 100ms
    def state_0(self):
        
        # Get Chosen Row / Column
        self.stimulus_code = self.intensification_order[self.intensification_order_index]
        if self.stimulus_code < self.label_matrix.shape[1]:
            row_column_labels = self.label_matrix[:, self.stimulus_code % self.label_matrix.shape[1]]
        else:
            row_column_labels = self.label_matrix[self.stimulus_code % self.label_matrix.shape[0], :]
        
        color_index = random.randint(0, self.color_array.shape[0] - 1)
        for label in row_column_labels:
            label.config(fg = self.color_array[color_index])
        
        # Wait Then Move To Next State
        self.root.after(self.state_0_delay, self.state_1)
    
    # State Where No Row / Column Is Intensified For 75ms
    def state_1(self):
        
        self.stimulus_code = -1
        self.reset_colors();
        
        # Check If Final Index
        self.intensification_order_index += 1
        if self.intensification_order_index < self.intensification_order.shape[0]:
            self.root.after(self.state_1_delay, self.state_0)
        elif self.controller.temp_repetitions != 0:
            self.root.after(self.state_1_delay, self.repeat_session)
        else:
            self.root.after(self.end_delay, self.end_session)
# -------------------------------------------- ### -------------------------------------------- #





# -------------------------------------------- Socket -------------------------------------------- #
class P300_Socket(object):
    
    def __init__(self, controller, HOST, PORT, BUFFER_SIZE = 256, FLUSH_SIZE = 300):
        
        self.controller = controller
        self.HOST = HOST
        self.PORT = PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.FLUSH_SIZE = FLUSH_SIZE
        
        # Socket Establishment
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect
        self.connect()
    
    def __del__(self):
        self.disconnect()
        del self
        
    def connect(self):
        self.socket.connect((self.HOST, self.PORT))
        self.socket.send(b'\r\n')
    
    def disconnect(self):
        self.socket.close()
    
    def receive(self):
        return self.socket.recv(self.BUFFER_SIZE)
    
    def setblocking(self, flag):
        self.socket.setblocking(flag)
    
    def flush(self):
        for _ in range(self.FLUSH_SIZE):
            self.receive()
# -------------------------------------------- ###### -------------------------------------------- #





# -------------------------------------------- CONTROLLER -------------------------------------------- #
class P300_Controller(object):
    
    def __init__(
            self,
            
            character_matrix,
            
            repetitions = 15,
            channels = 14,
            start_sample = 410,
            end_sample = 910,
            
            bg = 'black',
            fg = 'grey',
            color_array = numpy.array(['red', 'green', 'blue']),
            font = 'Courier 10',
            start_delay = 2500,
            state_0_delay = 100,
            state_1_delay = 75,
            end_delay = 2000,
            
            
            IP = '127.0.0.1',
            PORT = 54123,
            BUFFER_SIZE = 256
        ):
        
        self.gui = P300_GUI(
                self,
                character_matrix,
                font = font,
                bg = bg,
                fg = fg,
                color_array = color_array,
                start_delay = start_delay,
                state_0_delay = state_0_delay,
                state_1_delay = state_1_delay,
                end_delay = end_delay
            )
        
        self.socket = P300_Socket(
                self,
                IP,
                PORT,
                BUFFER_SIZE = BUFFER_SIZE
            )
        
        self.repetitions = repetitions
        self.channels = channels
        self.start_sample = start_sample
        self.end_sample = end_sample
        
        self.temp_repetitions = 0
    
    def __del__(self):
        del self.gui
        del self.socket
        del self
    
    def mainloop(self):
        while 1:
            self.gui.update()
    
    def train_session(self, target_char):
        signal_session = numpy.empty((0))
        stimulus_code_session = numpy.empty((0))
        
        for _ in target_char:
            
            # Record
            signal_epoch, stimulus_code_epoch = self.record()
            
            # Append
            signal_session, stimulus_code_session = self.append_epoch_into_session(
                    signal_session,
                    stimulus_code_session,
                    signal_epoch,
                    stimulus_code_epoch
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
        
        # Start GUI Session
        self.gui.start_session()
        
        while 1:
            
            # Update GUI
            self.gui.update()
            
            data = self.socket.receive()
            
            data = data.decode('utf-8')
            data = numpy.fromstring(data, dtype = numpy.float, sep=',')[2 : 2 + self.channels]
            if(data.shape[0] == self.channels):
                signal = numpy.append(signal, data.reshape(1, self.channels), axis = 0)
                stimulus_code = numpy.append(stimulus_code, self.gui.stimulus_code + 1)
            
            if self.gui.is_session == False:
                break
        
        return signal, stimulus_code
# -------------------------------------------- ########## -------------------------------------------- #
_thread.start_new_thread(EmotivSocket.EmotivSocketSender, ())

cntrlr = P300_Controller(CHARACTER_MATRIX, font = 'Courier 70')

target_char = 'ABCDEF'
signal, stimulus_code = cntrlr.train_session(target_char)
for index in range(len(target_char)):
    numpy.savetxt('signal_' + target_char[index] + '.txt', signal[index])
    numpy.savetxt('stimulus_code_' + target_char[index] + '.txt', stimulus_code[index])

cntrlr.gui.close()
cntrlr.socket.disconnect()