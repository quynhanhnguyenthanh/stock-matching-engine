import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import random
import time

from core.order import Order
from core.engine import MatchingEngine
from core.trie import Trie

st.set_page_config(
    page_title="Stock Matching Engine",
    layout="wide",
    page_icon="📈"
)

if 'engine' not in st.session_state:
    st.session_state.engine = MatchingEngine()
    st.session_state.trie = Trie()
    st.session_state.balance = 100_000_000
    st.session_state.portfolio = {}
    st.session_state.trade_history = []

    symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI', 'VCB', 'VHM', 'TCB', 'VPB', 'MBB']
    for sym in symbols:
        st.session_state.trie.insert(sym)

    for _ in range(500):
        sym = random.choice(symbols)
        side = random.choice(['BUY', 'SELL'])
        price = float(
            random.randrange(80000, 100000, 100)
            if sym == 'FPT'
            else random.randrange(50000, 70000, 100)
        )
        qty = random.randint(1, 50) * 100
        order = Order(uuid.uuid4().hex[:6], sym, side, 'LIMIT', price, qty)
        st.session_state.engine.process_order(order)

st.title("Stock Matching Engine Dashboard")
col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("Tìm kiếm & Đặt lệnh")
    all_symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI', 'VCB', 'VHM', 'TCB', 'VPB', 'MBB']
    selected_symbol = st.selectbox("Chọn mã cổ phiếu:", options=all_symbols, index=0)
    st.info(f"Đang xem chi tiết mã: **{selected_symbol}**")

    st.divider()
    st.header("Portfolio Giả Lập")
    st.metric(label="Số dư hiện có", value=f"{st.session_state.balance:,.0f} VNĐ")

    portfolio_data = [{"Mã": sym, "Sở Hữu": qty} for sym, qty in st.session_state.portfolio.items() if qty > 0]
    st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)

    st.divider()
    st.header("Đặt lệnh mới")
    o_side = st.radio("Chiều giao dịch", ['BUY', 'SELL'], horizontal=True)
    o_type = st.radio("Loại lệnh", ['LIMIT', 'MARKET'], horizontal=True)
    is_market = (o_type == 'MARKET')

    o_price = st.number_input("Giá (VNĐ)", min_value=0.0, value=90000.0, step=100.0, disabled=is_market)
    o_qty = st.number_input("Khối lượng", min_value=100, value=1000, step=100)
    submitted = st.button("Gửi lệnh vào hệ thống", use_container_width=True)

    if submitted:
        book = st.session_state.engine.order_books.get(selected_symbol)
        exec_price = o_price
        
        if o_side == "BUY":
            if is_market:
                if book and book.sell_heap:
                    exec_price = book.sell_heap[0][0] 
                else:
                    st.error("❌ Không thể khớp lệnh Market Buy: Sổ lệnh trống")
                    st.stop()
            
            total_cost = exec_price * o_qty
            if st.session_state.balance < total_cost:
                st.error(f"❌ Không đủ số dư. Cần {total_cost:,.0f} VNĐ")
            else:
                st.session_state.balance -= total_cost
                st.session_state.portfolio[selected_symbol] = st.session_state.portfolio.get(selected_symbol, 0) + o_qty
                new_order = Order(uuid.uuid4().hex[:6].upper(), selected_symbol, o_side, o_type, exec_price, o_qty)
                
                start_t = time.perf_counter()
                st.session_state.engine.process_order(new_order)
                end_t = time.perf_counter()

                st.session_state.trade_history.append({
                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"BUY {o_type}",
                    "Giá": f"{exec_price:,.0f}",
                    "Khối Lượng": f"{o_qty:,}"
                })
                st.success(f"✅ Thành công trong {(end_t - start_t)*1000:.4f} ms")
                st.rerun()

        else:
            owned_qty = st.session_state.portfolio.get(selected_symbol, 0)
            if owned_qty < o_qty:
                st.error("❌ Không đủ cổ phiếu để bán")
            else:
                if is_market:
                    if book and book.buy_heap:
                        exec_price = -book.buy_heap[0][0]
                    else:
                        st.error("❌ Không thể khớp lệnh Market Sell: Sổ lệnh trống")
                        st.stop()

                st.session_state.portfolio[selected_symbol] -= o_qty
                st.session_state.balance += (exec_price * o_qty)
                new_order = Order(uuid.uuid4().hex[:6].upper(), selected_symbol, o_side, o_type, exec_price, o_qty)

                start_t = time.perf_counter()
                st.session_state.engine.process_order(new_order)
                end_t = time.perf_counter()

                st.session_state.trade_history.append({
                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"SELL {o_type}",
                    "Giá": f"{exec_price:,.0f}",
                    "Khối Lượng": f"{o_qty:,}"
                })
                st.success(f"✅ Thành công trong {(end_t - start_t)*1000:.4f} ms")
                st.rerun()

