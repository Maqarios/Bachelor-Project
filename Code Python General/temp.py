import numpy
import tkinter
import random
import socket
import math
from preprocessor import P300_Preprocessor
import matplotlib

CHARACTER_MATRIX = numpy.array([['A', 'B', 'C', 'D', 'E', 'F'],
                                ['G', 'H', 'I', 'J', 'K', 'L'],
                                ['M', 'N', 'O', 'P', 'Q', 'R'],
                                ['S', 'T', 'U', 'V', 'W', 'X'],
                                ['Y', 'Z', '1', '2', '3', '4'],
                                ['5', '6', '7', '8', '9', '_']])




# -------------------------------------------- CONTROLLER -------------------------------------------- #
# -------------------------------------------- ########## -------------------------------------------- #
#import _thread
#from emotivsocket import EmotivSocketSender
#_thread.start_new_thread(EmotivSocketSender, ())

cntrlr = P300_Controller(CHARACTER_MATRIX, font = 'Courier 70', repetitions=3, state_0_delay=0.11, state_1_delay=0.076)

target_char = 'AJSWO185'
target_char = ''.join(random.sample(target_char, len(target_char)))

signal, stimulus_code = cntrlr.train_session(target_char, plot=True)
for index in range(len(target_char)):
    numpy.savetxt('signal_' + target_char[index] + '.txt', signal[index])
    numpy.savetxt('stimulus_code_' + target_char[index] + '.txt', stimulus_code[index])

cntrlr.gui.close()
cntrlr.socket.disconnect()