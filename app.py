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

    st.session_state.portfolio = {
        'FPT': 500,
        'VNM': 500,
        'VIC': 500
    }

    # trade history
    st.session_state.trade_history = []

    symbols = [
        'FPT', 'VNM', 'VIC', 'HPG', 'SSI',
        'VCB', 'VHM', 'TCB', 'VPB', 'MBB'
    ]

    for sym in symbols:
        st.session_state.trie.insert(sym)

    # tạo dữ liệu mẫu với giá thực tế (hàng chục nghìn vnđ)
    for _ in range(200):

        sym = random.choice(['FPT', 'VNM', 'VIC'])
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
    # ORDER FORM
    # =========================

    st.divider()

    st.header("Đặt lệnh mới")

    with st.form("order_form"):

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

        o_price = st.number_input(
            "Giá (VNĐ - bỏ qua nếu Market)",
            min_value=0.0,
            value=90000.0,
            step=100.0
        )

        o_qty = st.number_input(
            "Khối lượng",
            min_value=100,
            value=1000,
            step=100
        )

        submitted = st.form_submit_button(
            "Gửi lệnh vào hệ thống"
        )

        if submitted:

            estimated_cost = o_price * o_qty

            # =========================
            # BUY ORDER
            # =========================

            if o_side == "BUY":

                if st.session_state.balance < estimated_cost:

                    st.error(
                        "❌ Không đủ số dư để đặt lệnh mua"
                    )

                else:

                    st.session_state.balance -= estimated_cost

                    st.session_state.portfolio[selected_symbol] = (
                        st.session_state.portfolio.get(
                            selected_symbol,
                            0
                        ) + o_qty
                    )

                    new_order = Order(
                        order_id=uuid.uuid4().hex[:6].upper(),
                        symbol=selected_symbol,
                        side=o_side,
                        order_type=o_type,
                        price=o_price,
                        quantity=o_qty
                    )

                    start_t = time.perf_counter()

                    st.session_state.engine.process_order(
                        new_order
                    )

                    end_t = time.perf_counter()

                    # trade history với định dạng số đẹp
                    st.session_state.trade_history.append({

                    "Thời Gian": time.strftime("%H:%M:%S"),
                    "Mã CP": selected_symbol,
                    "Loại": o_side,
                    "Giá": f"{o_price:,.0f}",
                    "Khối Lượng": f"{o_qty:,}"
                    })

                    st.success(
                        f"""
                        ✅ Khớp lệnh
                        trong {(end_t - start_t)*1000:.4f} ms
                        """
                    )

            # =========================
            # SELL ORDER
            # =========================

            else:

                owned_qty = st.session_state.portfolio.get(
                    selected_symbol,
                    0
                )

                if owned_qty < o_qty:

                    st.error(
                        "❌ Không đủ cổ phiếu để bán"
                    )

                else:

                    st.session_state.portfolio[selected_symbol] -= o_qty

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

                    st.session_state.engine.process_order(
                        new_order
                    )

                    end_t = time.perf_counter()

                    # trade history
                    st.session_state.trade_history.append({

                        "Thời Gian": time.strftime("%H:%M:%S"),
                        "Mã CP": selected_symbol,
                        "Loại": o_side,
                        "Giá": f"{o_price:,.0f}",
                        "Khối Lượng": f"{o_qty:,}"
                    })

                    st.success(
                        f"""
                        ✅ Khớp lệnh/Thêm vào sổ thành công
                        trong {(end_t - start_t)*1000:.4f} ms
                        """
                    )

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

            df_asks = df_asks.iloc[::-1]

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
    # CHART
    # =====================================================

    st.divider()

    st.header(
        "Phân tích Kỹ thuật"
    )

    # cập nhật nến với giá trị thật (nhân 1000)
    dummy_candles = pd.DataFrame({

        'Date': pd.date_range(
            start='2026-05-01',
            periods=10
        ),

        'Open': [88000, 89000, 90000, 89000, 91000, 92000, 91000, 93000, 94000, 93000],

        'High': [90000, 91000, 91000, 92000, 93000, 94000, 93000, 95000, 96000, 95000],

        'Low': [87000, 88000, 88000, 88000, 90000, 91000, 90000, 92000, 92000, 91000],

        'Close': [89000, 90000, 89000, 91000, 92000, 91000, 93000, 94000, 93000, 95000]
    })

    fig = go.Figure(data=[

        go.Candlestick(

            x=dummy_candles['Date'],

            open=dummy_candles['Open'],

            high=dummy_candles['High'],

            low=dummy_candles['Low'],

            close=dummy_candles['Close'],

            increasing_line_color='green',

            decreasing_line_color='red'
        )
    ])

    fig.update_layout(

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),

        height=350,

        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
