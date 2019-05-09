import numpy

class P300_FileLoader(object):
    
    def __init__(self, signal_pretext, stimulus_code_pretext, characters_to_be_loaded):
        
        self.signal_pretext = signal_pretext
        self.stimulus_code_pretext = stimulus_code_pretext
        self.characters_to_be_loaded = characters_to_be_loaded
        
        self.signal_session = numpy.empty((0))
        self.stimulus_code_session = numpy.empty((0))
        
        self.load_files()
    
    def reinit(self, signal_pretext, stimulus_code_pretext, characters_to_be_loaded):
        
        self.signal_pretext = signal_pretext
        self.stimulus_code_pretext = stimulus_code_pretext
        self.characters_to_be_loaded = characters_to_be_loaded
        
        self.signal_session = numpy.empty((0))
        self.stimulus_code_session = numpy.empty((0))
        
        self.load_files()
    
    def load_files(self):
        
        for char in self.characters_to_be_loaded:
            
            signal_epoch = numpy.loadtxt(self.signal_pretext + char + '.txt')
            stimulus_code_epoch = numpy.loadtxt(self.stimulus_code_pretext + char + '.txt')
            
            self.append_epoch_into_session(signal_epoch, stimulus_code_epoch)
    
    def append_epoch_into_session(
            self,
            signal_epoch,
            stimulus_code_epoch
        ):
        
        if (self.signal_session.shape[0] == 0) and (self.stimulus_code_session.shape[0] == 0):
            self.signal_session = numpy.reshape(signal_epoch, (1, -1, self.channels))
            self.stimulus_code_session = numpy.reshape(stimulus_code_epoch, (1, -1))
        
        else:
            # Determine Minimum
            final_index = min(self.signal_session.shape[1], signal_epoch.shape[0])
            
            # Clip
            self.signal_session = self.signal_session[:, : final_index, :]
            self.stimulus_code_session = self.stimulus_code_session[:, : final_index]
            signal_epoch = signal_epoch[ : final_index, :]
            stimulus_code_epoch = stimulus_code_epoch[ : final_index]
            
            # Reshape
            signal_epoch = numpy.reshape(signal_epoch, (1, -1, self.signal_session.shape[2]))
            stimulus_code_epoch = numpy.reshape(stimulus_code_epoch, (1, -1))
            
            # Append
            self.signal_session = numpy.append(self.signal_session, signal_epoch, axis = 0)
            self.stimulus_code_session = numpy.append(self.stimulus_code_session, stimulus_code_epoch, axis = 0)