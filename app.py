import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# KONFIGURASI HALAMAN UTAMA (Mobile Friendly)
# ==========================================
st.set_page_config(page_title="Kavling Digital Pro", page_icon="🦅", layout="centered")

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
# PENGATURAN TERSEMBUNYI (Kalibrasi Broker & Modal)
# ==========================================
with st.expander("⚙️ Kalibrasi Broker, Modal & Risiko (Klik untuk Buka)"):
    st.markdown("**Kalibrasi Harga (Sync dengan MT5):**")
    broker_offset = st.number_input("⚖️ Geser Harga (Contoh: Jika App lebih tinggi $5, isi -5):", value=0.0, step=0.5)
    
    st.markdown("---")
    balance = st.number_input("💰 Saldo Akun (USD):", min_value=10.0, value=100.0, step=10.0)
    risk_percent = st.slider("🛡️ Batas Risiko per Trade (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# ==========================================
# KONTROL RADAR UTAMA
# ==========================================
st.subheader("📡 Radar Pasar Live")
col_a, col_b = st.columns(2)
with col_a:
    ticker_symbol = st.selectbox("Instrumen:", ["XAUUSD (Emas Spot)", "BTCUSD (Crypto)"])
with col_b:
    timeframe = st.selectbox("Timeframe:", ["5m", "15m", "30m", "1h"], index=1)

# TOMBOL SINKRONISASI MANUAL
if st.button("🔄 Sinkronkan Data Harga Sekarang", use_container_width=True):
    st.cache_data.clear()

# Tarik Data Live 
@st.cache_data(ttl=5)
def load_data(ticker, interval):
    period = "5d" if interval in ["5m", "15m", "30m"] else "1mo"
    df = yf.download(ticker, period=period, interval=interval, progress=False, ignore_tz=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.dropna(inplace=True)
    return df

# Menggunakan ticker SPOT GOLD (XAUUSD=X) agar lebih mirip MT5
ticker_code = "XAUUSD=X" if "XAUUSD" in ticker_symbol else "BTC-USD"
df = load_data(ticker_code, timeframe)

# MENERAPKAN KALIBRASI BROKER KE SEMUA DATA CHART
if broker_offset != 0.0:
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] + broker_offset

df = detect_support_resistance(df)

current_price = float(df['Close'].iloc[-1])
current_support = float(df['Support'].iloc[-1])
current_resistance = float(df['Resistance'].iloc[-1])

# Info Harga Ringkas
st.info(f"🏷️ **Harga Saat Ini:** ${current_price:,.2f} | 🟢 **Lantai:** ${current_support:,.2f} | 🔴 **Atap:** ${current_resistance:,.2f}")

# Chart Interaktif
fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Candlestick")])
fig.add_hline(y=current_support, line_dash="dash", line_color="#00cc96", annotation_text="Lantai (Buy Zone)")
fig.add_hline(y=current_resistance, line_dash="dash", line_color="#ef553b", annotation_text="Atap (Sell Zone)")
fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================
# KALKULATOR EKSEKUSI (Bawah Chart)
# ==========================================
st.subheader("🎯 Kalkulator Setup (Risk & Reward)")
trade_type = st.radio("Skenario Arah:", ["🟢 BUY (Pantulan Lantai)", "🔴 SELL (Penolakan Atap)"], horizontal=True)

# Input Harga Otomatis
entry_price = st.number_input("📍 Harga Entry (Masuk):", value=current_price, format="%.2f")
default_sl = current_support - 2.0 if "BUY" in trade_type else current_resistance + 2.0
stop_loss = st.number_input("🛑 Harga Stop Loss (Cut Loss):", value=default_sl, format="%.2f")

if st.button("🚀 Hitung & Cek Validasi AI", use_container_width=True):
    jarak_sl = abs(entry_price - stop_loss)
    risk_usd = balance * (risk_percent / 100)

    if jarak_sl == 0:
        st.error("❌ Stop Loss tidak boleh sama dengan Entry!")
    else:
        pip_value = 10 if "XAUUSD" in ticker_symbol else 1
        lot_size = risk_usd / (jarak_sl * pip_value)

        tp_1_2 = entry_price + (jarak_sl * 2) if "BUY" in trade_type else entry_price - (jarak_sl * 2)
        tp_1_3 = entry_price + (jarak_sl * 3) if "BUY" in trade_type else entry_price - (jarak_sl * 3)

        st.markdown("### 📋 Rencana Trading Anda:")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.success(f"📦 **Lot Aman:** {lot_size:.3f}")
            st.warning(f"💸 **Risiko (Uang Hilang):** ${risk_usd:,.2f}")
        with col_res2:
            st.info(f"🎯 **TP 1 (1:2):** ${tp_1_2:,.2f}")
            st.info(f"🚀 **TP 2 (1:3):** ${tp_1_3:,.2f}")

        st.divider()
        st.markdown("### 🧠 Keputusan AI Guard:")
        
        range_total = abs(current_resistance - current_support)
        if range_total > 0:
            batas_bawah = current_support + (range_total * 0.3)
            batas_atas = current_resistance - (range_total * 0.3)

            if batas_bawah < entry_price < batas_atas:
                 st.markdown("<div class='ai-guard-warning'><b>🚨 DILARANG ENTRY!</b><br>Harga berada di tengah-tengah area (No-Trade Zone). Emosi Anda sedang dipancing. Tunggu harga di Atap atau Lantai!</div>", unsafe_allow_html=True)
            else:
                 st.markdown("<div class='ai-guard-safe'><b>✅ APPROVED (DISETUJUI)!</b><br>Setup ini memiliki probabilitas tinggi (berada di Killzone). Ingat, tekan pelatuk hanya jika ada pola Pin Bar atau Engulfing!</div>", unsafe_allow_html=True)
