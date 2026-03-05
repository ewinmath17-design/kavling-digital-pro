import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="Kavling Digital Pro | Gold Edition", page_icon="🥇", layout="wide")

st.title("🥇 Kavling Digital Pro: XAUUSD Master AI")
st.markdown("**Sistem Trading Kuantitatif Berbasis Price Action murni & Absolute Risk Management**")
st.divider()

# ==========================================
# FUNGSI DETEKSI SUPPORT & RESISTANCE (SBR/RBS)
# ==========================================
def detect_support_resistance(df, window=20):
    df['Support'] = df['Low'].rolling(window=window, center=False).min()
    df['Resistance'] = df['High'].rolling(window=window, center=False).max()
    return df

# ==========================================
# SIDEBAR: KONTROL RADAR & RISIKO
# ==========================================
with st.sidebar:
    st.header("⚙️ Radar Multi-Timeframe")
    ticker_symbol = st.selectbox("Instrumen Pasar:", ["GC=F (Emas/XAUUSD Proxy)", "BTC-USD (Bitcoin)"])
    timeframe = st.selectbox("Pilih Timeframe:", ["5m", "15m", "30m", "1h"], index=1)
    
    st.header("💼 Parameter Akun & Risiko")
    balance = st.number_input("Saldo Akun (USD):", min_value=10.0, value=1000.0, step=10.0)
    risk_percent = st.slider("Risiko per Transaksi (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# ==========================================
# MENARIK DATA PASAR LIVE
# ==========================================
@st.cache_data(ttl=60)
def load_data(ticker, interval):
    period = "5d" if interval in ["5m", "15m", "30m"] else "1mo"
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    # Menangani format multi-index YFinance terbaru jika ada
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.dropna(inplace=True)
    return df

ticker_code = "GC=F" if "GC=F" in ticker_symbol else "BTC-USD"
df = load_data(ticker_code, timeframe)
df = detect_support_resistance(df)

current_price = float(df['Close'].iloc[-1])
current_support = float(df['Support'].iloc[-1])
current_resistance = float(df['Resistance'].iloc[-1])

# ==========================================
# LAYAR UTAMA: LAYOUT KOLOM (CHART & KALKULATOR)
# ==========================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Radar Price Action: {ticker_symbol} ({timeframe})")
    
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'],
                    name="Candlestick")])
    
    fig.add_hline(y=current_support, line_dash="dash", line_color="green", annotation_text="Lantai (Support)")
    fig.add_hline(y=current_resistance, line_dash="dash", line_color="red", annotation_text="Atap (Resistance)")
    
    fig.update_layout(xaxis_rangeslider_visible=False, height=450, template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"**Harga Saat Ini:** ${current_price:,.2f} | **Support:** ${current_support:,.2f} | **Resistance:** ${current_resistance:,.2f}")

with col2:
    st.subheader("🤖 Kalkulator Eksekusi & AI Guard")
    trade_type = st.radio("Skenario Probabilitas:", ["BUY (Pijakan Lantai)", "SELL (Tolak Atap)"])
    
    entry_price = st.number_input("Harga Entry Target:", value=current_price, format="%.2f")
    default_sl = current_support - 2.0 if "BUY" in trade_type else current_resistance + 2.0
    stop_loss = st.number_input("Harga Stop Loss (Wajib):", value=default_sl, format="%.2f")
    
    if st.button("Hitung Eksekusi", type="primary"):
        jarak_sl = abs(entry_price - stop_loss)
        risk_usd = balance * (risk_percent / 100)
        
        if jarak_sl == 0:
            st.error("❌ Stop Loss tidak boleh sama dengan Entry!")
        else:
            pip_value = 10 if "GC=F" in ticker_symbol else 1
            lot_size = risk_usd / (jarak_sl * pip_value)
            
            if "BUY" in trade_type:
                tp_1_2 = entry_price + (jarak_sl * 2)
                tp_1_3 = entry_price + (jarak_sl * 3)
            else:
                tp_1_2 = entry_price - (jarak_sl * 2)
                tp_1_3 = entry_price - (jarak_sl * 3)
                
            st.success(f"**Ukuran Lot Maksimal:** {lot_size:.3f} Lot")
            st.warning(f"**Uang Ter-Risiko:** ${risk_usd:,.2f}")
            
            st.markdown("### 🎯 Target Profit")
            st.write(f"- **TP 1 (RR 1:2):** ${tp_1_2:,.2f}")
            st.write(f"- **TP 2 (RR 1:3):** ${tp_1_3:,.2f}")
            
            st.markdown("---")
            # Logika AI Guard
            range_total = abs(current_resistance - current_support)
            if range_total > 0:
                batas_bawah = current_support + (range_total * 0.3)
                batas_atas = current_resistance - (range_total * 0.3)
                
                if batas_bawah < entry_price < batas_atas:
                     st.error("🚨 **AI GUARD WARNING:** Harga di TENGAH area konsolidasi (No-Trade Zone). Dilarang Entry!")
                else:
                     st.success("✅ **AI GUARD APPROVED:** Anda berada di Killzone. Setup probabilitas tinggi!")
