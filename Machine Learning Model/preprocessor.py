import numpy
import math
import scipy

class P300_Preprocessor(object):
    
    def __init__(
            self,
            signals,
            stimulus_code,
            target_char,
            matrix,
            common_average_reference = 0,
            moving_average = 0,
            z_score = 0,
            decimation = 0,
            extracted_channels = numpy.empty((0)),
            digitization_samples = 240,
            start_window = 0,
            end_window = 240
        ):
        
        self.signals = signals
        self.stimulus_code = stimulus_code
        self.target_char = target_char
        self.matrix = matrix
        self.digitization_samples = digitization_samples
        self.start_window = start_window
        self.end_window = end_window
        
        self.window = self.end_window - self.start_window
        self.intensifications = self.matrix.shape[0] + self.matrix.shape[1]
        self.digitization_difference = math.floor(self.digitization_samples / 10)
        
        self.preprocessed_signals = signals
        
        self.calculate_average()
        if common_average_reference: self.calulate_common_average_reference()
        if moving_average: self.calculate_moving_average(moving_average)
        if z_score: self.calculate_z_score()
        if decimation: self.calculate_decimation(decimation)
        if extracted_channels.shape[0]: self.calculate_concatenation(extracted_channels)
        
        self.calculate_classes()
    
    def reinit(
            self,
            signals = None,
            stimulus_code = None,
            target_char = None,
            matrix = None,
            common_average_reference = 0,
            moving_average = 0,
            z_score = 0,
            decimation = 0,
            extracted_channels = numpy.empty((0)),
            digitization_samples = 240,
            start_window = 0,
            end_window = 240
        ):
        
        if signals: self.signals = signals
        if stimulus_code: self.stimulus_code = stimulus_code
        if target_char: self.target_char = target_char
        if matrix: self.matrix = matrix
        if digitization_samples: self.digitization_samples = digitization_samples
        if start_window: self.start_window = start_window
        if end_window: self.end_window = end_window
        
        self.window = self.end_window - self.start_window
        self.intensifications = self.matrix.shape[0] + self.matrix.shape[1]
        self.digitization_difference = math.floor(self.digitization_samples / 10)
        
        self.preprocessed_signals = signals
        self.preprocessed_classes = None
        
        self.calculate_average()
        if common_average_reference: self.calulate_common_average_reference()
        if moving_average: self.calculate_moving_average(moving_average)
        if z_score: self.calculate_z_score()
        if decimation: self.calculate_decimation(decimation)
        if extracted_channels.shape[0]: self.calculate_concatenation(extracted_channels)
        
        self.calculate_classes()
    
    # Calculation of Intensification Average
    def calculate_average(self):
        
        preprocessed_signals = numpy.zeros((self.preprocessed_signals.shape[0], self.intensifications, self.window, self.preprocessed_signals.shape[2]))
        
        for epoch in range(self.preprocessed_signals.shape[0]):
            
            intensification_counter = numpy.zeros((self.intensifications))
            for n in range(1, self.preprocessed_signals.shape[1]):
                if self.stimulus_code[epoch, n] == 0 and self.stimulus_code[epoch, n - 1] != 0:
                    intensification_counter[int(self.stimulus_code[epoch, n - 1]) - 1] += 1
                    preprocessed_signals[epoch, int(self.stimulus_code[epoch, n - 1]) - 1] += self.preprocessed_signals[epoch, n + self.start_window - self.digitization_difference : n + self.end_window - self.digitization_difference]
            for intensification in range(self.intensifications):
                preprocessed_signals[epoch, intensification] /= intensification_counter[intensification]
        
        self.preprocessed_signals = preprocessed_signals
    
    
    # Calculation of Common Average Reference
    def calulate_common_average_reference(self):
        
        for epoch in range(self.preprocessed_signals.shape[0]):
            
            mean_sample = numpy.mean(self.preprocessed_signals[epoch, :, :, :], axis=2)
            for channel in range(self.preprocessed_signals.shape[3]):
                self.preprocessed_signals[epoch, :, :, channel] = self.preprocessed_signals[epoch, :, :, channel] - mean_sample
    
    
    # Calculation of Moving Average
    def calculate_moving_average(self, moving_average):
        
        for epoch in range(self.preprocessed_signals.shape[0]):
            
            for intensification in range(self.preprocessed_signals.shape[1]):
                for sample in range(math.ceil(self.preprocessed_signals.shape[2] / moving_average)):
                    if ((sample * moving_average) + moving_average) < self.preprocessed_signals.shape[2]:
                        self.preprocessed_signals[epoch, intensification, (sample * moving_average) : ((sample * moving_average) + moving_average), :] = \
                            numpy.mean(self.preprocessed_signals[epoch, intensification, (sample * moving_average) : ((sample * moving_average) + moving_average), :], axis=0)
                    else:
                        self.preprocessed_signals[epoch, intensification, (sample * moving_average) : , :] = \
                            numpy.mean(self.preprocessed_signals[epoch, intensification, (sample * moving_average) : , :], axis=0)
    
    
    # Calculation of Z-Score
    def calculate_z_score(self):
        
        for epoch in range(self.preprocessed_signals.shape[0]):
            
            mean_channel = numpy.mean(self.preprocessed_signals[epoch, :, :, :], axis=1)
            std_channel = numpy.std(self.preprocessed_signals[epoch, :, :, :], axis=1)
            for sample in range(self.preprocessed_signals.shape[2]):
                self.preprocessed_signals[epoch, :, sample, :] = (self.preprocessed_signals[epoch, :, sample, :] - mean_channel) / std_channel
    
    
    # Calculation of Decimation
    def calculate_decimation(self, decimation):
        
        preprocessed_signals = numpy.zeros((self.preprocessed_signals.shape[0], self.intensifications, math.floor(self.window / decimation), self.preprocessed_signals.shape[3]))
        
        for epoch in range(self.preprocessed_signals.shape[0]):
            
            for intensification in range(self.preprocessed_signals.shape[1]):
                for i in range(math.floor(self.window / decimation)):
                    preprocessed_signals[epoch, intensification, i, :] = self.preprocessed_signals[epoch, intensification, (i * decimation), :]
        
        self.preprocessed_signals = preprocessed_signals
    
    
    # Calculation of Concatenation
    def calculate_concatenation(self, extracted_channels):
        
        preprocessed_signals = numpy.zeros((self.preprocessed_signals.shape[0], self.preprocessed_signals.shape[1], self.preprocessed_signals.shape[2] * extracted_channels.shape[0]))
        
        for epoch in range(self.preprocessed_signals.shape[0]):
        
            for intensification in range(self.preprocessed_signals.shape[1]):
                    
                    for channel_index in range(extracted_channels.shape[0]):
                        preprocessed_signals[epoch, intensification, (self.preprocessed_signals.shape[2] * channel_index):(self.preprocessed_signals.shape[2] * channel_index) + self.preprocessed_signals.shape[2]] = \
                            self.preprocessed_signals[epoch, intensification, :, extracted_channels[channel_index]]
    
        self.preprocessed_signals = preprocessed_signals
    
    
    # Class (y) Constructor
    def calculate_classes(self):
        
        self.preprocessed_classes = numpy.zeros((len(self.target_char), self.intensifications))
        
        for epoch in range(len(self.target_char)):
            
            # Getting Index Of Chosen Character
            indices = numpy.where(self.matrix == self.target_char[epoch])
            chosen_column = indices[1][0]
            chosen_row = indices[0][0] + self.matrix.shape[1]
            
            for row_column in range(self.intensifications):
                if row_column == chosen_row or row_column == chosen_column:
                    self.preprocessed_classes[epoch, row_column] = 1
                else:
                    self.preprocessed_classes[epoch, row_column] = -1