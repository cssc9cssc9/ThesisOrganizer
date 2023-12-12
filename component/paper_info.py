import os

class PaperInfo:
    def __init__(self, apiData:dict):
        self.requestJsonData = apiData

    def get_data(self) -> dict:
        return self.preprocessing()
    
    def preprocessing(self) -> dict:
        requestData = dict()
        requestData.update(self.requestJsonData)
        if 'authors' in requestData:
            requestData['authors'] = ','.join([author['name'] for author in requestData['authors']])
        if 'fieldsOfStudy' in requestData:
            requestData['fieldsOfStudy'] = ','.join([field for field in requestData['fieldsOfStudy'] ]) if requestData['fieldsOfStudy'] else ""
        return requestData