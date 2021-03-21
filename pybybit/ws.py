import time
import websocket
from threading import Thread

class WebScoketAPI:
    _MAINNET_INVERSE = 'wss://stream.bybit.com/realtime'
    _TESTNET_INVERSE = 'wss://stream-testnet.bybit.com/realtime'
    _MAINNET_LINEAR_PUBLIC = 'wss://stream.bybit.com/realtime_public'
    _MAINNET_LINEAR_PRIVATE = 'wss://stream.bybit.com/realtime_private'
    _TESTNET_LINEAR_PUBLIC = 'wss://stream-testnet.bybit.com/realtime_public'
    _TESTNET_LINEAR_PRIVATE = 'wss://stream-testnet.bybit.com/realtime_private'
    _COMMAND = '{{"op":"{op}","args":[{args}]}}'
    _ORDERBOOKL2_25 = 'orderBookL2_25'
    _ORDERBOOK_200 = 'orderBook_200.100ms'
    _TRADE = 'trade'
    _INSURANCE = 'insurance'
    _INSTRUMENT_INFO = 'instrument_info.100ms'
    _KLINEV2 = 'klineV2'
    _CANDLE = 'candle'
    _POSITION = 'position'
    _EXECUTION = 'execution'
    _ORDER = 'order'
    _STOPORDER = 'stop_order'
    _WALLET = 'wallet'
    _PUBLIC_TOPICS = [_ORDERBOOKL2_25, _ORDERBOOK_200, _TRADE, _INSTRUMENT_INFO, _KLINEV2, _CANDLE]
    _PRIVATE_TOPICS = [_POSITION, _EXECUTION, _ORDER, _STOPORDER, _WALLET]
    _HEARTBEAT_SEC = 60.0
    _MINRECONECT_SEC = 60.0

    def __init__(self, auth, testnet) -> None:
        self._auth = auth
        self._testnet = testnet
        self._callbacks = []

    def _subscribe(self, topics: list, ws: websocket.WebSocket) -> None:
        args = ','.join(f'"{t}"' for t in topics)
        cmd = self._COMMAND.format(op='subscribe', args=args)
        ws.send(cmd)

    def _onmessage(self, ws: websocket.WebSocket) -> None:
        Thread(target=self._heartbeat, args=[ws], daemon=True).start()
        while True:
            msg: str = ws.recv()
            for cb in self._callbacks:
                cb(msg, ws)

    def _heartbeat(self, ws: websocket.WebSocket) -> None:
        while True:
            time.sleep(self._HEARTBEAT_SEC)
            try:
                ws.send('{"op":"ping"}')
            except BrokenPipeError:
                break

    def _loop(self, wsurl: str, topics: list) -> None:
        while True:
            t = time.time()
            try:
                if any(t in self._PRIVATE_TOPICS for t in topics):
                    param = self._auth._wssign()
                    wsurl += f'?{param}'
                ws = websocket.create_connection(wsurl)
                self._subscribe(topics, ws)
                self._onmessage(ws)
            except websocket.WebSocketException:
                pass
            except ConnectionResetError:
                pass
            except KeyboardInterrupt:
                break
            time.sleep(max(self._MINRECONECT_SEC - (time.time() - t), 0))

    def add_callback(self, func) -> None:
        if callable(func):
            self._callbacks.append(func)

    def run_forever_inverse(self, topics: list) -> None:
        wsurl = self._MAINNET_INVERSE if not self._testnet else self._TESTNET_INVERSE
        Thread(target=self._loop, args=[wsurl, topics], daemon=True).start()

    def run_forever_linear_public(self, topics: list) -> None:
        wsurl = self._MAINNET_LINEAR_PUBLIC if not self._testnet else self._TESTNET_LINEAR_PUBLIC
        Thread(target=self._loop, args=[wsurl, topics], daemon=True).start()

    def run_forever_linear_private(self, topics: list) -> None:
        wsurl = self._MAINNET_LINEAR_PRIVATE if not self._testnet else self._TESTNET_LINEAR_PRIVATE
        Thread(target=self._loop, args=[wsurl, topics], daemon=True).start()
