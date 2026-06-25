import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Page Config
st.set_page_config(page_title="Nifty Institutional Tracker", layout="wide")

# --- CSS for better styling ---
st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Nifty 50 Institutional Strategy Dashboard")

# --- Sidebar ---
st.sidebar.header("Strategy Settings")
timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 10, 120, 30)

# --- Logic Functions ---
def get_live_data(ticker, interval):
    try:
        # We fetch a bit more data to ensure technical indicators have enough padding
        data = yf.download(ticker, period="5d", interval=interval, progress=False)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def calculate_zones(price):
    return {
        "red": round(price / 20) * 20,
        "orange": round(price / 100) * 100,
        "green": round(price / 250) * 250
    }

# --- Dashboard Content ---
placeholder = st.empty()

# Streamlit scripts rerun on interaction. 
# This loop handles the "Live" update feel.
while True:
    with placeholder.container():
        df = get_live_data("^NSEI", timeframe)
        
        if df is not None:
            # Handle potential multi-index columns from yfinance
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            price_diff = current_price - prev_price
            
            zones = calculate_zones(current_price)
            
            # --- Top Metrics ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Nifty 50", f"{current_price:,.2f}", f"{price_diff:,.2f}")
            m2.metric("Red Zone (Scalp)", f"{zones['red']}")
            m3.metric("Orange (100)", f"{zones['orange']}")
            m4.metric("Green (250)", f"{zones['green']}")

            # --- Signal Logic ---
            dist_to_orange = current_price - zones['orange']
            
            if abs(dist_to_orange) < 15:
                signal_text, color = "WAIT - AT ZONE", "#FFA500" # Orange
            elif dist_to_orange > 0:
                signal_text, color = "BULLISH BIAS", "#00FF00" # Green
            else:
                signal_text, color = "BEARISH BIAS", "#FF0000" # Red

            st.markdown(f"""
                <div style="padding:20px; border-radius:10px; background-color:{color}22; border: 2px solid {color}; text-align:center;">
                    <h2 style="color:{color}; margin:0;">{signal_text}</h2>
                    <p style="margin:0;">Price is {abs(dist_to_orange):.2f} pts from Institutional Orange Zone</p>
                </div>
            """, unsafe_allow_html=True)

            # --- Visuals ---
            st.subheader("Price Movement")
            st.line_chart(df['Close'].tail(100))
            
            # --- Table ---
            st.subheader("Institutional Zone Breakdown")
            zones_data = {
                "Zone Type": ["Red (20)", "Orange (100)", "Green (250)"],
                "Level": [zones['red'], zones['orange'], zones['green']],
                "Distance": [current_price - zones['red'], current_price - zones['orange'], current_price - zones['green']],
                "Context": ["Scalping / Momentum", "Institutional Supply/Demand", "Major Trend Pivot"]
            }
            st.table(pd.DataFrame(zones_data))
            
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("Waiting for market data...")

    time.sleep(refresh_rate)
    st.rerun()