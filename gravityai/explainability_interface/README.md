# explainability-interface
This repo contains the code which implements abstract and concrete classes to allow machine learning models to interact with various explainability Python libararies, such as DeepSHAP and ELI5. At the moment, those two libraries have concrete implementations. 

The abstract class is called Explainer, and the concrete implementations are stored in `explainer.py`. For the SHAPExplainer, please refer to `example.ipynb` for instructions on how to run the code and obtain information through SHAP. Instructions for ELI5 will be included in a later update.
