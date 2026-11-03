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
# MATERI EDUKASI NTL
# ==========================================
with st.expander("📖 Panduan Membaca Data Night Time Light (NTL)"):
    st.markdown("""
    **Apa itu Night Time Light (NTL)?**
    NTL adalah data citra satelit yang menangkap emisi cahaya buatan manusia di malam hari (seperti lampu jalan, penerangan pabrik, perumahan, dan kendaraan). Data ini diperoleh dari sensor VIIRS (Visible Infrared Imaging Radiometer Suite) milik NASA/NOAA.

    **Mengapa NTL digunakan oleh BPS?**
    Pendaran cahaya malam hari memiliki korelasi positif yang kuat dengan aktivitas ekonomi, tingkat urbanisasi, dan kepadatan penduduk. NTL sering digunakan sebagai proksi independen untuk memantau pergerakan PDRB dan fenomena ekonomi spasial.

    **Cara Membaca Indikator NTL:**
    * **Nilai Absolut (Rata-rata NTL):** Semakin tinggi nilainya, semakin terang wilayah tersebut, mengindikasikan konsentrasi infrastruktur dan aktivitas ekonomi yang padat.
    * **Laju Pertumbuhan (QtQ / MtM / YoY):** 
        * **Positif (Naik):** Menunjukkan adanya ekspansi aktivitas, pembangunan infrastruktur baru, atau pemulihan ekonomi di wilayah tersebut.
        * **Negatif (Turun):** Bisa mengindikasikan perlambatan aktivitas ekonomi, penurunan konsumsi listrik, atau dampak dari bencana/pembatasan sosial.
    """)

# ==========================================
# 1. CACHE & BACA DATA EXCEL
# ==========================================
@st.cache_data
def load_data():
    df_triwulan = pd.read_excel('data_ntl_sumut_triwulanan.xlsx')
    df_bulanan = pd.read_excel('data_ntl_sumut_bulanan.xlsx')
    return df_triwulan, df_bulanan

df_triwulan, df_bulanan = load_data()

# ==========================================
# 2. SIDEBAR & FILTER DINAMIS
# ==========================================
st.sidebar.header("Filter Analisis")

# Toggle Pemilihan Dataset
jenis_analisis = st.sidebar.radio("Tingkat Analisis:", ["Triwulanan", "Bulanan"])
st.sidebar.markdown("---")

if jenis_analisis == "Triwulanan":
    list_tahun = sorted(df_triwulan['Tahun'].unique(), reverse=True)
    selected_tahun = st.sidebar.selectbox("Pilih Tahun", list_tahun)
    selected_triwulan = st.sidebar.selectbox("Pilih Triwulan", [1, 2, 3, 4], format_func=lambda x: f"Triwulan {x} (Q{x})")
    
    df_filtered = df_triwulan[(df_triwulan['Tahun'] == selected_tahun) & (df_triwulan['Triwulan'] == selected_triwulan)]
    judul_stat = f"Q{selected_triwulan} {selected_tahun}"
    laju_pendek_label = "QtQ NTL"
    laju_pendek_title = "Laju Pertumbuhan QtQ (Quarter-to-Quarter)"
    
else:
    list_tahun = sorted(df_bulanan['Tahun'].unique(), reverse=True)
    selected_tahun = st.sidebar.selectbox("Pilih Tahun", list_tahun)
    
    # Filter bulan berdasarkan tahun yang dipilih agar dinamis
    bulan_tersedia = df_bulanan[df_bulanan['Tahun'] == selected_tahun]['Bulan_Angka'].unique()
    bulan_indo = {1:'Januari', 2:'Februari', 3:'Maret', 4:'April', 5:'Mei', 6:'Juni', 7:'Juli', 8:'Agustus', 9:'September', 10:'Oktober', 11:'November', 12:'Desember'}
    
    selected_bulan_angka = st.sidebar.selectbox("Pilih Bulan", sorted(bulan_tersedia), format_func=lambda x: bulan_indo[x])
    
    df_filtered = df_bulanan[(df_bulanan['Tahun'] == selected_tahun) & (df_bulanan['Bulan_Angka'] == selected_bulan_angka)]
    judul_stat = f"{bulan_indo[selected_bulan_angka]} {selected_tahun}"
    laju_pendek_label = "MtM NTL"
    laju_pendek_title = "Laju Pertumbuhan MtM (Month-to-Month)"

# ==========================================
# 3. STATISTIK UTAMA SUMATERA UTARA
# ==========================================
st.subheader(f"Statistik NTL - {judul_stat}")

if df_filtered.empty:
    st.warning("Data untuk periode ini belum tersedia di dalam file Excel.")
else:
    rata_sumut = df_filtered['NTL'].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Rata-rata NTL Sumatera Utara", f"{rata_sumut:.4f}")
    col2.metric("Jumlah Kab/Kota Dianalisis", len(df_filtered))

    # ==========================================
    # 4. VISUALISASI GRAFIK INTERAKTIF
    # ==========================================
    st.subheader("Visualisasi Pertumbuhan NTL")
    
    tab1, tab2 = st.tabs(["Laju YoY", f"Laju {laju_pendek_label.split()[0]}"])
    
    with tab1:
        df_yoy = df_filtered.sort_values(by='YoY NTL', ascending=False)
        fig_yoy = px.bar(
            df_yoy, x='nmkab', y='YoY NTL', 
            title=f"Laju Pertumbuhan YoY (Year-on-Year) - {judul_stat}",
            labels={'nmkab': 'Kabupaten/Kota', 'YoY NTL': 'YoY (%)'},
            color='YoY NTL', color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

    with tab2:
        df_pendek = df_filtered.sort_values(by=laju_pendek_label, ascending=False)
        fig_pendek = px.bar(
            df_pendek, x='nmkab', y=laju_pendek_label, 
            title=f"{laju_pendek_title} - {judul_stat}",
            labels={'nmkab': 'Kabupaten/Kota', laju_pendek_label: f"{laju_pendek_label.split()[0]} (%)"},
            color=laju_pendek_label, color_continuous_scale='Magma'
        )
        st.plotly_chart(fig_pendek, use_container_width=True)

    # ==========================================
    # 5. TABEL RINCIAN
    # ==========================================
    st.subheader("Tabel Rincian per Kabupaten/Kota")
    df_tabel = df_filtered[['nmkab', 'NTL', laju_pendek_label, 'YoY NTL']].sort_values(by='NTL', ascending=False).reset_index(drop=True)
    
    st.dataframe(
        df_tabel.style.format({
            'NTL': '{:.4f}',
            laju_pendek_label: '{:.2f}%',
            'YoY NTL': '{:.2f}%'
        }), 
        use_container_width=True
    )

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 14px;'>"
    "Tim Neraca Produksi Sumatera Utara dibuat dengan ❤️ dan ☕</p>", 
    unsafe_allow_html=True
)
