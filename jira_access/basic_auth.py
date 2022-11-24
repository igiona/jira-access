import base64

import requests


class BasicAuth(requests.auth.AuthBase):
    """Class to be used as auth mechanism for the requests module."""

    def __init__(self, mail, token):
        access_key = f"{mail}:{token}"
        self._access_key_encoded = base64.b64encode(access_key.encode("ascii")).decode("ascii")

    def __call__(self, r):
        r.headers["authorization"] = "Basic " + self._access_key_encoded
        return r
