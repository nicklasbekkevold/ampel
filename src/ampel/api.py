import json
import time

import requests


def http_get_request(url: str, path: str, headers=None, params=None) -> dict[str:str]:
    """Performs HTTP get request and return response body if successful, otherwise
    returns None.
    """
    session = requests.Session()

    if headers is None:
        headers = {}
    try:
        response = session.get(url + path, params=params)
    except Exception:
        time.sleep(1)  # try again
        response = session.get(url + path, params=params, timeout=120)

    if response.status_code in (200, 201):
        return json.loads(response.content.decode("utf-8"))
    else:
        print(response.status_code)
