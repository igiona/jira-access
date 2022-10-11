## Class to be used as auth mechanism for the requests module
##
import base64
import requests

class BasicAuth(requests.auth.AuthBase):
    def __init__(self, mail, token):
        accessKey = f"{mail}:{token}"
        self._accessKeyEncoded = base64.b64encode(accessKey.encode("ascii")).decode('ascii')

    def __call__(self, r):
        r.headers["authorization"] = "Basic " + self._accessKeyEncoded
        return r