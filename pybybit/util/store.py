import json
import urllib.parse
from threading import Event
from typing import Any, Dict, List, Optional, Union
from requests import Response, Session
from websocket import WebSocket

class DataStore:
    def __init__(self) -> None:
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
        self._events: List[Event] = []

    def onresponse(self, resp: Response, session: Session) -> None:
        content: Dict[str, Any] = resp.json()
        if content.get('ret_code') == 0:
            # order
            if any([
                resp.request.path_url.startswith('/v2/private/order'),
                resp.request.path_url.startswith('/private/linear/order/search'),
                resp.request.path_url.startswith('/futures/private/order'),
            ]):
                if isinstance(content['result'], list):
                    self.order._onresponse(content['result'])
            # stoporder
            elif any([
                resp.request.path_url.startswith('/v2/private/stop-order'),
                resp.request.path_url.startswith('/private/linear/order/search'),
                resp.request.path_url.startswith('/futures/private/order'),
            ]):
                if isinstance(content['result'], list):
                    self.stoporder._onresponse(content['result'])
            # position
            elif any([
                resp.request.path_url.startswith('/v2/private/position/list'),
                resp.request.path_url.startswith('/futures/private/position/list'),
            ]):
                self.position.inverse._onresponse(content['result'])
            elif resp.request.path_url.startswith('/private/linear/position/list'):
                self.position.linear._onresponse(content['result'])
            # wallet
            elif resp.request.path_url.startswith('/v2/private/wallet/balance'):
                self.wallet._onresponse(content['result'])

    def onmessage(self, msg: str, ws: WebSocket) -> None:
        content: Dict[str, Any] = json.loads(msg)
        if 'topic' in content:
            topic: str = content['topic']
            data: Union[List[Item], Item] = content['data']
            type_: Optional[str] = content.get('type')
            if any([
                topic.startswith('orderBookL2_25'),
                topic.startswith('orderBook_200'),
            ]):
                self.orderbook._onmessage(type_, data)
            elif topic.startswith('trade'):
                self.trade._onmessage(data)
            elif topic.startswith('insurance'):
                self.insurance._onmessage(data)
            elif topic.startswith('instrument_info'):
                self.instrument._onmessage(type_, data)
            if any([
                topic.startswith('klineV2'),
                topic.startswith('candle'),
            ]):
                self.kline._onmessage(topic, data)
            elif topic == 'position':
                self.position._onmessage(data)
                self.wallet._onposition(data)
            elif topic == 'execution':
                self.execution._onmessage(data)
            elif topic == 'order':
                self.order._onmessage(data)
            elif topic == 'stop_order':
                self.stoporder._onmessage(data)
            elif topic == 'wallet':
                self.wallet._onmessage(data)
            for event in self._events:
                event.set()
            self._events.clear()

    def wait(self) -> None:
        event = Event()
        self._events.append(event)
        event.wait()

class DefaultDataStore(DataStore): ...

Item = Dict[str, Any]

class _KeyValueStore:
    _KEYS: List[str]
    _MAXLEN: Optional[int]

    def __init__(self) -> None:
        self._data: Dict[str, Item] = {}
        self._events: List[Event] = []
    
    def get(self, **kwargs) -> Optional[Item]:
        try:
            dumps = self._dumps(kwargs)
            if dumps in self._data:
                return self._data[dumps]
        except KeyError:
            if kwargs:
                for item in self._data.values():
                    for k, v, in kwargs.items():
                        if not k in item:
                            break
                        if v != item[k]:
                            break
                    else:
                        return item
            else:
                for item in self._data.values():
                    return item

    def getlist(self, **kwargs) -> List[Item]:
        if kwargs:
            result = []
            for item in self._data.values():
                for k, v in kwargs.items():
                    if not k in item:
                        break
                    if v != item[k]:
                        break
                else:
                    result.append(item)
            return result
        else:
            return list(self._data.values())

    def __len__(self):
        return len(self._data)

    def _dumps(self, item: Item) -> str:
        keyitem = {k: item[k] for k in self._KEYS}
        return urllib.parse.urlencode(keyitem)
    
    def _update(self, items: List[Item]) -> None:
        for item in items:
            try:
                key = self._dumps(item)
                if key in self._data:
                    self._data[key].update(item)
                else:
                    self._data[key] = item
            except KeyError:
                pass
        if self._MAXLEN is not None:
            len_data = len(self._data)
            if len_data > self._MAXLEN:
                over = len_data - self._MAXLEN
                keys = []
                for i, k in enumerate(self._data.keys()):
                    if i < over:
                        keys.append(k)
                    else:
                        break
                for k in keys:
                    self._data.pop(k)
        for event in self._events:
            event.set()
        self._events.clear()

    def _pop(self, items: List[Item]) -> None:
        for item in items:
            try:
                key = self._dumps(item)
                if key in self._data:
                    self._data.pop(key)
            except KeyError:
                pass
        for event in self._events:
            event.set()
        self._events.clear()

    def wait(self) -> None:
        event = Event()
        self._events.append(event)
        event.wait()

