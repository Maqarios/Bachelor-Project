import numpy
import tkinter

class P300_GUI(object):
    
    def __init__(
            self,
            character_matrix,
            bg = 'black',
            fg = 'white',
            font = 'Courier 10'
        ):
        
        # Instance Variables
        self.character_matrix = character_matrix
        self.bg = bg
        self.fg = fg
        self.font = font
        
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
        self.root.geometry('%dx%d+0+0' % (self.label_matrix[0, 0].winfo_reqwidth() * self.label_matrix.shape[1], self.label_matrix[0, 0].winfo_reqheight() * self.label_matrix.shape[0]))
        
        # Session Initialization
        self.init_session()
        
        # Event Loop Initialization
        self.root.mainloop()
    
    # Re-Initialization
    def reinit(self, character_matrix):
        self.character_matrix = character_matrix
        self.label_matrix = numpy.empty(self.character_matrix.shape, dtype = tkinter.Label)
        for row in numpy.arange(self.character_matrix.shape[0]):
            for column in numpy.arange(self.character_matrix.shape[1]):
                self.label_matrix[row, column] = tkinter.Label(self.root, text = self.character_matrix[row, column], bg = self.bg, fg = self.fg, font = self.font)
                self.label_matrix[row, column].grid(row = row, column = column)
        self.root.geometry('%dx%d+0+0' % (self.label_matrix[0, 0].winfo_reqwidth() * self.label_matrix.shape[1], self.label_matrix[0, 0].winfo_reqheight() * self.label_matrix.shape[0]))
    
    # Color Reset
    def reset_colors(self):
        for row in numpy.arange(self.character_matrix.shape[0]):
            for column in numpy.arange(self.character_matrix.shape[1]):
                self.label_matrix[row, column].config(bg = self.bg, fg = self.fg)
    
    # Session Initialization
    def init_session(self):
        
        # Intensification Order Initialization
        self.intensification_order = numpy.arange(self.label_matrix.shape[0] + self.label_matrix.shape[1])
        numpy.random.shuffle(self.intensification_order)
        
        # Chosen Intensification Initialization
        self.intensification_order_index = 0
        
        # Sleep for 2.5s Then Start
        self.root.after(2500, self.state_0)
        
    # State Where Row / Column Is Intensified For 100ms
    def state_0(self):
        
        # Get Chosen Row / Column
        if self.intensification_order[self.intensification_order_index] < self.label_matrix.shape[1]:
            row_column_labels = self.label_matrix[:, self.intensification_order[self.intensification_order_index] % self.label_matrix.shape[1]]
        else:
            row_column_labels = self.label_matrix[self.intensification_order[self.intensification_order_index] % self.label_matrix.shape[0], :]
        
        for label in row_column_labels:
            label.config(bg = self.fg, fg = self.bg)
        
        # Wait Then Move To Next State
        self.root.after(100, self.state_1)
    
        
    # State Where No Row / Column Is Intensified For 75ms
    def state_1(self):
        
        self.reset_colors();
        
        # Check If Final Index
        self.intensification_order_index += 1
        if(self.intensification_order_index < self.intensification_order.shape[0]):
            self.root.after(75, self.state_0)
        else:
            self.intensification_order_index = 0
            self.root.after(1000, self.state_0)

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])

gui = P300_GUI(CHARACTER_MATRIX, font='Courier 70')