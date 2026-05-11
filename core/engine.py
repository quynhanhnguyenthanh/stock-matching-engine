import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import random
import time

from core.order import Order
from core.engine import MatchingEngine
from analytics.trie import Trie

st.set_page_config(
    page_title="Stock Matching Engine",
    layout="wide",
    page_icon="📈"
)

# =========================
# INIT SESSION STATE
# =========================

if 'engine' not in st.session_state:

    st.session_state.engine = MatchingEngine()
    st.session_state.trie = Trie()

    # portfolio giả lập (cấp vốn 100 triệu vnđ)
    st.session_state.balance = 100_000_000

    # Khởi tạo ví rỗng (chưa sở hữu cổ phiếu nào)
    st.session_state.portfolio = {}

    # trade history
    st.session_state.trade_history = []

    symbols = [
        'FPT', 'VNM', 'VIC', 'HPG', 'SSI',
        'VCB', 'VHM', 'TCB', 'VPB', 'MBB'
    ]

    for sym in symbols:
        st.session_state.trie.insert(sym)

    # tạo dữ liệu mẫu với giá thực tế (hàng chục nghìn vnđ)
    for _ in range(500):

        sym = random.choice(symbols)
        side = random.choice(['BUY', 'SELL'])

        # giá ngẫu nhiên với bước giá 100 vnđ
        price = float(
            random.randrange(80000, 100000, 100)
            if sym == 'FPT'
            else random.randrange(50000, 70000, 100)
        )

        qty = random.randint(1, 50) * 100

        order = Order(
            uuid.uuid4().hex[:6],
            sym,
            side,
            'LIMIT',
            price,
            qty
        )

        st.session_state.engine.process_order(order)

# =========================
# UI HEADER
# =========================

st.title("Stock Matching Engine Dashboard")

col_left, col_right = st.columns([1, 2])

# =========================================================
# LEFT PANEL
# =========================================================

