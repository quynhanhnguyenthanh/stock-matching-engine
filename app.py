import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import random
from datetime import datetime, timezone, timedelta

from core.order import Order
from core.engine import MatchingEngine
from core.trie import Trie

VN_TZ = timezone(timedelta(hours=7))

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
        price = float(random.randrange(80000, 100000, 100) if sym == 'FPT' else random.randrange(50000, 70000, 100))
        qty = random.randint(1, 50) * 100
        order = Order(uuid.uuid4().hex[:6], sym, side, 'LIMIT', price, qty)
        st.session_state.engine.process_order(order)

st.title("Stock Matching Engine Dashboard")
col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("Tìm kiếm & Đặt lệnh")
    all_symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI', 'VCB', 'VHM', 'TCB', 'VPB', 'MBB']
    selected_symbol = st.selectbox("Chọn mã cổ phiếu:", options=all_symbols, index=0)
    
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
        
        if o_side == "BUY":
            total_cost = 0.0
            remaining_to_fill = o_qty
            
            if is_market:
                if not book or not book.sell_heap:
                    st.error("❌ Không có người bán để khớp lệnh Market")
                    st.stop()
                
                sorted_asks = sorted(book.sell_heap, key=lambda x: x[0])
                for p, ts, oid in sorted_asks:
                    ord_item = book.orders_map.get(oid)
                    if ord_item:
                        fill = min(remaining_to_fill, ord_item.quantity)
                        total_cost += fill * p
                        remaining_to_fill -= fill
                        if remaining_to_fill <= 0: break
                
                if remaining_to_fill > 0:
                    st.warning(f"⚠️ Chỉ có thể khớp {o_qty - remaining_to_fill} cổ phiếu do thiếu thanh khoản.")
            else:
                total_cost = o_price * o_qty

            if st.session_state.balance < total_cost:
                st.error(f"❌ Không đủ tiền. Cần {total_cost:,.0f} VNĐ")
            else:
                st.session_state.balance -= total_cost
                qty_actually_bought = o_qty - (remaining_to_fill if is_market else 0)
                st.session_state.portfolio[selected_symbol] = st.session_state.portfolio.get(selected_symbol, 0) + qty_actually_bought
                
                new_order = Order(uuid.uuid4().hex[:6].upper(), selected_symbol, o_side, o_type, o_price if not is_market else (total_cost/qty_actually_bought), qty_actually_bought)
                st.session_state.engine.process_order(new_order)
                
                st.session_state.trade_history.append({
                    "Thời Gian": datetime.now(VN_TZ).strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"BUY {o_type}",
                    "Giá": f"Avg: {total_cost/qty_actually_bought:,.0f}" if is_market else f"{o_price:,.0f}",
                    "Khối Lượng": f"{qty_actually_bought:,}"
                })
                st.rerun()

        else:
            owned_qty = st.session_state.portfolio.get(selected_symbol, 0)
            if owned_qty < o_qty:
                st.error("❌ Không đủ cổ phiếu để bán")
            else:
                total_gain = 0.0
                remaining_to_fill = o_qty
                
                if is_market:
                    if not book or not book.buy_heap:
                        st.error("❌ Không có người mua để khớp lệnh Market")
                        st.stop()
                    
                    sorted_bids = sorted(book.buy_heap, key=lambda x: x[0])
                    for neg_p, ts, oid in sorted_bids:
                        ord_item = book.orders_map.get(oid)
                        if ord_item:
                            fill = min(remaining_to_fill, ord_item.quantity)
                            total_gain += fill * (-neg_p)
                            remaining_to_fill -= fill
                            if remaining_to_fill <= 0: break
                else:
                    total_gain = o_price * o_qty

                qty_actually_sold = o_qty - (remaining_to_fill if is_market else 0)
                st.session_state.portfolio[selected_symbol] -= qty_actually_sold
                st.session_state.balance += total_gain
                
                new_order = Order(uuid.uuid4().hex[:6].upper(), selected_symbol, o_side, o_type, o_price if not is_market else (total_gain/qty_actually_sold), qty_actually_sold)
                st.session_state.engine.process_order(new_order)

                st.session_state.trade_history.append({
                    "Thời Gian": datetime.now(VN_TZ).strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"SELL {o_type}",
                    "Giá": f"Avg: {total_gain/qty_actually_sold:,.0f}" if is_market else f"{o_price:,.0f}",
                    "Khối Lượng": f"{qty_actually_sold:,}"
                })
                st.rerun()

