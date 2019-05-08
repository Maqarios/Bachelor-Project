import numpy
import tkinter
import random

class P300_GUI(object):
    
    def __init__(
            self,
            controller,
            character_matrix,
            font = 'Courier 70',
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
        self.intensification_order = numpy.arange(self.character_matrix.shape[0] + self.character_matrix.shape[1])
        numpy.random.shuffle(self.intensification_order)
        
        # Chosen Intensification Initialization
        self.intensification_order_index = 0
        self.stimulus_code = -1
        
        # Sleep for 2.5s Then Start
        self.root.after(self.start_delay, self.state_0)
    
    def repeat_session(self):
        
        # Intensification Order Initialization
        self.intensification_order = numpy.arange(self.character_matrix.shape[0] + self.character_matrix.shape[1])
        numpy.random.shuffle(self.intensification_order)
        
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
        
        self.reset_colors()
        
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
            self.controller.temp_repetitions -= 1
            self.root.after(self.state_1_delay, self.repeat_session)
        else:
            self.root.after(self.end_delay, self.end_session)