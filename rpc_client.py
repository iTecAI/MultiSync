import json
import requests
from cryptography.fernet import Fernet
import base64, time

def _request(url, data, key):
    f = Fernet(base64.urlsafe_b64decode(key))
    payload = {'data':base64.urlsafe_b64encode(f.encrypt(json.dumps(data).encode('utf-8'))).decode('utf-8')}
    resp = json.loads(requests.post(url,{},payload).text)
    dat = f.decrypt(base64.urlsafe_b64decode(resp['data'].encode('utf-8'))).decode('utf-8')
    return json.loads(dat)

class Client:
    def __init__(self,config):
        self.server = config['server_url']
        self.key = config['key']
    def request(self,path,payload):
        return _request(self.server+path,payload,self.key)
    def add_module(self,key,data):
        return self.request('/modules/add/',{'key':key,'data':data})
    def check_status(self,key):
        return self.request('/modules/status/',{'key':key})
    def remove_module(self,key):
        return self.request('/modules/remove/',{'key':key})
    def update_module(self,key):
        return self.request('/modules/update/',{'key':key})
    def get_module_info(self,key=None):
        if key:
            return self.request('/modules/info/',{'key':key})
        else:
            return self.request('/modules/info/',{})
    def command(self,module,command,kwargs):
        return self.request(f'/command/',{'module':module,'command':command,'kwargs':kwargs})