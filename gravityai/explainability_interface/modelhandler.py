import abc
import shap
import json
import numpy as np

class ModelHandlerSHAP(abc.ABC):
    @abc.abstractmethod
    def getExplainer(self,model, data):
        pass

class GeneralHandler(ModelHandlerSHAP):
    def getExplainer(self, model, data=None):
        explainer = shap.Explainer(model)
        return explainer

    def getBarPlotJson(self, explanationObject,processed_data, max_features=5, output_labels=None, feature_labels=None):
        '''
        A function to get the shap bar plot in json form. Handles both 2D np arrays (single output variable) and 3D np arrays (multiple
        output variables).
        '''
        def getShapBarGraphJson(array, n=max_features):
            '''
            Helper function to take a 2D np array, and return a tuple containing the indices of the shap values (i.e. which feature), as well
            as the shap values. The length of the shap value will almost always be one higher, since the final value in there is the combined shap value
            of the rest of the features. The exception is if n is set to more than the length of the feature space. If feature_labels is provided, it will also include a mapping 
            from indices to feature names for inclusion in the front-end graph.
            '''
            nonlocal feature_labels
            means = array.mean(axis=0)
            ix = np.argsort(means.values)
            shap_values = np.abs(means.values)[ix]
            if feature_labels:
                if shap_values.shape[0] < n:
                    feature_dict = {i:feature_labels[i] for i in list(ix)}
                else:
                    feature_dict = {i:feature_labels[i] for i in list(ix[:n])}
            else:
                feature_dict = None
            if shap_values.shape[0] < n:
                return [ix, shap_values, feature_dict]
            else:
                shap_values_toRet = []
                shap_values_toRet.extend(list(shap_values[:n]))
                sum_shap = np.sum(shap_values[n:])
                shap_values_toRet.append(sum_shap)
                return [ix[:n], shap_values_toRet, feature_dict]
        output_dict = {}
        feature_dict = {}
        shap_values = explanationObject(processed_data)
        if feature_labels and shap_values.shape[1] != len(feature_labels):
            print(len(shap_values))
            raise Exception("Please ensure that the length of the feature_labels list exactly matches the number of features expected by the model.")
        
        if len(shap_values.shape) > 2:
            #handle each categorical variable
            if output_labels and len(output_labels) != shap_values.shape[-1]:
                raise Exception("Please ensure that the output_labels list corresponds exactly to the outputs expected by the model.")
            for z in range(shap_values.shape[2]):
                if output_labels:
                    key = output_labels[z]
                else:
                    key = z
                output_dict[key] = getShapBarGraphJson(shap_values[:,:,z])
        else:
            #single handling
            for z in range(1):
                if len(output_labels) > 1:
                    raise Exception("Please ensure that the output_labels list corresponds exactly to the outputs expected by the model.")
                output_dict = getShapBarGraphJson(shap_values)
        return output_dict

class NeuralNetworkHandler(ModelHandlerSHAP):
    def getExplainer(self, model, data):
        explainer = shap.KernelExplainer(model, data)
        return explainer