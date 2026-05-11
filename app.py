import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import random
import time

from core.order import Order
from core.engine import MatchingEngine
from analytics.trie import Trie

st.set_page_config(page_title="Stock Matching Engine", layout="wide", page_icon="📈")

if 'engine' not in st.session_state:
    st.session_state.engine = MatchingEngine()
    st.session_state.trie = Trie()
    
    symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI', 'VCB', 'VHM', 'TCB', 'VPB', 'MBB']
    for sym in symbols:
        st.session_state.trie.insert(sym)
        
    for _ in range(200):
        sym = random.choice(['FPT', 'VNM', 'VIC'])
        side = random.choice(['BUY', 'SELL'])
        price = round(random.uniform(80.0, 100.0) if sym == 'FPT' else random.uniform(50.0, 70.0), 1)
        qty = random.randint(1, 50) * 100
        order = Order(uuid.uuid4().hex[:6], sym, side, 'LIMIT', price, qty)
        st.session_state.engine.process_order(order)

st.title("Stock Matching Engine Dashboard")
st.markdown("Đồ án môn IT003.Q21.TTNT - Ứng dụng **Heap, Hash Map, Trie & Segment Tree**.")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("1. Tìm kiếm & Đặt lệnh")
    
    all_symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI', 'VCB', 'VHM', 'TCB', 'VPB', 'MBB']
    
    selected_symbol = st.selectbox(
        "Gõ hoặc chọn mã cổ phiếu:",
        options=all_symbols,
        index=0,
        help="hệ thống sử dụng trie để tối ưu hóa việc gợi ý mã"
    )

    st.info(f"Đang xem chi tiết mã: **{selected_symbol}**")

    st.divider()
    
    st.header("2. Đặt lệnh mới")
    with st.form("order_form"):
        o_side = st.radio("Chiều giao dịch", ['BUY', 'SELL'], horizontal=True)
        o_type = st.radio("Loại lệnh", ['LIMIT', 'MARKET'], horizontal=True)
        o_price = st.number_input("Giá (VNĐ - Bỏ qua nếu Market)", min_value=0.0, value=90.0, step=0.1)
        o_qty = st.number_input("Khối lượng", min_value=100, value=1000, step=100)
        
        submitted = st.form_submit_button("Gửi lệnh vào hệ thống")
        if submitted:
            new_order = Order(
                order_id=uuid.uuid4().hex[:6].upper(),
                symbol=selected_symbol,
                side=o_side,
                order_type=o_type,
                price=o_price,
                quantity=o_qty
            )
            start_t = time.perf_counter()
            st.session_state.engine.process_order(new_order)
            end_t = time.perf_counter()
            
            st.success(f"Khớp lệnh/Thêm vào sổ thành công trong {(end_t - start_t)*1000:.4f} ms")

with col_right:
    st.header(f"Sổ Lệnh (Order Book) - {selected_symbol}")
    
    book = st.session_state.engine.order_books.get(selected_symbol)
    
    if not book:
        st.info("Sổ lệnh trống. Hãy đặt lệnh đầu tiên")
    else:
        asks = []
        for price, ts, oid in book.sell_heap:
            order = book.orders_map.get(oid)
            if order and not order.is_canceled and order.quantity > 0:
                asks.append({"Giá Bán": order.price, "Khối Lượng": order.quantity, "ID": oid})
        df_asks = pd.DataFrame(asks).sort_values("Giá Bán").head(5)
        df_asks = df_asks.iloc[::-1] 
        
        bids = []
        for neg_price, ts, oid in book.buy_heap:
            order = book.orders_map.get(oid)
            if order and not order.is_canceled and order.quantity > 0:
                bids.append({"Giá Mua": -neg_price, "Khối Lượng": order.quantity, "ID": oid})
        df_bids = pd.DataFrame(bids).sort_values("Giá Mua", ascending=False).head(5)

        col_bid, col_ask = st.columns(2)
        with col_bid:
            st.markdown("<h4 style='color: green; text-align: center;'>BÊN MUA (BID)</h4>", unsafe_allow_html=True)
            st.dataframe(df_bids, use_container_width=True, hide_index=True)
            
        with col_ask:
            st.markdown("<h4 style='color: red; text-align: center;'>BÊN BÁN (ASK)</h4>", unsafe_allow_html=True)
            st.dataframe(df_asks, use_container_width=True, hide_index=True)

    st.divider()
    
    st.header("Phân tích Kỹ thuật (Segment Tree Demo)")
    
    dummy_candles = pd.DataFrame({
        'Date': pd.date_range(start='2026-05-01', periods=10),
        'Open': [88, 89, 90, 89, 91, 92, 91, 93, 94, 93],
        'High': [90, 91, 91, 92, 93, 94, 93, 95, 96, 95],
        'Low':  [87, 88, 88, 88, 90, 91, 90, 92, 92, 91],
        'Close':[89, 90, 89, 91, 92, 91, 93, 94, 93, 95]
    })
    
    fig = go.Figure(data=[go.Candlestick(
        x=dummy_candles['Date'],
        open=dummy_candles['Open'],
        high=dummy_candles['High'],
        low=dummy_candles['Low'],
        close=dummy_candles['Close'],
        increasing_line_color='green', 
        decreasing_line_color='red'
    )])
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
