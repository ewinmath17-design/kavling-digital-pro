import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="Kavling Digital Pro | Gold Edition", page_icon="🥇", layout="wide")

st.title("🥇 Kavling Digital Pro: XAUUSD Master AI")
st.markdown("**Sistem Trading Kuantitatif Berbasis Price Action murni & Absolute Risk Management**")
st.markdown("*Terinspirasi dari kejeniusan Paul Tudor Jones, George Soros, dan Mark Douglas.*")
st.divider()

# ==========================================
# FUNGSI DETEKSI SUPPORT & RESISTANCE (SBR/RBS)
# ==========================================
def detect_support_resistance(df, window=20):
    """Mendeteksi area pijakan (Lantai/Support) dan atap (Resistance) secara otomatis"""
    df['Support'] = df['Low'].rolling(window=window, center=False).min()
    df['Resistance'] = df['High'].rolling(window=window, center=False).max()
    return df

# ==========================================
# SIDEBAR: KONTROL RADAR & RISIKO
# ==========================================
with st.sidebar:
    st.header("⚙️ Radar Multi-Timeframe")
    # Menggunakan GC=F (Gold Futures) sebagai proxy XAUUSD live gratis terbaik
    ticker_symbol = st.selectbox("Instrumen Pasar:", ["GC=F (Emas/XAUUSD Proxy)", "BTC-USD (Bitcoin)"])
    timeframe = st.selectbox("Pilih Timeframe:", ["5m", "15m", "30m", "1h", "1d"], index=1)
    
    st.header("💼 Parameter Akun (Tudor Jones Logic)")
    balance = st.number_input("Saldo Akun (USD):", min_value=10.0, value=1000.0, step=10.0)
    risk_percent = st.slider("Risiko per Transaksi (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# ==========================================
# MENARIK DATA PASAR LIVE
# ==========================================
@st.cache_data(ttl=60) # Cache data selama 60 detik agar aplikasi tidak lemot
def load_data(ticker, interval):
    period = "5d" if interval in ["5m", "15m", "30m"] else "1mo"
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    df.columns = df.columns.droplevel(1) # Membersihkan format YFinance baru
    df.dropna(inplace=True)
    return df

data_load_state = st.text('Mendeteksi sinyal pasar dari satelit...')
df = load_data("GC=F" if "GC=F" in ticker_symbol else "BTC-USD", timeframe)
df = detect_support_resistance(df)
data_load_state.text('Data pasar live berhasil disinkronisasi! ✅')

current_price = df['Close'].iloc[-1]
current_support = df['Support'].iloc[-1]
current_resistance = df['Resistance'].iloc[-1]

# ==========================================
# LAYAR UTAMA: LAYOUT KOLOM (CHART & KALKULATOR)
# ==========================================
col1, col2 = st.columns([2, 1]) # Kolom Chart lebih lebar dari Kalkulator

with col1:
    st.subheader(f"📊 Radar Price Action: {ticker_symbol} ({timeframe})")
    
    # Menggambar Chart Candlestick Ala MetaTrader
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'],
                    name="Candlestick")])
    
    # Menambahkan Garis Lantai Beton (Support) & Atap Beton (Resistance)
    fig.add_hline(y=current_support, line_dash="dash", line_color="green", annotation_text="Lantai Beton (Support)")
    fig.add_hline(y=current_resistance, line_dash="dash", line_color="red", annotation_text="Atap Beton (Resistance)")
    
    fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark",
                      margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Status Market Live
    st.info(f"**Harga Saat Ini:** ${current_price:,.2f} | **Area Tunggu Bawah:** ${current_support:,.2f} | **Area Tunggu Atas:** ${current_resistance:,.2f}")

with col2:
    st.subheader("🤖 Kalkulator Eksekusi & AI Guard")
    trade_type = st.radio("Skenario Probabilitas:", ["BUY (Pengecekan Lantai)", "SELL (Pengecekan Atap)"])
    
    # Otomatis mengisi harga entry dengan harga saat ini agar user tidak repot
    entry_price = st.number_input("Harga Entry Target:", value=float(current_price), format="%.2f")
    stop_loss = st.number_input("Harga Stop Loss (Wajib):", value=float(current_support - 2 if trade_type == "BUY (Pengecekan Lantai)" else current_resistance + 2), format="%.2f")
    
    if st.button("Tembak Resolusi Eksekusi", type="primary"):
        jarak_sl = abs(entry_price - stop_loss)
        risk_usd = balance * (risk_percent / 100)
        
        # Validasi SL tidak logis
        if jarak_sl == 0:
            st.error("❌ Stop Loss tidak boleh sama dengan Entry!")
        else:
            # Kalkulasi Lot (Asumsi Emas 1 Lot = $10/pip, BTC = 1 Lot/poin)
            pip_value = 10 if "GC=F" in ticker_symbol else 1
            lot_size = risk_usd / (jarak_sl * pip_value)
            
            # Kalkulasi TP ala Paul Tudor Jones (1:2 & 1:3)
            if "BUY" in trade_type:
                tp_1_2 = entry_price + (jarak_sl * 2)
                tp_1_3 = entry_price + (jarak_sl * 3)
            else:
                tp_1_2 = entry_price - (jarak_sl * 2)
                tp_1_3 = entry_price - (jarak_sl * 3)
                
            # --- TAMPILAN HASIL ---
            st.success(f"**Ukuran Lot Maksimal:** {lot_size:.3f} Lot")
            st.warning(f"**Uang Ter-Risiko:** ${risk_usd:,.2f} ({risk_percent}% dari Modal)")
            
            st.markdown("### 🎯 Target Profit Institusi")
            st.write(f"- **TP 1 (RR 1:2):** ${tp_1_2:,.2f}")
            st.write(f"- **TP 2 (RR 1:3):** ${tp_1_3:,.2f}")
            
            # --- AI PSYCHOLOGY GUARD (MARK DOUGLAS LOGIC) ---
            st.markdown("---")
            if (entry_price > current_support + (abs(current_resistance-current_support)*0.3)) and (entry_price < current_resistance - (abs(current_resistance-current_support)*0.3)):
                 st.error("🚨 **AI GUARD WARNING:** Harga berada di TENGAH-TENGAH area konsolidasi. Anda melanggar aturan Naked Forex. Dilarang Entry! Tunggu harga mendekati Lantai/Atap.")
            else:
                 st.success("✅ **AI GUARD APPROVED:** Anda berada di Killzone. Setup memiliki probabilitas tinggi. Jaga disiplin Anda!")
