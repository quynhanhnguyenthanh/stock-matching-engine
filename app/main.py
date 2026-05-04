from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orderbook import OrderBook

app = FastAPI(title="Stock Matching Engine API")

engine = OrderBook()

class OrderRequest(BaseModel):
    is_buy: bool
    price: float
    quantity: int

@app.post("/api/order", summary="Đặt lệnh mới")
def place_order(order: OrderRequest):
    import uuid
    order_id = str(uuid.uuid4())[:8]
    
    engine.add_order(order_id, order.is_buy, order.price, order.quantity)
    
    return {"message": "Đặt lệnh thành công", "order_id": order_id}

@app.delete("/api/order/{order_id}", summary="Hủy lệnh")
def cancel_order(order_id: str):
    success = engine.cancel_order(order_id)
    if success:
        return {"message": f"Hủy lệnh {order_id} thành công (Lazy Deletion)"}
    raise HTTPException(status_code=404, detail="Không tìm thấy lệnh hoặc đã khớp")

@app.get("/api/orderbook", summary="Xem sổ lệnh hiện tại")
def get_orderbook():
    """
    Trả về top 5 mức giá tốt nhất của cả 2 bên để vẽ lên giao diện.
    """
    top_bids = []
    for order in engine.bids.data[:5]: 
        if not order.is_canceled and order.quantity > 0:
            top_bids.append({"price": order.price, "quantity": order.quantity})
            
    top_asks = []
    for order in engine.asks.data[:5]:
        if not order.is_canceled and order.quantity > 0:
            top_asks.append({"price": order.price, "quantity": order.quantity})

    return {
        "bids": sorted(top_bids, key=lambda x: x['price'], reverse=True),
        "asks": sorted(top_asks, key=lambda x: x['price']),
        "recent_trades": engine.trades[-10:] 
    }
