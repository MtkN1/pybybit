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
        self.futures = Futures(self._request)

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
            self.inverse.private_order(symbol=symbol),
            self.inverse.private_stoporder(symbol=symbol),
            self.inverse.private_position_list(symbol=symbol),
            self.inverse.private_wallet_balance(),
        )

    def initialize_request_linear(self, symbol: str):
        return (
            self.linear.private_order_search(symbol=symbol),
            self.linear.private_stoporder_search(symbol=symbol),
            self.linear.private_position_list(symbol=symbol),
            self.inverse.private_wallet_balance(),
        )

    def initialize_request_futures(self, symbol: str):
        return (
            self.futures.private_order(symbol=symbol),
            self.futures.private_stoporder(symbol=symbol),
            self.futures.private_position_list(symbol=symbol),
            self.inverse.private_wallet_balance(),
        )

class Inverse:
    def __init__(self, request: RESTAPI._request):
        self._request = request

    def public_orderbook_l2(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Order book
        """
        method = 'GET'
        path = '/v2/public/orderBook/L2'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def public_kline_list(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Kline
        """
        method = 'GET'
        path = '/v2/public/kline/list'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_tickers(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Latest Information for Symbol
        """
        method = 'GET'
        path = '/v2/public/tickers'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def public_tradingrecords(
        self,
        symbol: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Public Trading Records
        """
        method = 'GET'
        path = '/v2/public/trading-records'
        query = {
            'symbol': symbol,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_symbols(
        self,
    ) -> requests.Response:
        """
        Query Symbol
        """
        method = 'GET'
        path = '/v2/public/symbols'
        query = {
        }
        return self._request(method, path, query, private=False)

    def public_liqrecords(
        self,
        symbol: str=None,
        from_: int=None,
        limit: int=None,
        start_time: int=None,
        end_time: int=None,
    ) -> requests.Response:
        """
        Liquidated Orders
        """
        method = 'GET'
        path = '/v2/public/liq-records'
        query = {
            'symbol': symbol,
            'from': from_,
            'limit': limit,
            'start_time': start_time,
            'end_time': end_time,
        }
        return self._request(method, path, query, private=False)

    def public_markpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Mark Price Kline
        """
        method = 'GET'
        path = '/v2/public/mark-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_indexpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Index Price Kline
        """
        method = 'GET'
        path = '/v2/public/index-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_premiumindexkline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Premium Index Kline
        """
        method = 'GET'
        path = '/v2/public/premium-index-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_openinterest(
        self,
        symbol: str=None,
        period: str=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Open Interest
        """
        method = 'GET'
        path = '/v2/public/open-interest'
        query = {
            'symbol': symbol,
            'period': period,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_bigdeal(
        self,
        symbol: str=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Latest Big Deal
        """
        method = 'GET'
        path = '/v2/public/big-deal'
        query = {
            'symbol': symbol,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_accountratio(
        self,
        symbol: str=None,
        period: str=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Long-Short Ratio
        """
        method = 'GET'
        path = '/v2/public/account-ratio'
        query = {
            'symbol': symbol,
            'period': period,
            'limit': limit,
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
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
        reduce_only: bool=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Place Active Order
        """
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
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
            'reduce_only': reduce_only,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_order_list(
        self,
        symbol: str=None,
        order_status: str=None,
        direction: str=None,
        limit: int=None,
        cursor: str=None,
    ) -> requests.Response:
        """
        Get Active Order
        """
        method = 'GET'
        path = '/v2/private/order/list'
        query = {
            'symbol': symbol,
            'order_status': order_status,
            'direction': direction,
            'limit': limit,
            'cursor': cursor,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancel(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Active Order
        """
        method = 'POST'
        path = '/v2/private/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Active Orders
        """
        method = 'POST'
        path = '/v2/private/order/cancelAll'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_order_replace(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: str=None,
        p_r_price: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Active Order
        """
        method = 'POST'
        path = '/v2/private/order/replace'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_order(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Query Active Order (real-time)
        """
        method = 'GET'
        path = '/v2/private/order'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: str=None,
        price: str=None,
        base_price: str=None,
        stop_px: str=None,
        time_in_force: str=None,
        trigger_by: str=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Place Conditional Order
        """
        method = 'POST'
        path = '/v2/private/stop-order/create'
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
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_list(
        self,
        symbol: str=None,
        stop_order_status: str=None,
        direction: str=None,
        limit: int=None,
        cursor: str=None,
    ) -> requests.Response:
        """
        Get Conditional Order
        """
        method = 'GET'
        path = '/v2/private/stop-order/list'
        query = {
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'direction': direction,
            'limit': limit,
            'cursor': cursor,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancel(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Conditional Order
        """
        method = 'POST'
        path = '/v2/private/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Conditional Orders
        """
        method = 'POST'
        path = '/v2/private/stop-order/cancelAll'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_replace(
        self,
        stop_order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: int=None,
        p_r_price: str=None,
        p_r_trigger_price: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Conditional Order
        """
        method = 'POST'
        path = '/v2/private/stop-order/replace'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'p_r_trigger_price': p_r_trigger_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Query Conditional Order (real-time)
        """
        method = 'GET'
        path = '/v2/private/stop-order'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_position_list(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        My Position
        """
        method = 'GET'
        path = '/v2/private/position/list'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_position_changepositionmargin(
        self,
        symbol: str=None,
        margin: str=None,
    ) -> requests.Response:
        """
        Change Margin
        """
        method = 'POST'
        path = '/v2/private/position/change-position-margin'
        query = {
            'symbol': symbol,
            'margin': margin,
        }
        return self._request(method, path, query, private=True)

    def private_position_tradingstop(
        self,
        symbol: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        trailing_stop: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
        new_trailing_active: float=None,
        sl_size: float=None,
        tp_size: float=None,
    ) -> requests.Response:
        """
        Set Trading-Stop
        """
        method = 'POST'
        path = '/v2/private/position/trading-stop'
        query = {
            'symbol': symbol,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
            'new_trailing_active': new_trailing_active,
            'sl_size': sl_size,
            'tp_size': tp_size,
        }
        return self._request(method, path, query, private=True)

    def private_position_leverage_save(
        self,
        symbol: str=None,
        leverage: float=None,
    ) -> requests.Response:
        """
        Set Leverage
        """
        method = 'POST'
        path = '/v2/private/position/leverage/save'
        query = {
            'symbol': symbol,
            'leverage': leverage,
        }
        return self._request(method, path, query, private=True)

    def private_execution_list(
        self,
        order_id: str=None,
        symbol: str=None,
        start_time: int=None,
        page: int=None,
        limit: int=None,
        order: str=None,
    ) -> requests.Response:
        """
        User Trade Records
        """
        method = 'GET'
        path = '/v2/private/execution/list'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'start_time': start_time,
            'page': page,
            'limit': limit,
            'order': order,
        }
        return self._request(method, path, query, private=True)

    def private_trade_closedpnl_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Closed Profit and Loss
        """
        method = 'GET'
        path = '/v2/private/trade/closed-pnl/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_tpsl_switchmode(
        self,
        symbol: str=None,
        tp_sl_mode: str=None,
    ) -> requests.Response:
        """
        Full/Partial Position SL/TP Switch
        """
        method = 'POST'
        path = '/v2/private/tpsl/switch-mode'
        query = {
            'symbol': symbol,
            'tp_sl_mode': tp_sl_mode,
        }
        return self._request(method, path, query, private=True)

    def private_position_switchisolated(
        self,
        symbol: str=None,
        is_isolated: bool=None,
        buy_leverage: float=None,
        sell_leverage: float=None,
    ) -> requests.Response:
        """
        Cross/Isolated Margin Switch
        """
        method = 'POST'
        path = '/v2/private/position/switch-isolated'
        query = {
            'symbol': symbol,
            'is_isolated': is_isolated,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage,
        }
        return self._request(method, path, query, private=True)

    def public_risklimit_list(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Get Risk Limit
        """
        method = 'GET'
        path = '/v2/public/risk-limit/list'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def private_position_risklimit(
        self,
        symbol: str=None,
        risk_id: int=None,
    ) -> requests.Response:
        """
        Set Risk Limit
        """
        method = 'POST'
        path = '/v2/private/position/risk-limit'
        query = {
            'symbol': symbol,
            'risk_id': risk_id,
        }
        return self._request(method, path, query, private=True)

    def public_funding_prevfundingrate(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Get the Last Funding Rate
        """
        method = 'GET'
        path = '/v2/public/funding/prev-funding-rate'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def private_funding_prevfunding(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        My Last Funding Fee
        """
        method = 'GET'
        path = '/v2/private/funding/prev-funding'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_funding_predictedfunding(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Predicted Funding Rate and My Funding Fee
        """
        method = 'GET'
        path = '/v2/private/funding/predicted-funding'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_account_apikey(
        self,
    ) -> requests.Response:
        """
        API Key Info
        """
        method = 'GET'
        path = '/v2/private/account/api-key'
        query = {
        }
        return self._request(method, path, query, private=True)

    def private_account_lcp(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        LCP Info
        """
        method = 'GET'
        path = '/v2/private/account/lcp'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_wallet_balance(
        self,
        coin: str=None,
    ) -> requests.Response:
        """
        Get Wallet Balance
        """
        method = 'GET'
        path = '/v2/private/wallet/balance'
        query = {
            'coin': coin,
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
        limit: int=None,
    ) -> requests.Response:
        """
        Wallet Fund Records
        """
        method = 'GET'
        path = '/v2/private/wallet/fund/records'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'currency': currency,
            'coin': coin,
            'wallet_fund_type': wallet_fund_type,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_wallet_withdraw_list(
        self,
        start_date: str=None,
        end_date: str=None,
        coin: str=None,
        status: str=None,
        page: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Withdraw Records
        """
        method = 'GET'
        path = '/v2/private/wallet/withdraw/list'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'coin': coin,
            'status': status,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_exchangeorder_list(
        self,
        limit: int=None,
        from_: int=None,
        direction: str=None,
    ) -> requests.Response:
        """
        Asset Exchange Records
        """
        method = 'GET'
        path = '/v2/private/exchange-order/list'
        query = {
            'limit': limit,
            'from': from_,
            'direction': direction,
        }
        return self._request(method, path, query, private=True)

    def public_time(
        self,
    ) -> requests.Response:
        """
        Server Time
        """
        method = 'GET'
        path = '/v2/public/time'
        query = {
        }
        return self._request(method, path, query, private=False)

    def public_announcement(
        self,
    ) -> requests.Response:
        """
        Announcement
        """
        method = 'GET'
        path = '/v2/public/announcement'
        query = {
        }
        return self._request(method, path, query, private=False)

class Linear:
    def __init__(self, request: RESTAPI._request):
        self._request = request

    def public_kline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Kline
        """
        method = 'GET'
        path = '/public/linear/kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_recenttradingrecords(
        self,
        symbol: str=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Public Trading Records
        """
        method = 'GET'
        path = '/public/linear/recent-trading-records'
        query = {
            'symbol': symbol,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_funding_prevfundingrate(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Get the Last Funding Rate
        """
        method = 'GET'
        path = '/public/linear/funding/prev-funding-rate'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def public_markpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Mark Price Kline
        """
        method = 'GET'
        path = '/public/linear/mark-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_indexpricekline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Index Price Kline
        """
        method = 'GET'
        path = '/public/linear/index-price-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def public_premiumindexkline(
        self,
        symbol: str=None,
        interval: str=None,
        from_: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Query Premium Index Kline
        """
        method = 'GET'
        path = '/public/linear/premium-index-kline'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_,
            'limit': limit,
        }
        return self._request(method, path, query, private=False)

    def private_order_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: float=None,
        price: float=None,
        time_in_force: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
        reduce_only: bool=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Place Active Order
        """
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
            'order_link_id': order_link_id,
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
        order_status: str=None,
    ) -> requests.Response:
        """
        Get Active Order
        """
        method = 'GET'
        path = '/private/linear/order/list'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'order': order,
            'page': page,
            'limit': limit,
            'order_status': order_status,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancel(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Active Order
        """
        method = 'POST'
        path = '/private/linear/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Active Orders
        """
        method = 'POST'
        path = '/private/linear/order/cancel-all'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_order_replace(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: str=None,
        p_r_price: float=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Active Order
        """
        method = 'POST'
        path = '/private/linear/order/replace'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_order_search(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
    ) -> requests.Response:
        """
        Query Active Order (real-time)
        """
        method = 'GET'
        path = '/private/linear/order/search'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_create(
        self,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: float=None,
        price: float=None,
        base_price: float=None,
        stop_px: float=None,
        time_in_force: str=None,
        trigger_by: str=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
        reduce_only: bool=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Place Conditional Order
        """
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
            'reduce_only': reduce_only,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
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
        limit: int=None,
    ) -> requests.Response:
        """
        Get Conditional Order
        """
        method = 'GET'
        path = '/private/linear/stop-order/list'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'order': order,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancel(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Conditional Order
        """
        method = 'POST'
        path = '/private/linear/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Conditional Orders
        """
        method = 'POST'
        path = '/private/linear/stop-order/cancel-all'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_replace(
        self,
        stop_order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: str=None,
        p_r_price: float=None,
        p_r_trigger_price: float=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Conditional Order
        """
        method = 'POST'
        path = '/private/linear/stop-order/replace'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'p_r_trigger_price': p_r_trigger_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_search(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Query Conditional Order (real-time)
        """
        method = 'GET'
        path = '/private/linear/stop-order/search'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_position_list(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        My Position
        """
        method = 'GET'
        path = '/private/linear/position/list'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_position_setautoaddmargin(
        self,
        symbol: str=None,
        side: str=None,
        auto_add_margin: bool=None,
    ) -> requests.Response:
        """
        Set Auto Add Margin
        """
        method = 'POST'
        path = '/private/linear/position/set-auto-add-margin'
        query = {
            'symbol': symbol,
            'side': side,
            'auto_add_margin': auto_add_margin,
        }
        return self._request(method, path, query, private=True)

    def private_position_switchisolated(
        self,
        symbol: str=None,
        is_isolated: bool=None,
        buy_leverage: float=None,
        sell_leverage: float=None,
    ) -> requests.Response:
        """
        Cross/Isolated Margin Switch
        """
        method = 'POST'
        path = '/private/linear/position/switch-isolated'
        query = {
            'symbol': symbol,
            'is_isolated': is_isolated,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage,
        }
        return self._request(method, path, query, private=True)

    def private_tpsl_switchmode(
        self,
        symbol: str=None,
        tp_sl_mode: str=None,
    ) -> requests.Response:
        """
        Full/Partial Position SL/TP Switch
        """
        method = 'POST'
        path = '/private/linear/tpsl/switch-mode'
        query = {
            'symbol': symbol,
            'tp_sl_mode': tp_sl_mode,
        }
        return self._request(method, path, query, private=True)

    def private_position_addmargin(
        self,
        symbol: str=None,
        side: str=None,
        margin: float=None,
    ) -> requests.Response:
        """
        Add/Reduce Margin
        """
        method = 'POST'
        path = '/private/linear/position/add-margin'
        query = {
            'symbol': symbol,
            'side': side,
            'margin': margin,
        }
        return self._request(method, path, query, private=True)

    def private_position_setleverage(
        self,
        symbol: str=None,
        buy_leverage: float=None,
        sell_leverage: float=None,
    ) -> requests.Response:
        """
        Set Leverage
        """
        method = 'POST'
        path = '/private/linear/position/set-leverage'
        query = {
            'symbol': symbol,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage,
        }
        return self._request(method, path, query, private=True)

    def private_position_tradingstop(
        self,
        symbol: str=None,
        side: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        trailing_stop: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
        sl_size: float=None,
        tp_size: float=None,
    ) -> requests.Response:
        """
        Set Trading-Stop
        """
        method = 'POST'
        path = '/private/linear/position/trading-stop'
        query = {
            'symbol': symbol,
            'side': side,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
            'sl_size': sl_size,
            'tp_size': tp_size,
        }
        return self._request(method, path, query, private=True)

    def private_trade_execution_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        User Trade Records
        """
        method = 'GET'
        path = '/private/linear/trade/execution/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_trade_closedpnl_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Closed Profit and Loss
        """
        method = 'GET'
        path = '/private/linear/trade/closed-pnl/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def public_risklimit(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Get Risk Limit
        """
        method = 'GET'
        path = '/public/linear/risk-limit'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=False)

    def private_position_setrisk(
        self,
        symbol: str=None,
        side: str=None,
        risk_id: int=None,
    ) -> requests.Response:
        """
        Set Risk Limit
        """
        method = 'POST'
        path = '/private/linear/position/set-risk'
        query = {
            'symbol': symbol,
            'side': side,
            'risk_id': risk_id,
        }
        return self._request(method, path, query, private=True)

    def private_funding_predictedfunding(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Predicted Funding Rate and My Funding Fee
        """
        method = 'GET'
        path = '/private/linear/funding/predicted-funding'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_funding_prevfunding(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        My Last Funding Fee
        """
        method = 'GET'
        path = '/private/linear/funding/prev-funding'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def public_time(
        self,
    ) -> requests.Response:
        """
        Server Time
        """
        method = 'GET'
        path = '/v2/public/time'
        query = {
        }
        return self._request(method, path, query, private=False)

    def public_announcement(
        self,
    ) -> requests.Response:
        """
        Announcement
        """
        method = 'GET'
        path = '/v2/public/announcement'
        query = {
        }
        return self._request(method, path, query, private=False)

class Futures:
    def __init__(self, request: RESTAPI._request):
        self._request = request

    def private_order_create(
        self,
        position_idx: int=None,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: int=None,
        price: float=None,
        time_in_force: str=None,
        reduce_only: bool=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Place Active Order
        """
        method = 'POST'
        path = '/futures/private/order/create'
        query = {
            'position_idx': position_idx,
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'time_in_force': time_in_force,
            'reduce_only': reduce_only,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_order_list(
        self,
        symbol: str=None,
        order_status: str=None,
        direction: str=None,
        limit: int=None,
        cursor: str=None,
    ) -> requests.Response:
        """
        Get Active Order
        """
        method = 'GET'
        path = '/futures/private/order/list'
        query = {
            'symbol': symbol,
            'order_status': order_status,
            'direction': direction,
            'limit': limit,
            'cursor': cursor,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancel(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Active Order
        """
        method = 'POST'
        path = '/futures/private/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_order_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Active Orders
        """
        method = 'POST'
        path = '/futures/private/order/cancelAll'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_order_replace(
        self,
        order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: str=None,
        p_r_price: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Active Order
        """
        method = 'POST'
        path = '/futures/private/order/replace'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_order(
        self,
        symbol: str=None,
        order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Query Active Order (real-time)
        """
        method = 'GET'
        path = '/futures/private/order'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_create(
        self,
        position_idx: int=None,
        side: str=None,
        symbol: str=None,
        order_type: str=None,
        qty: str=None,
        price: str=None,
        base_price: str=None,
        stop_px: str=None,
        time_in_force: str=None,
        trigger_by: str=None,
        close_on_trigger: bool=None,
        order_link_id: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Place Conditional Order
        """
        method = 'POST'
        path = '/futures/private/stop-order/create'
        query = {
            'position_idx': position_idx,
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
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_list(
        self,
        symbol: str=None,
        stop_order_status: str=None,
        direction: str=None,
        limit: int=None,
        cursor: str=None,
    ) -> requests.Response:
        """
        Get Conditional Order
        """
        method = 'GET'
        path = '/futures/private/stop-order/list'
        query = {
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'direction': direction,
            'limit': limit,
            'cursor': cursor,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancel(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Cancel Conditional Order
        """
        method = 'POST'
        path = '/futures/private/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_cancelall(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        Cancel All Conditional Orders
        """
        method = 'POST'
        path = '/futures/private/stop-order/cancelAll'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder_replace(
        self,
        stop_order_id: str=None,
        order_link_id: str=None,
        symbol: str=None,
        p_r_qty: int=None,
        p_r_price: str=None,
        p_r_trigger_price: str=None,
        take_profit: float=None,
        stop_loss: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
    ) -> requests.Response:
        """
        Replace Conditional Order
        """
        method = 'POST'
        path = '/futures/private/stop-order/replace'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'p_r_trigger_price': p_r_trigger_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
        }
        return self._request(method, path, query, private=True)

    def private_stoporder(
        self,
        symbol: str=None,
        stop_order_id: str=None,
        order_link_id: str=None,
    ) -> requests.Response:
        """
        Query Conditional Order (real-time)
        """
        method = 'GET'
        path = '/futures/private/stop-order'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
        }
        return self._request(method, path, query, private=True)

    def private_position_list(
        self,
        symbol: str=None,
    ) -> requests.Response:
        """
        My Position
        """
        method = 'GET'
        path = '/futures/private/position/list'
        query = {
            'symbol': symbol,
        }
        return self._request(method, path, query, private=True)

    def private_position_changepositionmargin(
        self,
        symbol: str=None,
        position_idx: int=None,
        margin: str=None,
    ) -> requests.Response:
        """
        Change Margin
        """
        method = 'POST'
        path = '/futures/private/position/change-position-margin'
        query = {
            'symbol': symbol,
            'position_idx': position_idx,
            'margin': margin,
        }
        return self._request(method, path, query, private=True)

    def private_position_tradingstop(
        self,
        symbol: str=None,
        position_idx: int=None,
        take_profit: float=None,
        stop_loss: float=None,
        trailing_stop: float=None,
        tp_trigger_by: str=None,
        sl_trigger_by: str=None,
        new_trailing_active: float=None,
        sl_size: float=None,
        tp_size: float=None,
    ) -> requests.Response:
        """
        Set Trading-Stop
        """
        method = 'POST'
        path = '/futures/private/position/trading-stop'
        query = {
            'symbol': symbol,
            'position_idx': position_idx,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'tp_trigger_by': tp_trigger_by,
            'sl_trigger_by': sl_trigger_by,
            'new_trailing_active': new_trailing_active,
            'sl_size': sl_size,
            'tp_size': tp_size,
        }
        return self._request(method, path, query, private=True)

    def private_position_leverage_save(
        self,
        symbol: str=None,
        buy_leverage: float=None,
        sell_leverage: float=None,
    ) -> requests.Response:
        """
        Set Leverage
        """
        method = 'POST'
        path = '/futures/private/position/leverage/save'
        query = {
            'symbol': symbol,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage,
        }
        return self._request(method, path, query, private=True)

    def private_position_switchmode(
        self,
        symbol: str=None,
        mode: int=None,
    ) -> requests.Response:
        """
        Position Mode Switch
        """
        method = 'POST'
        path = '/futures/private/position/switch-mode'
        query = {
            'symbol': symbol,
            'mode': mode,
        }
        return self._request(method, path, query, private=True)

    def private_tpsl_switchmode(
        self,
        symbol: str=None,
        tp_sl_mode: str=None,
    ) -> requests.Response:
        """
        Full/Partial Position SL/TP Switch
        """
        method = 'POST'
        path = '/futures/private/tpsl/switch-mode'
        query = {
            'symbol': symbol,
            'tp_sl_mode': tp_sl_mode,
        }
        return self._request(method, path, query, private=True)

    def private_position_switchisolated(
        self,
        symbol: str=None,
        is_isolated: bool=None,
        buy_leverage: float=None,
        sell_leverage: float=None,
    ) -> requests.Response:
        """
        Cross/Isolated Margin Switch
        """
        method = 'POST'
        path = '/futures/private/position/switch-isolated'
        query = {
            'symbol': symbol,
            'is_isolated': is_isolated,
            'buy_leverage': buy_leverage,
            'sell_leverage': sell_leverage,
        }
        return self._request(method, path, query, private=True)

    def private_execution_list(
        self,
        order_id: str=None,
        symbol: str=None,
        start_time: int=None,
        page: int=None,
        limit: int=None,
        order: str=None,
    ) -> requests.Response:
        """
        User Trade Records
        """
        method = 'GET'
        path = '/futures/private/execution/list'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'start_time': start_time,
            'page': page,
            'limit': limit,
            'order': order,
        }
        return self._request(method, path, query, private=True)

    def private_trade_closedpnl_list(
        self,
        symbol: str=None,
        start_time: int=None,
        end_time: int=None,
        exec_type: str=None,
        page: int=None,
        limit: int=None,
    ) -> requests.Response:
        """
        Closed Profit and Loss
        """
        method = 'GET'
        path = '/futures/private/trade/closed-pnl/list'
        query = {
            'symbol': symbol,
            'start_time': start_time,
            'end_time': end_time,
            'exec_type': exec_type,
            'page': page,
            'limit': limit,
        }
        return self._request(method, path, query, private=True)

    def private_position_risklimit(
        self,
        symbol: str=None,
        risk_id: int=None,
        position_idx: int=None,
    ) -> requests.Response:
        """
        Set Risk Limit
        """
        method = 'POST'
        path = '/futures/private/position/risk-limit'
        query = {
            'symbol': symbol,
            'risk_id': risk_id,
            'position_idx': position_idx,
        }
        return self._request(method, path, query, private=True)

    def public_time(
        self,
    ) -> requests.Response:
        """
        Server Time
        """
        method = 'GET'
        path = '/v2/public/time'
        query = {
        }
        return self._request(method, path, query, private=False)

    def public_announcement(
        self,
    ) -> requests.Response:
        """
        Announcement
        """
        method = 'GET'
        path = '/v2/public/announcement'
        query = {
        }
        return self._request(method, path, query, private=False)
