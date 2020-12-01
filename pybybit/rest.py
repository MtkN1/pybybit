import requests

class RESTAPI:
    _MAINNET = 'https://api.bybit.com'
    _TESTNET = 'https://api-testnet.bybit.com'

    def __init__(self, auth, testnet):
        self._session = requests.Session()
        self._auth = auth
        self._url = self._MAINNET if not testnet else self._TESTNET
        self._callbacks = []
        self.inverse = Inverse(self._request)
        self.linear = Linear(self._request)

    def _prepare(self, method: str, url: str, query: dict, private: bool) -> dict:
        for k in list(query):
            if query[k] is None:
                del query[k]
        if private:
            query = self._auth._prepare(query)
        query_str = '&'.join(f'{k}={v}' for k, v in query.items())
        if private:
            sign = self._auth._sign(query_str)
            query_str += f'&{sign}'
        req_args = {'method': method, 'url': url}
        if method == 'GET':
            if len(query_str) > 0:
                req_args['url'] += f'?{query_str}'
        else: # method == 'POST' or other
            req_args['data'] = query_str
            req_args['headers'] = {'Content-Type': 'application/x-www-form-urlencoded'}
        return req_args

    def _request(self, method: str, path: str, query: dict, private: bool) -> requests.Response:
        req_args = self._prepare(method, self._url + path, query, private)
        resp = self._session.request(**req_args)
        for cb in self._callbacks:
            cb(resp, self._session)
        return resp

    def add_callback(self, func) -> None:
        if callable(func):
            self._callbacks.append(func)

    def initialize_request_inverse(self, symbol: str):
        return (
            self.inverse.private_order_list(symbol=symbol, order_status='New,PartiallyFilled'),
            self.inverse.private_stoporder_list(symbol=symbol, stop_order_status='Untriggered'),
            self.inverse.private_position_list(symbol=symbol),
            self.inverse.private_wallet_balance(coin=symbol.replace('USD', '')),
        )

    def initialize_request_linear(self, symbol: str):
        return (
            self.linear.private_order_list(symbol=symbol, order_status='New'),
            self.linear.private_stoporder_list(symbol=symbol, stop_order_status='Untriggered'),
            self.linear.private_position_list(symbol=symbol),
            self.inverse.private_wallet_balance(coin='USDT'),
        )

