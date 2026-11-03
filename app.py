import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard NTL Sumatera Utara", page_icon="💡", layout="wide")
st.title("Pemantauan Night Time Light (NTL) Sumatera Utara")
st.markdown("Dashboard ini menampilkan agregasi intensitas cahaya malam hari dari satelit VIIRS sebagai proksi aktivitas ekonomi spasial.")

# ==========================================
# MATERI EDUKASI NTL (Bisa dilipat/expander)
# ==========================================
with st.expander("📖 Panduan Membaca Data Night Time Light (NTL)"):
    st.markdown("""
    **Apa itu Night Time Light (NTL)?**
    NTL adalah data citra satelit yang menangkap emisi cahaya buatan manusia di malam hari (seperti lampu jalan, penerangan pabrik, perumahan, dan kendaraan). Data ini diperoleh dari sensor VIIRS (Visible Infrared Imaging Radiometer Suite) milik NASA/NOAA.

    **Mengapa NTL digunakan oleh BPS?**
    Pendaran cahaya malam hari memiliki korelasi positif yang kuat dengan aktivitas ekonomi, tingkat urbanisasi, dan kepadatan penduduk. NTL sering digunakan sebagai proksi independen untuk memantau pergerakan PDRB dan fenomena ekonomi spasial yang sulit direkam oleh survei konvensional.

    **Cara Membaca Indikator NTL:**
    * **Nilai Absolut (Rata-rata NTL):** Semakin tinggi nilainya, semakin terang wilayah tersebut, yang mengindikasikan konsentrasi infrastruktur dan aktivitas ekonomi yang padat (biasanya kota besar akan memiliki NTL jauh lebih tinggi dari kabupaten).
    * **Laju Pertumbuhan (QtQ / YoY):** 
        * **Positif (Naik):** Menunjukkan adanya ekspansi aktivitas, pembangunan infrastruktur baru, atau pemulihan ekonomi di wilayah tersebut dibandingkan periode sebelumnya.
        * **Negatif (Turun):** Bisa mengindikasikan perlambatan aktivitas ekonomi, penurunan konsumsi listrik, atau dampak dari bencana/pembatasan sosial.
    """)

# ==========================================
# 1. CACHE & BACA DATA EXCEL
# ==========================================
@st.cache_data
def load_data():
    # Pastikan file excel berada di dalam folder 'data'
    df = pd.read_excel('data_ntl_sumut_triwulanan.xlsx')
    return df

df_ntl = load_data()

# ==========================================
# 2. SIDEBAR & FILTER DINAMIS
# ==========================================
st.sidebar.header("Filter Waktu")

list_tahun = sorted(df_ntl['Tahun'].unique(), reverse=True)
selected_tahun = st.sidebar.selectbox("Pilih Tahun", list_tahun)
selected_triwulan = st.sidebar.selectbox("Pilih Triwulan", [1, 2, 3, 4], format_func=lambda x: f"Triwulan {x} (Q{x})")

df_filtered = df_ntl[(df_ntl['Tahun'] == selected_tahun) & (df_ntl['Triwulan'] == selected_triwulan)]

# ==========================================
# 3. STATISTIK UTAMA SUMATERA UTARA
# ==========================================
st.subheader(f"Statistik NTL - Q{selected_triwulan} {selected_tahun}")

if df_filtered.empty:
    st.warning("Data untuk periode ini belum tersedia di dalam file Excel.")
else:
    # Nilai Rata-rata Sumatera Utara dihitung di sini
    rata_sumut = df_filtered['NTL'].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Rata-rata NTL Sumatera Utara", f"{rata_sumut:.4f}")
    col2.metric("Jumlah Kab/Kota Dianalisis", len(df_filtered))

    # ==========================================
    # 4. VISUALISASI GRAFIK INTERAKTIF
    # ==========================================
    st.subheader("Visualisasi Pertumbuhan NTL")
    
    tab1, tab2 = st.tabs(["Laju YoY", "Laju QtQ"])
    
    with tab1:
        df_yoy = df_filtered.sort_values(by='YoY NTL', ascending=False)
        fig_yoy = px.bar(
            df_yoy, x='nmkab', y='YoY NTL', 
            title="Laju Pertumbuhan YoY (Year-on-Year)",
            labels={'nmkab': 'Kabupaten/Kota', 'YoY NTL': 'YoY (%)'},
            color='YoY NTL', color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

    with tab2:
        df_qtq = df_filtered.sort_values(by='QtQ NTL', ascending=False)
        fig_qtq = px.bar(
            df_qtq, x='nmkab', y='QtQ NTL', 
            title="Laju Pertumbuhan QtQ (Quarter-to-Quarter)",
            labels={'nmkab': 'Kabupaten/Kota', 'QtQ NTL': 'QtQ (%)'},
            color='QtQ NTL', color_continuous_scale='Magma'
        )
        st.plotly_chart(fig_qtq, use_container_width=True)

    # ==========================================
    # 5. TABEL RINCIAN
    # ==========================================
    st.subheader("Tabel Rincian per Kabupaten/Kota")
    df_tabel = df_filtered[['nmkab', 'NTL', 'QtQ NTL', 'YoY NTL']].sort_values(by='NTL', ascending=False).reset_index(drop=True)
    
    st.dataframe(
        df_tabel.style.format({
            'NTL': '{:.4f}',
            'QtQ NTL': '{:.2f}%',
            'YoY NTL': '{:.2f}%'
        }), 
        use_container_width=True
    )

# ==========================================
# FOOTER
# ==========================================
st.markdown("---") # Garis pembatas horizontal
# Footer teks berada di tengah dengan HTML/CSS sederhana
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 14px;'>"
    "Tim Neraca Produksi Sumatera Utara dibuat dengan ❤️ dan ☕</p>", 
    unsafe_allow_html=True
)