with col_right:
    st.header(f"Sổ Lệnh - {selected_symbol}")
    book = st.session_state.engine.order_books.get(selected_symbol)
    if not book:
        st.info("Sổ lệnh trống.")
    else:
        asks = []
        for p, ts, oid in book.sell_heap:
            ord_obj = book.orders_map.get(oid)
            if ord_obj and ord_obj.quantity > 0:
                asks.append({"Giá": ord_obj.price, "KL": ord_obj.quantity, "ID": oid})
        
        bids = []
        for np, ts, oid in book.buy_heap:
            ord_obj = book.orders_map.get(oid)
            if ord_obj and ord_obj.quantity > 0:
                bids.append({"Giá": ord_obj.price, "KL": ord_obj.quantity, "ID": oid})

        df_bids = pd.DataFrame(bids).sort_values("Giá", ascending=True).head(5) if bids else pd.DataFrame(columns=["Giá", "KL", "ID"])
        
        df_asks = pd.DataFrame(asks).sort_values("Giá", ascending=False).head(5) if asks else pd.DataFrame(columns=["Giá", "KL", "ID"])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4 style='color:green;text-align:center;'>BÊN MUA</h4>", unsafe_allow_html=True)
            st.dataframe(df_bids, use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<h4 style='color:red;text-align:center;'>BÊN BÁN</h4>", unsafe_allow_html=True)
            st.dataframe(df_asks, use_container_width=True, hide_index=True)

    st.divider()
    st.header("Lịch sử khớp lệnh")
    if st.session_state.trade_history:
        st.dataframe(pd.DataFrame(st.session_state.trade_history[-20:][::-1]), use_container_width=True, hide_index=True)

    st.divider()
    st.header("Phân tích Dữ liệu")
    tab1, tab2 = st.tabs(["📊 Độ sâu thị trường", "📉 Biểu đồ Giá"])
    with tab1:
        if book:
            b_d = [{"p": -p, "q": book.orders_map[o].quantity} for p, t, o in book.buy_heap if o in book.orders_map]
            a_d = [{"p": p, "q": book.orders_map[o].quantity} for p, t, o in book.sell_heap if o in book.orders_map]
            fig = go.Figure()
            if b_d:
                df_b = pd.DataFrame(b_d).groupby('p').sum().reset_index().sort_values('p', ascending=False)
                df_b['cum'] = df_b['q'].cumsum()
                fig.add_trace(go.Scatter(x=df_b['p'], y=df_b['cum'], fill='tozeroy', name='Bids', line=dict(color='green')))
            if a_d:
                df_a = pd.DataFrame(a_d).groupby('p').sum().reset_index().sort_values('p')
                df_a['cum'] = df_a['q'].cumsum()
                fig.add_trace(go.Scatter(x=df_a['p'], y=df_a['cum'], fill='tozeroy', name='Asks', line=dict(color='red')))
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
    with tab2:
        real_trades = [t for t in st.session_state.trade_history if t["Mã CP"] == selected_symbol]
        if real_trades:
            prices = []
            for t in real_trades:
                price_str = str(t["Giá"]).replace('Avg: ', '').replace(',', '')
                try:
                    prices.append(float(price_str))
                except ValueError:
                    pass
            
            if prices:
                fig_line = go.Figure(go.Scatter(y=prices, mode='lines+markers', line=dict(color='#00d2ff')))
                fig_line.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_line, use_container_width=True)
