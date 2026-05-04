class NaiveOrderBook:
    def __init__(self):
        self.bids = []  
        self.asks = []  
        self.trades = []

    def add_order(self, order_id: str, is_buy: bool, price: float, quantity: int):
        order = {"id": order_id, "price": price, "qty": quantity}
        
        if is_buy:
            self.bids.append(order)
            self.bids.sort(key=lambda x: x['price'], reverse=True)
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda x: x['price'])
            
        self._match()

    def cancel_order(self, order_id: str) -> bool:
        for i, o in enumerate(self.bids):
            if o['id'] == order_id:
                self.bids.pop(i)
                return True
        for i, o in enumerate(self.asks):
            if o['id'] == order_id:
                self.asks.pop(i)
                return True
        return False

    def _match(self):
        while self.bids and self.asks:
            best_bid = self.bids[0]
            best_ask = self.asks[0]

            if best_bid['price'] >= best_ask['price']:
                match_qty = min(best_bid['qty'], best_ask['qty'])
                best_bid['qty'] -= match_qty
                best_ask['qty'] -= match_qty

                if best_bid['qty'] == 0:
                    self.bids.pop(0) 
                if best_ask['qty'] == 0:
                    self.asks.pop(0)
            else:
                break
