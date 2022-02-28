import abc
import eli5
from .modelhandler import *


MODEL_TYPE_MAPPINGS = {
    "general": "GeneralHandler",
    "neuralNetwork": "NeuralNetworkHandler"
}

class Explainer(abc.ABC):
    '''
    Abstract explainer class
    '''
    
    def __init__(self, model, data,model_type="general"):
        self.model = model
        self.data = data
        self.model_type = model_type

       

class SHAPExplainer(Explainer):
    '''
    Concrete class for SHAP explainer
    '''

    def __init__(self, model, data,  model_type="general"):
        super().__init__(model, data, model_type)
        self.modelHandler = self._makeModelHandler()
    
    def _makeModelHandler(self):
        module = __import__("modelhandler")
        class_ = getattr(module, MODEL_TYPE_MAPPINGS[self.model_type])
        instance = class_()
        return instance

    def getExplanationObject(self):
        return self.modelHandler.getExplainer(self.model, self.data)

    def getBarPlotJson(self, explanationObject, max_features=5, output_labels=None, feature_labels=None):
        return self.modelHandler.getBarPlotJson(explanationObject, self.data, max_features, output_labels, feature_labels)

class ELI5Explainer(Explainer):
    '''
    Concrete class for ELI5 explainer
    '''
    def __init__(self, model, data, outputs, model_type="general"):
        super().__init__(model, data, outputs, model_type)

    def explainWeights(self):
        return eli5.explain_weights(self.model) #for interface with a front end to show different graphs

    def explainPredictions(self, dataPoint):
        return eli5.explain_prediction(self.model, dataPoint)

