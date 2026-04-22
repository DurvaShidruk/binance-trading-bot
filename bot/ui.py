import streamlit as st
import pandas as pd

from .config import SUPPORTED_SYMBOLS, get_settings
from .orders import place_order, get_history, build_preview
from .logging_config import tail_log


def _inject_css(dark: bool) -> None:
    bg = "#0b0d12" if dark else "#f7f8fb"
    fg = "#e6e8ef" if dark else "#0b0d12"
    card = "#141821" if dark else "#ffffff"
    border = "#1f2430" if dark else "#e6e8ef"
    muted = "#8a93a6" if dark else "#5b6478"
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {bg}; color: {fg}; }}
        section[data-testid="stSidebar"] {{ background: {card}; }}
        .tb-card {{
            background: {card}; border: 1px solid {border};
            border-radius: 14px; padding: 20px 22px; margin-bottom: 16px;
        }}
        .tb-title {{ font-size: 28px; font-weight: 700; margin: 0; color: {fg}; }}
        .tb-sub {{ color: {muted}; margin-top: 4px; font-size: 14px; }}
        .tb-label {{ color: {muted}; font-size: 12px; text-transform: uppercase;
                     letter-spacing: 0.08em; margin-bottom: 4px; }}
        .tb-value {{ font-size: 18px; font-weight: 600; color: {fg}; }}
        .tb-pill {{ display:inline-block; padding: 4px 10px; border-radius: 999px;
                    font-size: 12px; font-weight: 600; }}
        .tb-buy {{ background: rgba(34,197,94,.15); color: #22c55e; }}
        .tb-sell {{ background: rgba(239,68,68,.15); color: #ef4444; }}
        .tb-ok {{ background: rgba(34,197,94,.12); border: 1px solid #22c55e;
                  color: #22c55e; padding: 10px 14px; border-radius: 10px; }}
        .tb-err {{ background: rgba(239,68,68,.12); border: 1px solid #ef4444;
                   color: #ef4444; padding: 10px 14px; border-radius: 10px; }}
        .tb-warn {{ background: rgba(234,179,8,.10); border: 1px solid #eab308;
                    color: #eab308; padding: 10px 14px; border-radius: 10px; }}
        .stButton > button {{ border-radius: 10px; font-weight: 600; }}
        pre {{ background: {bg} !important; border: 1px solid {border};
               border-radius: 10px; padding: 12px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _result_card(result):
    side_cls = "tb-buy" if result.side == "BUY" else "tb-sell"
    if result.success:
        st.markdown(
            f'<div class="tb-ok"> {result.message} '
            f'<span style="opacity:.8">({result.elapsed_ms} ms)</span></div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(4)
        cols[0].markdown(f'<div class="tb-label">Order ID</div><div class="tb-value">{result.orderId}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="tb-label">Status</div><div class="tb-value">{result.status}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="tb-label">Executed</div><div class="tb-value">{result.executedQty}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="tb-label">Avg Price</div><div class="tb-value">{result.avgPrice or "-"}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="margin-top:10px"><span class="tb-pill {side_cls}">{result.side}</span> '
            f'<span style="opacity:.7">{result.symbol} • {result.type}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div class="tb-err"> {result.message}</div>', unsafe_allow_html=True)


def run() -> None:
    st.set_page_config(page_title="Futures Testnet Bot", page_icon="📈", layout="wide")

    if "dark" not in st.session_state:
        st.session_state.dark = True
    if "pending" not in st.session_state:
        st.session_state.pending = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    with st.sidebar:
        st.markdown("###  Settings")
        st.session_state.dark = st.toggle("Dark mode", value=st.session_state.dark)
        settings = get_settings()
        status = " Connected" if settings.is_configured else " Missing API keys"
        st.caption(f"Endpoint: `{settings.base_url}`")
        st.caption(status)
        st.markdown("---")
        st.caption("Testnet only. No real funds are used.")

    _inject_css(st.session_state.dark)

    st.markdown('<p class="tb-title"> Binance Futures Testnet Bot</p>', unsafe_allow_html=True)
    st.markdown('<p class="tb-sub">Place MARKET, LIMIT and STOP orders with live preview, retries and full audit logs.</p>', unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="tb-card">', unsafe_allow_html=True)
        st.subheader("New Order")
        symbol = st.selectbox("Symbol", SUPPORTED_SYMBOLS, index=0)
        side = st.radio("Side", ["BUY", "SELL"], horizontal=True)
        order_type = st.selectbox("Order type", ["MARKET", "LIMIT", "STOP"])
        quantity = st.number_input("Quantity", min_value=0.0, value=0.001, step=0.001, format="%.6f")

        price = None
        stop_price = None
        if order_type == "LIMIT":
            price = st.number_input("Limit price (USDT)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
        elif order_type == "STOP":
            c1, c2 = st.columns(2)
            with c1:
                stop_price = st.number_input("Stop price", min_value=0.0, value=0.0, step=1.0, format="%.2f")
            with c2:
                price = st.number_input("Limit price", min_value=0.0, value=0.0, step=1.0, format="%.2f")

        if st.button("Preview order", use_container_width=True, type="primary"):
            st.session_state.pending = dict(
                symbol=symbol, side=side, order_type=order_type,
                quantity=quantity, price=price, stop_price=stop_price,
            )

        if st.session_state.pending:
            p = st.session_state.pending
            preview = build_preview(**p)
            side_cls = "tb-buy" if p["side"] == "BUY" else "tb-sell"
            st.markdown(
                f'<div class="tb-warn" style="margin-top:12px"> <b>Trade preview</b><br>'
                f'<span class="tb-pill {side_cls}" style="margin-top:6px">{p["side"]}</span> '
                f'<span style="margin-left:8px">{preview}</span></div>',
                unsafe_allow_html=True,
            )
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(" Confirm & place", use_container_width=True):
                    with st.spinner("Placing order..."):
                        st.session_state.last_result = place_order(**p)
                    st.session_state.pending = None
                    st.rerun()
            with cc2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending = None
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="tb-card">', unsafe_allow_html=True)
        st.subheader("Result")
        if st.session_state.last_result:
            _result_card(st.session_state.last_result)
        else:
            st.caption("Submit an order to see the response here.")
        st.markdown("</div>", unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1], gap="large")
    with b1:
        st.markdown('<div class="tb-card">', unsafe_allow_html=True)
        st.subheader("Order History")
        history = get_history(5)
        if not history:
            st.caption("No orders yet.")
        else:
            df = pd.DataFrame([{
                "Time": h.get("raw", {}).get("updateTime", ""),
                "Symbol": h.get("symbol"),
                "Side": h.get("side"),
                "Type": h.get("type"),
                "Qty": h.get("executedQty") or "-",
                "Price": h.get("avgPrice") or h.get("price") or "-",
                "Status": h.get("status") or ("OK" if h.get("success") else "FAIL"),
            } for h in history])
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="tb-card">', unsafe_allow_html=True)
        st.subheader("Logs")
        st.code(tail_log(15) or "(empty)", language="log")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    run()
