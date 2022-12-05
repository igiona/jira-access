from __future__ import annotations

import requests


class BearerAuth(requests.auth.AuthBase):
    """Class to be used as auth mechanism for the requests module."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["authorization"] = "Bearer " + self.token
        return r
