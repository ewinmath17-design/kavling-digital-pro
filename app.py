import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. KONFIGURASI TAMPILAN PREMIUM
# ==========================================
st.set_page_config(page_title="Kavling Digital - Trading Vision", layout="wide", page_icon="📈")

# ==========================================
# 2. PANEL KONTROL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2642/2642503.png", width=80)
    st.header("⚙️ Command Center")
    st.markdown("Atur parameter kecerdasan buatan di sini.")
    
    API_KEY = st.text_input("🔑 Gemini API Key:", type="password", help="Kunci akses ke otak AI")
    
    st.divider()
    st.subheader("🎯 Parameter Eksekusi")
    # Fitur Dinamis: User bisa ganti Risk/Reward kapan saja
    rr_ratio = st.selectbox("Risk:Reward Ratio Target", ["1:1 (Agresif)", "1:1.5 (Moderat)", "1:2 (Standar)", "1:3 (Swing)"], index=2)
    
    # Fitur Dinamis: Gaya trading
    trading_style = st.radio("⏱️ Mode Trading", ["Scalping (Cepat)", "Day Trading (Harian)", "Swing Trading (Santai)"], index=0)
    
    st.divider()
    st.caption("Sistem beroperasi pada prototipe gratis tanpa komersialisasi API. Powered by Gemini Flash.")

# ==========================================
# 3. AREA KERJA UTAMA
# ==========================================
st.title("📈 Kavling Digital: AI Trading Vision Pro")
st.markdown("Unggah chart Anda untuk analisis teknikal dan manajemen risiko otomatis.")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    uploaded_files = st.file_uploader("Upload Multi-Timeframe Chart (Tarik & Lepas file di sini)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        images = []
        # Tampilan grid responsif untuk gambar
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file)
            images.append(img)
            cols[idx].image(img, caption=f"Visual Data {idx+1}", use_column_width="auto")

        if st.button("🚀 Eksekusi Mesin AI", use_container_width=True):
            with st.spinner(f"Menganalisis market dengan mode {trading_style}..."):
                
                trading_prompt = f"""
                Anda adalah Senior Quant Trader dan Mentor Trading yang sangat disiplin. 
                Gunakan mode: {trading_style}. Target Risk:Reward adalah {rr_ratio}.
                Analisis visual chart ini dengan presisi. Perhatikan struktur harga terhadap Moving Average.

                Keluarkan HANYA format markdown ini:

                ### 📊 Analisis Teknikal Terpadu
                * **Aset & Timeframe:** [Deteksi dari gambar]
                * **Korelasi Tren:** [Jelaskan korelasi antar timeframe dan posisi harga terhadap MA]
                
                ### 🎯 Sistem Eksekusi ({rr_ratio})
                * **📊 PROBABILITAS WIN:** [0-100%]
                * **💡 STATUS:** [EKSEKUSI SEKARANG / TAHAN DULU (WAIT) / DILARANG ENTRY]
                * **ACTION:** [BUY / SELL / WAIT]
                * **ENTRY PRICE:** [Harga presisi]
                * **STOP LOSS (SL):** [Tempatkan di swing terdekat]
                * **TAKE PROFIT (TP):** [Hitung matematis berdasarkan jarak SL dan {rr_ratio}]

                ---
                ### 🧠 Mentor Insights
                [Satu paragraf nasihat psikologi trading yang tenang, menyesuaikan dengan probabilitas setup di atas.]
                """
                
                try:
                    payload = [trading_prompt] + images
                    response = model.generate_content(payload)
                    st.success("Sistem Selesai Menganalisis!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Koneksi terputus: {e}")
else:
    st.warning("⚠️ Sistem siaga. Masukkan API Key di Panel Kontrol (sebelah kiri) untuk memulai.")