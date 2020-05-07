import hmac
import hashlib
import time

class Authentication:
    def __init__(self, key: str='', secret: str='') -> None:
        self._key = key
        self._secret = secret.encode()

    def _prepare(self, req_args: dict) -> dict:
        auth_args = {'api_key': self._key, 'timestamp': int(time.time() * 1000)}
        return dict(sorted({**req_args, **auth_args}.items()))

    def _sign(self, query_str: str) -> str:
        hexdigest = hmac.new(self._secret, query_str.encode(), hashlib.sha256).hexdigest()
        return f'sign={hexdigest}'

    def _wssign(self) -> str:
        expires = int((time.time() + 5.0) * 1000)
        signature = hmac.new(self._secret, f'GET/realtime{expires}'.encode(), hashlib.sha256).hexdigest()
        return f'api_key={self._key}&expires={expires}&signature={signature}'
