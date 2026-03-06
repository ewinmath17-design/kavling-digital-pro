import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# KONFIGURASI HALAMAN UTAMA (Mobile Friendly)
# ==========================================
st.set_page_config(page_title="Kavling Digital Pro", page_icon="🦅", layout="centered")

# CSS Custom untuk mempercantik tampilan peringatan AI
st.markdown("""
<style>
.ai-guard-safe {background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745;}
.ai-guard-warning {background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; border-left: 5px solid #dc3545;}
</style>
""", unsafe_allow_html=True)

st.title("🦅 Kavling Digital Pro")
st.caption("Asisten Trading AI berbasis Price Action & Absolute Risk")
st.divider()

# ==========================================
# FUNGSI DETEKSI SBR/RBS
# ==========================================
def detect_support_resistance(df, window=20):
    df['Support'] = df['Low'].rolling(window=window, center=False).min()
    df['Resistance'] = df['High'].rolling(window=window, center=False).max()
    return df

# ==========================================
# PENGATURAN TERSEMBUNYI (Hemat Layar HP)
# ==========================================
with st.expander("⚙️ Pengaturan Modal & Risiko (Klik untuk Buka)"):
    balance = st.number_input("💰 Saldo Akun (USD):", min_value=10.0, value=100.0, step=10.0)
    risk_percent = st.slider("🛡️ Batas Risiko per Trade (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# ==========================================
# KONTROL RADAR UTAMA
# ==========================================
st.subheader("📡 Radar Pasar Live")
col_a, col_b = st.columns(2)
with col_a:
    ticker_symbol = st.selectbox("Instrumen:", ["XAUUSD (Emas)", "BTCUSD (Crypto)"])
with col_b:
    timeframe = st.selectbox("Timeframe:", ["5m", "15m", "30m", "1h"], index=1)

# ==========================================
# TOMBOL SINKRONISASI MANUAL & PENARIK DATA CEPAT
# ==========================================
if st.button("🔄 Sinkronkan Data Harga Sekarang", use_container_width=True):
    st.cache_data.clear() # Memaksa sistem membuang data lama

# Tarik Data Live (Dipercepat menjadi 5 detik Cache)
@st.cache_data(ttl=5)
def load_data(ticker, interval):
    period = "5d" if interval in ["5m", "15m", "30m"] else "1mo"
    # Mengambil data langsung tanpa delay timezone
    df = yf.download(ticker, period=period, interval=interval, progress=False, ignore_tz=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.dropna(inplace=True)
    return df

ticker_code = "GC=F" if "XAUUSD" in ticker_symbol else "BTC-USD"
df = load_data(ticker_code, timeframe)
df = detect_support_resistance(df)

current_price = float(df['Close'].iloc[-1])
current_support = float(df['Support'].iloc[-1])
current_resistance = float(df['Resistance'].iloc[-1])

# Info Harga Ringkas
st.info(f"🏷️ **Harga Saat Ini:** ${current_price:,.2f} | 🟢 **Lantai:** ${current_support:,.2f} | 🔴 **Atap:** ${current_resistance:,.2f}")

# Chart Interaktif yang disesuaikan untuk HP
fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Candlestick")])
fig.add_hline(y=current_support, line_dash="dash", line_color="#00cc96", annotation_text="Lantai (Buy Zone)")
fig.add_hline(y=current_resistance, line_dash="dash", line_color="#ef553b", annotation_text="Atap (Sell Zone)")
fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
st.
