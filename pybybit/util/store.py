import json
from requests import Response, Session
from websocket import WebSocket
from typing import Union, List

class DefaultDataStore:
    def __init__(self):
        self.orderbook = OrderBook()
        self.trade = Trade()
        self.insurance = Insurance()
        self.instrument = Instrument()
        self.kline = Kline()
        self.position = Position()
        self.execution = Execution()
        self.order = Order()
        self.stoporder = StopOrder()
        self.wallet = Wallet()

    def onresponse(self, resp: Response, session: Session):
        if any((resp.request.path_url.startswith('/open-api/order/list'),
                resp.request.path_url.startswith('/private/linear/order/list'))):
            data = resp.json()
            if self._checkstatus(resp, data):
                self.order._onresponse(data['result']['data'])
        elif any((resp.request.path_url.startswith('/open-api/stop-order/list'),
                resp.request.path_url.startswith('/private/linear/stop-order/list'))):
            data = resp.json()
            if self._checkstatus(resp, data):
                self.stoporder._onresponse(data['result']['data'])
        elif any((resp.request.path_url.startswith('/v2/private/position/list'),
                resp.request.path_url.startswith('/private/linear/position/list'))):
            data = resp.json()
            if self._checkstatus(resp, data):
                self.position._onresponse(data['result'])
        elif resp.request.path_url.startswith('/v2/private/wallet/balance'):
            data = resp.json()
            if self._checkstatus(resp, data):
                for k, v in data['result'].items():
                    if k == 'USDT':
                        self.wallet._onresponse(v)
                    else:
                        self.position._onwallet(k ,v)

    def onmessage(self, msg: str, ws: WebSocket):
        wsdata = json.loads(msg)
        if 'topic' in wsdata:
            topic: str = wsdata['topic']
            data: Union[list, dict] = wsdata['data']
            type_: str = wsdata.get('type')
            if any((topic.startswith('orderBookL2_25'),
                    topic.startswith('orderBook_200'))):
                self.orderbook._onmessage(type_, data)
            elif topic.startswith('trade'):
                self.trade._onmessage(data)
            elif topic.startswith('insurance'):
                self.insurance._onmessage(data)
            elif topic.startswith('instrument_info'):
                self.instrument._onmessage(type_, data)
            elif any((topic.startswith('klineV2'),
                      topic.startswith('candle'))):
                self.kline._onmessage(topic, data)
            elif topic.startswith('position'):
                self.position._onmessage(data)
            elif topic.startswith('execution'):
                self.execution._onmessage(data)
            elif topic.startswith('order'):
                self.order._onmessage(data)
            elif topic.startswith('stop_order'):
                self.stoporder._onmessage(data)
            elif topic.startswith('wallet'):
                self.wallet._onmessage(data)

    def _checkstatus(self, resp: Response, data: dict) -> bool:
        return resp.status_code == 200 and data.get('ret_code') == 0

class OrderBook:
    def __init__(self):
        self._data = {}
    
    def getbest(self, symbol: str) -> dict:
        p = {'Sell': [], 'Buy': []}
        for item in self._data.values():
            if item['symbol'] == symbol:
                p[item['side']].append(float(item['price']))
        return {'Sell': min(p['Sell']) if p['Sell'] else None,
                'Buy': max(p['Buy']) if p['Buy'] else None}

    def getbook(self, symbol: str) -> dict:
        b = {'Sell': [], 'Buy': []}
        for item in self._data.values():
            if item['symbol'] == symbol:
                b[item['side']].append(item)
        b['Sell'].sort(key=lambda x: x['price'])
        b['Buy'].sort(key=lambda x: x['price'], reverse=True)
        return b

    def getlist(self) -> List[dict]:
        return list(self._data.values())

    def _key(self, item: dict) -> str:
        symbol = item['symbol']
        id_ = item['id']
        return f'{symbol}@{id_}'

    def _onmessage(self, type_: str, data: Union[list, dict]):
        if type_ == 'snapshot':
            _data = []
            if isinstance(data, list):
                _data.extend(data)
            elif isinstance(data, dict):
                _data.extend(data['order_book'])
            for item in _data:
                key = self._key(item)
                self._data[key] = item
        elif type_ == 'delta':
            for item in data['delete']:
                key = self._key(item)
                if key in self._data:
                    del self._data[key]
            for item in data['update']:
                key = self._key(item)
                if key in self._data:
                    self._data[key].update(item)
                else:
                    self._data[key] = item
            for item in data['insert']:
                key = self._key(item)
                self._data[key] = item

class Trade:
    _MAX_RECORD = 500000

    def __init__(self):
        self._data = []

    def gettrade(self, symbol: str) -> List[dict]:
        t = []
        for item in self._data:
            if item['symbol'] == symbol:
                t.append(item)
        return t

    def getlist(self) -> List[dict]:
        return list(self._data)

    def _onmessage(self, data: List[dict]):
        self._data.extend(data)
        if len(self._data) > self._MAX_RECORD:
            del self._data[:len(self._data) - self._MAX_RECORD]

class Insurance:
    def __init__(self):
        self._data = {}

    def get(self, currency: str) -> dict:
        return dict(self._data.get(currency))

    def getlist(self) -> List[dict]:
        return list(self._data.values())

    def _key(self, item: dict) -> str:
        return item['currency']

    def _onmessage(self, data: List[dict]):
        kv = {item['currency']: item for item in data}
        self._data.update(kv)

