"""Module to define the BearerAuth class."""

from __future__ import annotations

import requests


class BearerAuth(requests.auth.AuthBase):
    """Class to be used as auth mechanism for the requests module."""

    def __init__(self, token: str):
        """Instantiate a BearerAuth object.

        Args:
            token: the token of the user
        """
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Add the BearerAuth header to the request.

        Returns:
            the request with the BearerAuth header added
        """
        r.headers["authorization"] = "Bearer " + self.token
        return r
