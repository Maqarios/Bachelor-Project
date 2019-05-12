import numpy

class P300_FileLoader(object):
    
    def __init__(self, signal_pretext, stimulus_code_pretext, characters_to_be_loaded):
        
        self.signal_pretext = signal_pretext
        self.stimulus_code_pretext = stimulus_code_pretext
        self.characters_to_be_loaded = characters_to_be_loaded
        
        self.load_files()
    
    def reinit(self, signal_pretext, stimulus_code_pretext, characters_to_be_loaded):
        
        self.signal_pretext = signal_pretext
        self.stimulus_code_pretext = stimulus_code_pretext
        self.characters_to_be_loaded = characters_to_be_loaded
        
        self.load_files()
    
    def load_files(self):
        
        self.signal = numpy.empty((0))
        self.stimulus_code = numpy.empty((0))
        self.loaded_characters = ''
        
        for char in self.characters_to_be_loaded:
            
            try:
                signal_epoch = numpy.loadtxt(self.signal_pretext + char + '.txt')
                stimulus_code_epoch = numpy.loadtxt(self.stimulus_code_pretext + char + '.txt')
            except:
                print('Character:', char, 'Not Found!')
                continue
            
            self.loaded_characters += char
            
            self.append_epoch_into_session(signal_epoch, stimulus_code_epoch)
    
    def append_epoch_into_session(
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