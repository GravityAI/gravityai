import requests
import os
import json
from fileSaver import mappings
import fileSaver

class GravityAIPipeline:
    def __init__(self, containers_list, keys_list, container_metadata_dicts):
        self.containers_list = containers_list
        self.keys_list = keys_list
        self.container_metadata_dicts = container_metadata_dicts

    def run(self, file):
        currentFile = file
        previousFile = None
        for i in range(len(self.containers_list)):
            if previousFile is not None:
                os.remove(previousFile)
            container = self.containers_list[i]
            key = self.keys_list[i]
            metadata = self.container_metadata_dicts
            containerRunner = GravityAIContainerRunner(container, key, metadata)
            containerRunner.postKey()
            
            result = containerRunner.run(currentFile)
            
            outputFileType = self.container_metadata_dicts[i]["outputFileType"]
            saverClass_ = getattr(fileSaver, mappings[outputFileType])
            saver = saverClass_()
            newFile = saver.save(result, f"tempFile_{i}")
            previousFile = currentFile
            currentFile = newFile
        return result


            



class GravityAIContainerRunner:
    def __init__(self, name, key, metadata, outputFileSaveMethod):
        self.name = name
        self.key = key
        self.metadata = metadata
        self.outputFileSaveMethod = outputFileSaveMethod
        self.openMethods = {"txt": "r", "pdf": "rb", "json": "r"}
    
    def postKey(self):
        url = self.metadata["url"]
        with open(self.key, "rb") as f:
            headers = {'accept': '*/*'}
            files = {"License": f}           
            requests.post(f"http://{url}/api/license/file", headers=headers, files=files)

    def run(self, file):
        mimeType = self.metadata["MimeType"]
        url = self.metadata["url"]
        headers = {'accept': '*/*'}
        openMethod = self.openMethods[file.split(".")[-1]]
        
        with open(file, openMethod) as f:
            files = {
                'Mappings': (None, ''),
                'CallbackUrl': (None, ''),
                'MimeType': (None, mimeType),
                'File': f,
            }

        result_submission = requests.post(f"http://{url}/data/add-job", files=files, headers=headers)
        id = result_submission.json()['data']['id']

        while True:
            status_code_json = requests.get(f"http://{url}/data/status/{id}")
            if status_code_json.json()['data']['status'] == 'Complete':
                break
        result_json = requests.get(f"http://{url}/data/result/{id}")
        result = result_json.json()
        return result




