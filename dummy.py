import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

# ============================================================
# KONFIGURASI DATABASE (otomatis deteksi mode)
# ============================================================
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

# ============================================================
# KONFIGURASI DATABASE (gunakan secrets.toml)
# ============================================================
try:
    DB_USER = st.secrets["DB_USER"]
    DB_PASS = st.secrets["DB_PASS"]
    DB_HOST = st.secrets["DB_HOST"]
    DB_PORT = st.secrets["DB_PORT"]
    DB_NAME = st.secrets["DB_NAME"]
except Exception as e:
    st.error("⚠️ Koneksi database belum dikonfigurasi dengan benar. Pastikan secrets.toml sudah terisi.")
    st.stop()

# Membuat koneksi engine
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ============================================================
# FUNGSI AMBIL DATA
# ============================================================
@st.cache_data(ttl=60)
def load_data():
    query = "SELECT * FROM app_record;"
    df = pd.read_sql(query, engine)
    return df

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(page_title="Dashboard Penjualan", layout="wide")
st.title("📊 Dashboard Penjualan (Live dari PostgreSQL)")
st.caption("Data otomatis diperbarui setiap beberapa detik dari database PostgreSQL.")

# ============================================================
# AUTO REFRESH
# ============================================================
refresh_rate = st.sidebar.slider("⏱️ Interval Refresh (detik)", 10, 120, 30)
st_autorefresh(interval=refresh_rate * 1000, limit=None, key="data_refresh")

# ============================================================
# LOAD & VISUALISASI DATA
# ============================================================
try:
    df = load_data()

    if df.empty:
        st.warning("⚠️ Data masih kosong di tabel 'cre_clean'.")
    else:
        # format tanggal jika ada
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        # Grafik Distribusi
        st.subheader("📈 Distribusi Tipe Pekerjaan")
        grouped = df.groupby("OCCUPATION_TYPE", as_index=False).size()
        grouped.columns = ["OCCUPATION_TYPE", "Count"]

        fig = px.bar(
            grouped,
            x="OCCUPATION_TYPE",
            y="Count",
            color="OCCUPATION_TYPE",
            title="Distribusi Tipe Pekerjaan",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

        # Dataframe Tabel
        st.subheader("📋 Data Lengkap")
        st.dataframe(df, use_container_width=True)

        # Tombol Download Data CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Data CSV",
            data=csv,
            file_name="data_penjualan.csv",
            mime="text/csv"
        )

        # Tombol Download Grafik PNG
        img_buffer = BytesIO()
        fig.write_image(img_buffer, format="png")
        st.download_button(
            label="🖼️ Download Grafik PNG",
            data=img_buffer.getvalue(),
            file_name="grafik_penjualan.png",
            mime="image/png"
        )

except Exception as e:
    st.error(f"❌ Gagal mengambil data: {e}")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("© 2025 Dashboard Streamlit PostgreSQL - by Andi")