with col_right:
    st.header(f"Sổ Lệnh - {selected_symbol}")
    book = st.session_state.engine.order_books.get(selected_symbol)

    if not book:
        st.info("Sổ lệnh trống.")
    else:
        asks = []
        for price, ts, oid in book.sell_heap:
            order = book.orders_map.get(oid)
            if order and not order.is_canceled and order.quantity > 0:
                asks.append({"Giá Bán": f"{order.price:,.0f}", "Khối Lượng": f"{order.quantity:,}", "ID": oid})
        df_asks = pd.DataFrame(asks).sort_values("Giá Bán").head(5) if asks else pd.DataFrame(columns=["Giá Bán", "Khối Lượng", "ID"])

        bids = []
        for neg_price, ts, oid in book.buy_heap:
            order = book.orders_map.get(oid)
            if order and not order.is_canceled and order.quantity > 0:
                bids.append({"Giá Mua": f"{-neg_price:,.0f}", "Khối Lượng": f"{order.quantity:,}", "ID": oid})
        df_bids = pd.DataFrame(bids).sort_values("Giá Mua", ascending=False).head(5) if bids else pd.DataFrame(columns=["Giá Mua", "Khối Lượng", "ID"])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4 style='color: green; text-align: center;'>BÊN MUA (BID)</h4>", unsafe_allow_html=True)
            st.dataframe(df_bids, use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<h4 style='color: red; text-align: center;'>BÊN BÁN (ASK)</h4>", unsafe_allow_html=True)
            st.dataframe(df_asks, use_container_width=True, hide_index=True)

    st.divider()
    st.header("Lịch sử khớp lệnh")
    if st.session_state.trade_history:
        st.dataframe(pd.DataFrame(st.session_state.trade_history[-20:][::-1]), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có giao dịch.")

    st.divider()
    st.header("Phân tích Dữ liệu")
    tab1, tab2 = st.tabs(["📊 Độ sâu thị trường", "📉 Biểu đồ Giá"])

    with tab1:
        if book:
            bid_d = [{"price": -p, "qty": book.orders_map[o].quantity} for p, t, o in book.buy_heap if o in book.orders_map]
            ask_d = [{"price": p, "qty": book.orders_map[o].quantity} for p, t, o in book.sell_heap if o in book.orders_map]
            fig_depth = go.Figure()
            if bid_d:
                df_b = pd.DataFrame(bid_d).groupby('price').sum().reset_index().sort_values('price', ascending=False)
                df_b['cum_qty'] = df_b['qty'].cumsum()
                fig_depth.add_trace(go.Scatter(x=df_b['price'], y=df_b['cum_qty'], fill='tozeroy', name='Bids', line=dict(color='green')))
            if ask_d:
                df_a = pd.DataFrame(ask_d).groupby('price').sum().reset_index().sort_values('price')
                df_a['cum_qty'] = df_a['qty'].cumsum()
                fig_depth.add_trace(go.Scatter(x=df_a['price'], y=df_a['cum_qty'], fill='tozeroy', name='Asks', line=dict(color='red')))
            fig_depth.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_depth, use_container_width=True)

    with tab2:
        real_trades = [t for t in st.session_state.trade_history if t["Mã CP"] == selected_symbol]
        if real_trades:
            prices = [float(t["Giá"].replace(',', '')) for t in real_trades]
            fig_line = go.Figure(go.Scatter(y=prices, mode='lines+markers', line=dict(color='#00d2ff')))
            fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_line, use_container_width=True)