class Inverse:
    def __init__(self, request: RESTAPI._request):
        self._request = request

    def public_orderbook_l2(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/public/orderBook/L2'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=False)

    def public_kline_list(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/v2/public/kline/list'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def public_tickers(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/public/tickers'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=False)

    def public_tradingrecords(
        self,
        symbol: str=None,
        from_: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/v2/public/trading-records'
        query = {
            'symbol': symbol,
            'from': from_,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def public_symbols(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/public/symbols'
        query = {}
        return self._request(method, path, query, private=False)

    def public_markpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/v2/public/mark-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def private_order_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: int=None,
        price: float=None,
        time_in_force: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        reduce_only: bool=None,
        close_on_trigger: bool=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/v2/private/order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'time_in_force': time_in_force,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'reduce_only': reduce_only,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_order_list(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        order: str=None,
        page: int=None,
        limit: int=None,
        order_status: str=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/order/list'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'order': order,
            'page': page,
            'limit': limit,
            'order_status': order_status
        }
        return self._request(method, path, query, private=True)

    def private_order_cancel(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/v2/private/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_order_cancelall(
        self,
        symbol: str=None) -> requests.Response:
        method = 'POST'
        path = '/v2/private/order/cancelAll'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_order_replace(
        self,
        order_id: str=None,
        symbol: str=None,
        p_r_qty: int=None,
        p_r_price: float=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/order/replace'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price
        }
        return self._request(method, path, query, private=True)

    def private_order_search(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/private/order'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: int=None,
        price: float=None,
        base_price: float=None,
        stop_px: float=None,
        time_in_force: str=None,
        trigger_by: str=None,
        close_on_trigger: bool=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/stop-order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'base_price': base_price,
            'stop_px': stop_px,
            'time_in_force': time_in_force,
            'trigger_by': trigger_by,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_list(
        self,
        stop_order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        stop_order_status: str=None,
        order: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/stop-order/list'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'order': order,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancel(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancelall(
        self,
        symbol: str=None) -> requests.Response:
        method = 'POST'
        path = '/v2/private/stop-order/cancelAll'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_replace(
        self,
        stop_order_id: str=None,
        symbol: str=None,
        p_r_qty: int=None,
        p_r_price: float=None,
        p_r_trigger_price: float=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/stop-order/replace'
        query = {
            'stop_order_id': stop_order_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_trigger_price': p_r_trigger_price
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_search(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/private/stop-order'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_position_list(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/private/position/list'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_changepositionmargin(
        self,
        symbol: str=None,
        margin: int=None) -> requests.Response:
        method = 'POST'
        path = '/position/change-position-margin'
        query = {
            'symbol': symbol,
            'margin': margin,
        }
        return self._request(method, path, query, private=True)

    def private_tradingstop(
        self,
        symbol: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        trailing_stop: float=None,
        new_trailing_active: float=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/position/trading-stop'
        query = {
            'symbol': symbol,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'new_trailing_active': new_trailing_active
        }
        return self._request(method, path, query, private=True)

    def private_leverage(
        self) -> requests.Response:
        method = 'GET'
        path = '/user/leverage'
        query = {}
        return self._request(method, path, query, private=True)

    def private_leverage_save(
        self,
        symbol: str=None,
        leverage: float=None) -> requests.Response:
        method = 'POST'
        path = '/user/leverage/save'
        query = {
            'symbol': symbol,
            'leverage': leverage
        }
        return self._request(method, path, query, private=True)

    def private_execution_list(
        self,
        order_id: str=None,
        symbol: str=None,
        start_time: int=None,
        page: int=None,
        limit: int=None,
        order: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/private/execution/list'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'start_time': start_time,
            'page': page,
            'limit': limit,
            'order': order
        }
        return self._request(method, path, query, private=True)

    def private_risklimit_list(
        self) -> requests.Response:
        method = 'GET'
        path = '/open-api/wallet/risk-limit/list'
        query = {}
        return self._request(method, path, query, private=True)

    def private_risklimit(
        self,
        symbol: str=None,
        risk_id: int=None) -> requests.Response:
        method = 'POST'
        path = '/open-api/wallet/risk-limit'
        query = {
            'symbol': symbol,
            'risk_id': risk_id,
        }
        return self._request(method, path, query, private=True)

    def private_prevfundingrate(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/funding/prev-funding-rate'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_prevfunding(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/funding/prev-funding'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_predictedfunding(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/funding/predicted-funding'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_apikey(
        self) -> requests.Response:
        method = 'GET'
        path = '/open-api/api-key'
        query = {}
        return self._request(method, path, query, private=True)

    def private_lcp(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/private/account/lcp'
        query = {}
        return self._request(method, path, query, private=True)

    def private_wallet_balance(
        self,
        coin: str=None) -> requests.Response:
        method = 'GET'
        path = '/v2/private/wallet/balance'
        query = {
            'coin': coin
        }
        return self._request(method, path, query, private=True)

    def private_wallet_fund_records(
        self,
        start_date: str=None,
        end_date: str=None,
        currency: str=None,
        coin: str=None,
        wallet_fund_type: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/wallet/fund/records'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'currency': currency,
            'coin': coin,
            'wallet_fund_type': wallet_fund_type,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def private_wallet_withdraw_list(
        self,
        start_date: str=None,
        end_date: str=None,
        coin: str=None,
        status: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/open-api/wallet/withdraw/list'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'coin': coin,
            'status': status,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def public_time(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/public/time'
        query = {}
        return self._request(method, path, query, private=False)

    def public_announcement(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/public/announcement'
        query = {}
        return self._request(method, path, query, private=False)

class Linear:
    def __init__(self, request: RESTAPI._request):
        self._request = request

    def public_kline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/public/linear/kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def public_recenttradingrecords(
        self,
        symbol: str=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/public/linear/recent-trading-records'
        query = {
            'symbol': symbol,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def public_prevfundingrate(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/public/linear/funding/prev-funding-rate'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=False)

    def public_markpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/public/linear/mark-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit
        }
        return self._request(method, path, query, private=False)

    def private_order_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: int=None,
        price: float=None,
        time_in_force: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: bool=None,
        sl_trigger_by: bool=None,
        reduce_only: bool=None,
        close_on_trigger: bool=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'time_in_force': time_in_force,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
            'reduce_only': reduce_only,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_order_list(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        order: str=None,
        page: int=None,
        limit: int=None,
        order_status: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/order/list'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'order': order,
            'page': page,
            'limit': limit,
            'order_status': order_status
        }
        return self._request(method, path, query, private=True)

    def private_order_cancel(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_order_cancelall(
        self,
        symbol: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/order/cancel-all'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_order_search(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/order/search'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: int=None,
        price: float=None,
        base_price: float=None,
        stop_px: float=None,
        time_in_force: str=None,
        trigger_by: str=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
        reduce_only: bool=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/stop-order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'base_price': base_price,
            'stop_px': stop_px,
            'time_in_force': time_in_force,
            'trigger_by': trigger_by,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id,
            'reduce_only': reduce_only
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_list(
        self,
        stop_order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        stop_order_status: str=None,
        order: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/stop-order/list'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'order': order,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancel(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancelall(
        self,
        symbol: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/stop-order/cancel-all'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_search(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/stop-order/search'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._request(method, path, query, private=True)

    def private_position_list(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/position/list'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def private_setautoaddmargin(
        self,
        symbol: str=None,
        side: str=None,
        auto_add_margin: bool=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/position/set-auto-add-margin'
        query = {
            'symbol': symbol,
            'side': side,
            'auto_add_margin': auto_add_margin
        }
        return self._request(method, path, query, private=True)

    def private_setleverage(
        self,
        symbol: str=None,
        buy_leverage: float=None,
        sell_leverage: float=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/position/set-leverage'
        query = {
            'symbol': symbol,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage
        }
        return self._request(method, path, query, private=True)

    def private_switchisolated(
        self,
        symbol: str=None,
        is_isolated: bool=None,
        buy_leverage: float=None,
        sell_leverage: float=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/position/switch-isolated'
        query = {
            'symbol': symbol,
            'is_isolated': is_isolated,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage
        }
        return self._request(method, path, query, private=True)

    def private_tradingstop(
        self,
        symbol: str=None,
        side: str=None,
        take_profit: str=None,
        stop_loss: str=None,
        trailing_stop: str=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/position/trading-stop'
        query = {
            'symbol': symbol,
            'side': side,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by
        }
        return self._request(method, path, query, private=True)

    def private_addmargin(
        self,
        symbol: str=None,
        side: str=None,
        margin: int=None) -> requests.Response:
        method = 'POST'
        path = '/private/linear/position/add-margin'
        query = {
            'symbol': symbol,
            'side': side,
            'margin': margin,
        }
        return self._request(method, path, query, private=True)

    def private_execution_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/trade/execution/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def private_closedpnl_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/trade/closed-pnl/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit
        }
        return self._request(method, path, query, private=True)

    def public_risklimit(
        self) -> requests.Response:
        method = 'GET'
        path = '/public/linear/risk-limit'
        query = {}
        return self._request(method, path, query, private=False)

    def private_prevfunding(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/funding/prev-funding'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def get_predictedfunding(
        self,
        symbol: str=None) -> requests.Response:
        method = 'GET'
        path = '/private/linear/funding/predicted-funding'
        query = {
            'symbol': symbol
        }
        return self._request(method, path, query, private=True)

    def public_time(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/public/time'
        query = {}
        return self._request(method, path, query, private=False)

    def public_announcement(
        self) -> requests.Response:
        method = 'GET'
        path = '/v2/public/announcement'
        query = {}
        return self._request(method, path, query, private=False)