class OrderBook(_KeyValueStore):
    _KEYS = ['symbol', 'id', 'side']
    _MAXLEN = None

    def getbest(self, symbol: str) -> Dict[str, Optional[Item]]:
        result = {'Sell': {}, 'Buy': {}}
        for item in self._data.values():
            if item['symbol'] == symbol:
                result[item['side']][float(item['price'])] = item
        return {
            'Sell': result['Sell'][min(result['Sell'])] if result['Sell'] else None,
            'Buy': result['Buy'][max(result['Buy'])] if result['Buy'] else None
        }

    def getsorted(self, symbol: str) -> Dict[str, List[Item]]:
        result = {'Sell': [], 'Buy': []}
        for item in self._data.values():
            if item['symbol'] == symbol:
                result[item['side']].append(item)
        return {
            'Sell': sorted(result['Sell'], key=lambda x: float(x['price'])),
            'Buy': sorted(result['Buy'], key=lambda x: float(x['price']), reverse=True)
        }

    def _onmessage(self, type_: str, data: Union[List[Item], Item]) -> None:
        if type_ == 'snapshot':
            if isinstance(data, dict):
                data = data['order_book']
            self._update(data)
        elif type_ == 'delta':
            self._pop(data['delete'])
            self._update(data['update'])
            self._update(data['insert'])

class Trade(_KeyValueStore):
    _KEYS = ['trade_id']
    _MAXLEN = 10000

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Insurance(_KeyValueStore):
    _KEYS = ['currency']
    _MAXLEN = None

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Instrument(_KeyValueStore):
    _KEYS = ['symbol']
    _MAXLEN = None

    def _onmessage(self, type_: str, data: Item) -> None:
        if type_ == 'snapshot':
            self._update([data])
        elif type_ == 'delta':
            self._update(data['update'])

class Kline(_KeyValueStore):
    _KEYS = ['symbol', 'start']
    _MAXLEN = 5000

    def _onmessage(self, topic: str, data: List[Item]) -> None:
        symbol = topic.split('.')[2] # ex:'klineV2.1.BTCUSD'
        for item in data:
            item['symbol'] = symbol
        self._update(data)

class Position:
    def __init__(self):
        self.inverse = PositionInverse()
        self.linear = PositionLinear()
    
    def _onmessage(self, data: List[Item]) -> None:
        if len(data):
            symbol: str = data[0]['symbol']
            if symbol.endswith('USDT'):
                self.linear._onmessage(data)
            else:
                self.inverse._onmessage(data)

class PositionInverse(_KeyValueStore):
    _KEYS = ['symbol', 'position_idx']
    _MAXLEN = None
    
    def getone(self, symbol: str) -> Optional[Item]:
        return self.get(symbol=symbol, position_idx=0)

    def getboth(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            'Sell': self.get(symbol=symbol, position_idx=2),
            'Buy': self.get(symbol=symbol, position_idx=1),
        }

    def _onresponse(self, data: Union[Item, List[Item]]) -> None:
        if isinstance(data, dict):
            self._update([data])
        elif isinstance(data, list):
            if len(data) and 'data' in data[0]:
                self._update([item['data'] for item in data])
            else:
                self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class PositionLinear(_KeyValueStore):
    _KEYS = ['symbol', 'side']
    _MAXLEN = None

    def getboth(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            'Sell': self.get(symbol=symbol, side='Sell'),
            'Buy': self.get(symbol=symbol, side='Buy'),
        }

    def _onresponse(self, data: List[Item]) -> None:
        if len(data) and 'data' in data[0]:
            self._update([item['data'] for item in data])
        else:
            self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Execution(_KeyValueStore):
    _KEYS = ['exec_id']
    _MAXLEN = 5000

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Order(_KeyValueStore):
    _KEYS = ['order_id']
    _MAXLEN = None

    def _onresponse(self, data: List[Item]) -> None:
        self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if item['order_status'] in ('Created', 'New', 'PartiallyFilled', ):
                self._update([item])
            else:
                self._pop([item])

class StopOrder(_KeyValueStore):
    _KEYS = ['stop_order_id']
    _MAXLEN = None

    def _onresponse(self, data: List[Item]) -> None:
        self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if 'order_id' in item:
                item['stop_order_id'] = item.pop('order_id')
            if 'order_status' in item:
                item['stop_order_status'] = item.pop('order_status')
            if item['stop_order_status'] in ('Active', 'Untriggered', ):
                self._update([item])
            else:
                self._pop([item])

class Wallet(_KeyValueStore):
    _KEYS = ['coin']
    _MAXLEN = None

    def _onresponse(self, data: Dict[str, Item]) -> None:
        for coin, item in data.items():
            _item = {}
            _item['coin'] = coin
            _item['wallet_balance'] = item['wallet_balance']
            _item['available_balance'] = item['available_balance']
            self._update([_item])

    def _onposition(self, data: List[Item]) -> None:
        if len(data) and 'position_idx' in data[0]:
            for item in data:
                _item = {}
                symbol: str = item['symbol']
                if symbol.endswith('USD'):
                    _item['coin'] = symbol[:-3] # ex:'BTCUSD'
                else:
                    _item['coin'] = symbol[:-6] # ex:'BTCUSDM21'
                _item['wallet_balance'] = item['wallet_balance']
                _item['available_balance'] = item['available_balance']
                self._update([_item])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            _item = {}
            _item['coin'] = 'USDT'
            _item['wallet_balance'] = item['wallet_balance']
            _item['available_balance'] = item['available_balance']
            self._update([item])
