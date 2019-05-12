import numpy

class P300_Model(object):
    
    def __init__(self, model):
        
        self.model = model
    
    def fit(self, X, y):
        self.model.fit(X, y)
    
    def predict(self):
        return
    
    def predict_character(self, signal, matrix):
        
        predicted_classes = self.model.decision_function(signal)

        column = numpy.where(predicted_classes[:6] == numpy.amax(predicted_classes[:6]))[0][0]
        row = numpy.where(predicted_classes[6:] == numpy.amax(predicted_classes[6:]))[0][0]
        
        return matrix[row, column]
    
    def calculate_accuracy(self, signal, matrix, target_char):
        
        accuracy = 0
        
        for epoch in range(signal.shape[0]):
            
            if target_char[epoch] == self.predict_character(signal[epoch], matrix):
                accuracy += 1
            
            accuracy = (accuracy / len(target_char)) * 100
        
        return accuracy