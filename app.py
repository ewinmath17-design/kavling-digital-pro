import streamlit as st
import pandas as pd

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Kavling Digital Pro", page_icon="🦅", layout="wide")

# Header Aplikasi
st.title("🦅 Kavling Digital Pro")
st.markdown("**Asisten Kuantitatif Price Action & Absolute Risk Management**")
st.divider()

# Layout Kolom
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ Parameter Akun & Risiko")
    balance = st.number_input("Saldo Akun Saat Ini (USD):", min_value=10.0, value=1000.0, step=10.0)
    risk_percent = st.slider("Batas Risiko per Transaksi (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    
    st.markdown("---")
    st.subheader("🎯 Parameter Setup (Price Action)")
    instrument = st.selectbox("Instrumen:", ["XAUUSD (Gold)", "BTCUSD (Bitcoin)", "Forex Major"])
    trade_type = st.radio("Arah Eksekusi:", ["BUY (Long)", "SELL (Short)"])
    
    entry_price = st.number_input("Harga Entry:", format="%.2f")
    stop_loss = st.number_input("Harga Stop Loss (Lantai/Atap Beton):", format="%.2f")

with col2:
    st.subheader("📊 Analisis & Output Algoritma")
    
    if st.button("Hitung Parameter Eksekusi", type="primary"):
        if entry_price == 0 or stop_loss == 0:
            st.warning("⚠️ Masukkan Harga Entry dan Stop Loss terlebih dahulu!")
        elif entry_price == stop_loss:
            st.error("❌ Harga Entry dan Stop Loss tidak boleh sama.")
        else:
            # Kalkulasi Jarak SL (Pips/Poin)
            jarak_sl = abs(entry_price - stop_loss)
            
            # Kalkulasi Nilai Risiko dalam USD
            risk_usd = balance * (risk_percent / 100)
            
            # Simulasi Kasar Lot Size (Penyesuaian untuk XAU/BTC)
            if instrument == "XAUUSD (Gold)":
                pip_value = 10 # Standar 1 Lot Standard = $10/pip
                lot_size = risk_usd / (jarak_sl * pip_value)
            elif instrument == "BTCUSD (Bitcoin)":
                pip_value = 1 # Asumsi 1 Lot = 1 BTC
                lot_size = risk_usd / (jarak_sl * pip_value)
            else:
                lot_size = risk_usd / (jarak_sl * 10)

            # Kalkulasi Target Profit (Risk:Reward 1:2 dan 1:3)
            if trade_type == "BUY (Long)":
                tp_1_2 = entry_price + (jarak_sl * 2)
                tp_1_3 = entry_price + (jarak_sl * 3)
            else:
                tp_1_2 = entry_price - (jarak_sl * 2)
                tp_1_3 = entry_price - (jarak_sl * 3)

            # Menampilkan Hasil
            st.info(f"**Uang yang Direlakan (Absolute Risk):** ${risk_usd:,.2f} ({risk_percent}%)")
            st.success(f"**Ukuran Lot Maksimal:** {lot_size:.3f} Lot")
            
            st.markdown("### 🎯 Rekomendasi Target Profit (TP)")
            st.write(f"- **TP Minimal (RR 1:2):** {tp_1_2:,.2f} *(Profit: ${risk_usd * 2:,.2f})*")
            st.write(f"- **TP Optimal (RR 1:3):** {tp_1_3:,.2f} *(Profit: ${risk_usd * 3:,.2f})*")
            
            # AI Psychology Guard (Logika Jarak SL)
            st.markdown("---")
            st.subheader("🧠 AI Psychology Guard")
            if (instrument == "XAUUSD (Gold)" and jarak_sl > 5.0) or (instrument == "BTCUSD (Bitcoin)" and jarak_sl > 1000.0):
                st.error("🚨 **PERINGATAN:** Jarak Stop Loss terlalu lebar! Anda masuk di tengah jalan (No-Trade Zone). Batalkan eksekusi dan tunggu harga retest di Lantai/Atap beton.")
            else:
                st.success("✅ **STATUS:** Area Entry Ideal. Stop Loss ketat. Eksekusi diizinkan!")

st.divider()
st.caption("Kavling Digital Pro v1.0 - Built by System Architect & AI")
