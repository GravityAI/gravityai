import abc

'''
Placeholder for handling specific data when using the SHAP library. Currently not needed

'''

class DataProcessor(abc.ABC):
    pass

class TextProcessor(DataProcessor):
    pass

class ImageProcessor(DataProcessor):
    pass

class StructuredDataProcessor(DataProcessor):
    pass