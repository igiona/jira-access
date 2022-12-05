from __future__ import annotations

import base64

import requests


class BasicAuth(requests.auth.AuthBase):
    """Class to be used as auth mechanism for the requests module."""

    def __init__(self, mail: str, token: str):
        access_key = f"{mail}:{token}"
        self._access_key_encoded = base64.b64encode(access_key.encode("ascii")).decode("ascii")

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["authorization"] = "Basic " + self._access_key_encoded
        return r