with col_left:

    st.header("Tìm kiếm & Đặt lệnh")

    all_symbols = [
        'FPT', 'VNM', 'VIC', 'HPG', 'SSI',
        'VCB', 'VHM', 'TCB', 'VPB', 'MBB'
    ]

    selected_symbol = st.selectbox(
        "Gõ hoặc chọn mã cổ phiếu:",
        options=all_symbols,
        index=0,
        help="hệ thống sử dụng trie để tối ưu tìm kiếm"
    )

    st.info(f"Đang xem chi tiết mã: **{selected_symbol}**")

    # =========================
    # PORTFOLIO
    # =========================

    st.divider()

    st.header("Portfolio Giả Lập")

    st.metric(
        label="Số dư hiện có",
        value=f"{st.session_state.balance:,.0f} VNĐ"
    )

    portfolio_data = []

    for sym, qty in st.session_state.portfolio.items():

        portfolio_data.append({
            "Mã": sym,
            "Sở Hữu": qty
        })

    df_portfolio = pd.DataFrame(portfolio_data)

    st.dataframe(
        df_portfolio,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # ORDER FORM (ĐÃ ĐƯỢC CHỈNH SỬA)
    # =========================

    st.divider()

    st.header("Đặt lệnh mới")

    # Đã bỏ "with st.form" để giao diện có thể phản hồi tức thì
    o_side = st.radio(
        "Chiều giao dịch",
        ['BUY', 'SELL'],
        horizontal=True
    )

    o_type = st.radio(
        "Loại lệnh",
        ['LIMIT', 'MARKET'],
        horizontal=True
    )

    # Logic kiểm tra: Nếu chọn MARKET thì is_market = True
    is_market = (o_type == 'MARKET')

    o_price = st.number_input(
        "Giá (VNĐ - bỏ qua nếu Market)",
        min_value=0.0,
        value=90000.0,
        step=100.0,
        disabled=is_market, # Khóa ô nếu là MARKET
        help="Lệnh Market sẽ tự động khớp giá tốt nhất trên sổ lệnh." if is_market else "Nhập mức giá bạn mong muốn."
    )

    o_qty = st.number_input(
        "Khối lượng",
        min_value=100,
        value=1000,
        step=100
    )

    # Thay st.form_submit_button bằng st.button thông thường
    submitted = st.button(
        "Gửi lệnh vào hệ thống",
        use_container_width=True
    )

    if submitted:

        estimated_cost = o_price * o_qty

        # =========================
        # BUY ORDER
        # =========================

        if o_side == "BUY":

            if not is_market and st.session_state.balance < estimated_cost:
                st.error("❌ Không đủ số dư để đặt lệnh mua")
            else:
                if not is_market:
                    st.session_state.balance -= estimated_cost
                
                st.session_state.portfolio[selected_symbol] = st.session_state.portfolio.get(selected_symbol, 0) + o_qty

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

                st.session_state.trade_history.append({
                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"BUY {o_type}",
                    "Giá": "MARKET" if is_market else f"{o_price:,.0f}",
                    "Khối Lượng": f"{o_qty:,}"
                })

                st.success(f"✅ Khớp lệnh trong {(end_t - start_t)*1000:.4f} ms")
                st.rerun()

        # =========================
        # SELL ORDER
        # =========================

        else:

            owned_qty = st.session_state.portfolio.get(selected_symbol, 0)

            if owned_qty < o_qty:
                st.error("❌ Không đủ cổ phiếu để bán")
            else:
                # Trừ cổ phiếu
                st.session_state.portfolio[selected_symbol] -= o_qty
                # Cộng tiền vào số dư (Balance)
                if not is_market:
                    st.session_state.balance += estimated_cost

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

                st.session_state.trade_history.append({
                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": f"SELL {o_type}",
                    "Giá": "MARKET" if is_market else f"{o_price:,.0f}",
                    "Khối Lượng": f"{o_qty:,}"
                })

                st.success(f"✅ Khớp lệnh/Thêm vào sổ thành công trong {(end_t - start_t)*1000:.4f} ms")
                st.rerun() # Gọi lại app để làm mới số dư trên UI ngay lập tức

# =========================================================
# RIGHT PANEL
# =========================================================

with col_right:

    st.header(f"Sổ Lệnh - {selected_symbol}")

    book = st.session_state.engine.order_books.get(
        selected_symbol
    )

    if not book:

        st.info("Sổ lệnh trống. Hãy đặt lệnh đầu tiên")

    else:

        # =========================
        # ASK SIDE
        # =========================

        asks = []

        for price, ts, oid in book.sell_heap:

            order = book.orders_map.get(oid)

            if (
                order
                and not order.is_canceled
                and order.quantity > 0
            ):

                asks.append({
                    "Giá Bán": f"{order.price:,.0f}",
                    "Khối Lượng": f"{order.quantity:,}",
                    "ID": oid
                })

        if asks:

            df_asks = (
                pd.DataFrame(asks)
                .sort_values("Giá Bán")
                .head(5)
            )

        else:

            df_asks = pd.DataFrame(
                columns=[
                    "Giá Bán",
                    "Khối Lượng",
                    "ID"
                ]
            )

        # =========================
        # BID SIDE
        # =========================

        bids = []

        for neg_price, ts, oid in book.buy_heap:

            order = book.orders_map.get(oid)

            if (
                order
                and not order.is_canceled
                and order.quantity > 0
            ):

                bids.append({
                    "Giá Mua": f"{-neg_price:,.0f}",
                    "Khối Lượng": f"{order.quantity:,}",
                    "ID": oid
                })

        if bids:

            df_bids = (
                pd.DataFrame(bids)
                .sort_values(
                    "Giá Mua",
                    ascending=False
                )
                .head(5)
            )

        else:

            df_bids = pd.DataFrame(
                columns=[
                    "Giá Mua",
                    "Khối Lượng",
                    "ID"
                ]
            )

        # =========================
        # DISPLAY ORDER BOOK
        # =========================

        col_bid, col_ask = st.columns(2)

        with col_bid:

            st.markdown(
                """
                <h4 style='color: green; text-align: center;'>
                BÊN MUA (BID)
                </h4>
                """,
                unsafe_allow_html=True
            )

            st.dataframe(
                df_bids,
                use_container_width=True,
                hide_index=True
            )

        with col_ask:

            st.markdown(
                """
                <h4 style='color: red; text-align: center;'>
                BÊN BÁN (ASK)
                </h4>
                """,
                unsafe_allow_html=True
            )

            st.dataframe(
                df_asks,
                use_container_width=True,
                hide_index=True
            )

    # =====================================================
    # TRADE HISTORY
    # =====================================================

    st.divider()

    st.header("Lịch sử khớp lệnh")

    trade_history = st.session_state.trade_history[-20:]

    if trade_history:

        df_trades = pd.DataFrame(
            trade_history[::-1]
        )

        st.dataframe(
            df_trades,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Chưa có giao dịch nào")

    # =====================================================
    # REAL-TIME CHARTS
    # =====================================================

    st.divider()
    st.header("Phân tích Dữ liệu Real-time")

    tab1, tab2 = st.tabs(["📊 Độ sâu thị trường (Market Depth)", "📉 Biểu đồ Giá (Tick Chart)"])

    # --- TAB 1: ĐỘ SÂU THỊ TRƯỜNG (MARKET DEPTH) ---
    with tab1:
        st.caption("Trực quan hóa khối lượng lệnh chờ trực tiếp từ cấu trúc Heap.")
        
        if book:
            # Quét Heap Bên Mua (Bid)
            bid_data = []
            for neg_price, ts, oid in book.buy_heap:
                order = book.orders_map.get(oid)
                if order and not order.is_canceled and order.quantity > 0:
                    bid_data.append({"price": -neg_price, "qty": order.quantity})
            
            # Quét Heap Bên Bán (Ask)
            ask_data = []
            for price, ts, oid in book.sell_heap:
                order = book.orders_map.get(oid)
                if order and not order.is_canceled and order.quantity > 0:
                    ask_data.append({"price": price, "qty": order.quantity})
            
            df_bid = pd.DataFrame(bid_data)
            df_ask = pd.DataFrame(ask_data)
            
            fig_depth = go.Figure()

            # Vẽ vùng Xanh (Lực Mua) - Cộng dồn khối lượng từ giá cao xuống thấp
            if not df_bid.empty:
                df_bid = df_bid.groupby('price').sum().reset_index().sort_values('price', ascending=False)
                df_bid['cum_qty'] = df_bid['qty'].cumsum()
                fig_depth.add_trace(go.Scatter(
                    x=df_bid['price'], y=df_bid['cum_qty'],
                    mode='lines', line=dict(color='#00ff00', width=2),
                    fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)',
                    name='Lực Mua (Bids)'
                ))
            
            # Vẽ vùng Đỏ (Lực Bán) - Cộng dồn khối lượng từ giá thấp lên cao
            if not df_ask.empty:
                df_ask = df_ask.groupby('price').sum().reset_index().sort_values('price')
                df_ask['cum_qty'] = df_ask['qty'].cumsum()
                fig_depth.add_trace(go.Scatter(
                    x=df_ask['price'], y=df_ask['cum_qty'],
                    mode='lines', line=dict(color='#ff4b4b', width=2),
                    fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.2)',
                    name='Lực Bán (Asks)'
                ))

            fig_depth.update_layout(
                xaxis_title="Mức Giá (VNĐ)",
                yaxis_title="Khối lượng tích lũy",
                margin=dict(l=20, r=20, t=20, b=20),
                height=350,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)' # Xóa nền lưới
            )
            st.plotly_chart(fig_depth, use_container_width=True)
        else:
            st.info("Chưa có lệnh chờ để vẽ biểu đồ.")

    # --- TAB 2: BIỂU ĐỒ GIÁ KHỚP (TICK CHART) ---
    with tab2:
        st.caption("Đường giá được vẽ chính xác từ từng lệnh đã khớp thành công.")
        
        real_trades = [t for t in st.session_state.trade_history if t["Mã CP"] == selected_symbol]
        
        if real_trades:
            # Lọc giá thật (Bỏ qua các lệnh Market không có giá cụ thể lưu lại để vẽ biểu đồ)
            prices = [float(t["Giá"].replace(',', '')) for t in real_trades if t["Giá"] != "MARKET"]
            
            if prices:
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    y=prices,
                    mode='lines+markers',
                    name='Giá khớp',
                    line=dict(color='#00d2ff', width=2),
                    marker=dict(size=6, color='#00d2ff')
                ))
                
                fig_line.update_layout(
                    xaxis_title="Thứ tự giao dịch (Cũ -> Mới)",
                    yaxis_title="Giá khớp (VNĐ)",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=350,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Chưa có đủ dữ liệu giá cụ thể để vẽ đường đồ thị.")
        else:
            st.info("Chưa có lệnh nào được khớp cho mã này.")
