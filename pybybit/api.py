from .rest import RESTAPI
from .ws import WebScoketAPI
from .util.auth import Authentication

class API:
    def __init__(self, key: str='', secret: str='', testnet: bool=False):
        auth = Authentication(key, secret)
        self.rest = RESTAPI(auth, testnet)
        self.ws = WebScoketAPI(auth, testnet)