class Instrument:
    def __init__(self):
        self._data = {}

    def get(self, symbol: str) -> dict:
        return dict(self._data.get(symbol))
    
    def getlist(self) -> List[dict]:
        return list(self._data.values())

    def _key(self, item: dict) -> str:
        return item['symbol']

    def _onmessage(self, type_: str, data: dict):
        if type_ == 'snapshot':
            key = self._key(data)
            self._data[key] = data
        elif type_ == 'delta':
            for item in data['update']:
                key = self._key(item)
                self._data[key].update(item)

class Kline:
    _MAX_RECORD = 5000

    def __init__(self):
        self._data = {}

    def get(self, symbol: str, start: int) -> dict:
        return dict(self._data.get(f'{symbol}@{start}'))

    def getlist(self) -> List[dict]:
        return list(self._data.values())
    
    def _key(self, item: dict) -> str:
        symbol = item['symbol']
        start = item['start']
        return f'{symbol}@{start}'

    def _onmessage(self, topic: str, data: List[dict]):
        symbol = topic.split('.')[-1]
        for item in data:
            item = {**{'symbol': symbol}, **item}
            key = self._key(item)
            if key in self._data:
                self._data[key].update(item)
            else:
                self._data[key] = item
        while len(self._data) > self._MAX_RECORD:
            del self._data[next(iter(self._data))]

class Position:
    def __init__(self):
        self._data = {}

    def get(self, symbol: str) -> dict:
        return dict(self._data.get(symbol))
    
    def getboth(self, symbol: str) -> dict:
        return {'Sell': self._data.get(f'{symbol}@Sell'),
                'Buy': self._data.get(f'{symbol}@Buy')}

    def getlist(self) -> List[dict]:
        return list(self._data.values())
    
    def _key(self, item: dict) -> str:
        if item['symbol'].endswith('USD'):
            return item['symbol']
        elif item['symbol'].endswith('USDT'):
            symbol = item['symbol']
            side = item['side']
            return f'{symbol}@{side}'

    def _onwallet(self, coin: str, data: dict):
        keys = ['wallet_balance', 'available_balance']
        self._data[f'{coin}USD'].update({k: data[k] for k in keys})

    def _onresponse(self, data: Union[List[dict], dict]):
        _data = []
        if isinstance(data, dict):
            _data.append(data)
        elif isinstance(data, list):
            _data.extend(data)
        for item in _data:
            key = self._key(item)
            if key in self._data:
                self._data[key].update(item)
            else:
                self._data[key] = item

    def _onmessage(self, data: List[dict]):
        for item in data:
            key = self._key(item)
            if key in self._data:
                self._data[key].update(item)
            else:
                self._data[key] = item

class Execution:
    _MAX_RECORD = 5000

    def __init__(self):
        self._data = []

    def getexecutions(self, symbol: str) -> List[dict]:
        e = []
        for item in self._data:
            if item['symbol'] == symbol:
                e.append(item)
        return e

    def getlist(self) -> List[dict]:
        return list(self._data)

    def _onmessage(self, data: List[dict]):
        self._data.extend(data)
        if len(self._data) > self._MAX_RECORD:
            del self._data[:len(self._data) - self._MAX_RECORD]

class Order:
    _MAX_RECORD = 5000

    def __init__(self):
        self._data = {}

    def get(self, symbol: str, order_id: str) -> dict:
        return dict(self._data.get(f'{symbol}@{order_id}'))

    def getactive(self, symbol: str):
        return [item for item in self._data.values() if item['symbol'] == symbol and item['order_status'] in ('New', 'PartiallyFilled')]

    def getlist(self) -> List[dict]:
        return list(self._data.values())

    def _key(self, item: dict) -> str:
        symbol = item['symbol']
        order_id = item['order_id']
        return f'{symbol}@{order_id}'

    def _onresponse(self, data: List[dict]):
        if data is not None:
            self._onmessage(data)

    def _onmessage(self, data: List[dict]):
        for item in data:
            key = self._key(item)
            if key in self._data:
                self._data[key].update(item)
            else:
                self._data[key] = item
        while len(self._data) > self._MAX_RECORD:
            del self._data[next(iter(self._data))]

class StopOrder:
    def __init__(self):
        self._data = {}

    def get(self, symbol: str, stop_order_id: str) -> dict:
        return dict(self._data.get(f'{symbol}@{stop_order_id}'))

    def getactive(self, symbol: str):
        return [item for item in self._data.values() if item['symbol'] == symbol and item['stop_order_status'] in ('Untriggered', )]

    def getlist(self) -> List[dict]:
        return list(self._data.values())
    
    def _key(self, item: dict) -> str:
        symbol = item['symbol']
        stop_order_id = item['stop_order_id']
        return f'{symbol}@{stop_order_id}'

    def _onresponse(self, data: List[dict]):
        if data is not None:
            self._onmessage(data)

    def _onmessage(self, data: List[dict]):
        for item in data:
            if 'order_id' in item:
                item['stop_order_id'] = item.pop('order_id')
            if 'order_status' in item:
                item['stop_order_status'] = item.pop('order_status')
            key = self._key(item)
            if key in self._data:
                self._data[key].update(item)
            else:
                self._data[key] = item

class Wallet:
    def __init__(self):
        self._data = {}

    def get(self) -> dict:
        return dict(self._data)

    def _onresponse(self, data: dict):
        keys = ['wallet_balance', 'available_balance']
        self._onmessage([{k: data[k] for k in keys}])

    def _onmessage(self, data: List[dict]):
        for item in data:
            self._data.update(item)
