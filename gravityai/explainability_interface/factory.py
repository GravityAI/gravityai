import shap
import abc
from .explainer import *

class ExplainabilityFactory(abc.ABC):
    '''
    Abstract factory for the different types of explainability options
    '''
    @abc.abstractmethod
    def create_factory(self):
        pass



class SHAPFactory(ExplainabilityFactory):
    '''
    Concrete factory for SHAP explainer
    '''

    def create_factory(self):
        shapExplainer = SHAPExplainer()
        return shapExplainer

    

class ELI5Factory(ExplainabilityFactory):
    '''
    Concrete factory for ELI5 explainer
    '''
    def create_factory(self):
        eli5Explainer = ELI5Explainer()
        return eli5Explainer







