import numpy
import os.path

class P300_FileLoader(object):
    
    def __init__(self, user_name):
        
        self.user_name = user_name
        
        self.load_files()
    
    def reinit(self, user_name):
        
        self.user_name = user_name
        
        self.load_files()
    
    def load_files(self):
        
        self.signal = numpy.empty((0))
        self.stimulus_code = numpy.empty((0))
        self.loaded_characters = ''
        
        characters_to_be_loaded = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_'
        
        for trial in range(100):
            
            path = 'user_data/' + self.user_name + '/' + str(trial)
            
            if os.path.exists(path):
                
                for char in characters_to_be_loaded:
                    
                    try:
                        signal_epoch = numpy.loadtxt(path + '/signal_' + char + '.txt')
                        stimulus_code_epoch = numpy.loadtxt(path + '/stimulus_code_' + char + '.txt')
                    except:
                        print('Character:', char, 'Not Found!')
                        continue
                
                    self.loaded_characters += char
                    self.append_epoch(signal_epoch, stimulus_code_epoch)
    
    def append_epoch(
            self,
            signal_epoch,
            stimulus_code_epoch
        ):
        
        if (self.signal.shape[0] == 0) and (self.stimulus_code.shape[0] == 0):
            self.signal = numpy.reshape(signal_epoch, (1, -1, signal_epoch.shape[1]))
            self.stimulus_code = numpy.reshape(stimulus_code_epoch, (1, -1))
        
        else:
            # Determine Minimum
            final_index = min(self.signal.shape[1], signal_epoch.shape[0])
            
            # Clip
            self.signal = self.signal[:, : final_index, :]
            self.stimulus_code = self.stimulus_code[:, : final_index]
            signal_epoch = signal_epoch[ : final_index, :]
            stimulus_code_epoch = stimulus_code_epoch[ : final_index]
            
            # Reshape
            signal_epoch = numpy.reshape(signal_epoch, (1, -1, self.signal.shape[2]))
            stimulus_code_epoch = numpy.reshape(stimulus_code_epoch, (1, -1))
            
            # Append
            self.signal = numpy.append(self.signal, signal_epoch, axis = 0)
            self.stimulus_code = numpy.append(self.stimulus_code, stimulus_code_epoch, axis = 0)