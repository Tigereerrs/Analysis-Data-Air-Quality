from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
MUSIM = {12: "Musim Dingin", 1: "Musim Dingin", 2: "Musim Dingin",
         3: "Musim Semi", 4: "Musim Semi", 5: "Musim Semi",
         6: "Musim Panas", 7: "Musim Panas", 8: "Musim Panas",
         9: "Musim Gugur", 10: "Musim Gugur", 11: "Musim Gugur"}
URUT_MUSIM = ["Musim Dingin", "Musim Semi", "Musim Panas", "Musim Gugur"]
BATAS = [0, 35, 75, 115, 150, 250, np.inf]
LABEL = ["Baik", "Sedang", "Tidak sehat (sensitif)", "Tidak sehat", "Sangat tidak sehat", "Berbahaya"]
WARNA_KATEGORI = ["#2E9E5B", "#F1C40F", "#E67E22", "#D35400", "#A93226", "#6C3483"]
AMBANG = 75

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv(Path(__file__).parent / "main_data.csv", parse_dates=["date"])
    df["musim"] = df["month"].map(MUSIM)
    df["kategori"] = pd.cut(df["PM2.5"], bins=BATAS, labels=LABEL)
    return df


def sorot(nilai, tinggi, rendah):
    if nilai == tinggi:
        return "#C0392B"
    if nilai == rendah:
        return "#2E86AB"
    return "#B0B7BD"


data = load_data()

# ---------------- Sidebar ----------------
st.sidebar.header("Filter Data")
semua_stasiun = sorted(data["station"].unique())
stasiun_dipilih = st.sidebar.multiselect("Stasiun", semua_stasiun, default=semua_stasiun)
tgl_min, tgl_max = data["date"].min().date(), data["date"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(tgl_min, tgl_max), min_value=tgl_min, max_value=tgl_max)
st.sidebar.caption(f"Ambang PM2.5 harian: {AMBANG} µg/m³ (standar Tiongkok Grade II, rata-rata 24 jam).")

if not isinstance(rentang, (list, tuple)) or len(rentang) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada filter di sebelah kiri.")
    st.stop()
if not stasiun_dipilih:
    st.warning("Pilih minimal satu stasiun.")
    st.stop()

df = data[
    data["station"].isin(stasiun_dipilih)
    & (data["date"] >= pd.to_datetime(rentang[0]))
    & (data["date"] <= pd.to_datetime(rentang[1]))
]
if df.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()

# ---------------- Header & ringkasan ----------------
st.title("Dashboard Kualitas Udara Beijing (PM2.5)")
st.caption("Data: Air Quality Dataset, 12 stasiun pemantauan, 1 Maret 2013 – 28 Februari 2017. Nilai harian merupakan rata-rata dari data per jam.")

ringkasan = df.groupby("station").agg(rata_rata=("PM2.5", "mean"), persen_hari=("over_75", "mean"))
ringkasan["persen_hari"] *= 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rata-rata PM2.5", f"{df['PM2.5'].mean():.1f} µg/m³")
c2.metric(f"Hari di atas {AMBANG} µg/m³", f"{df['over_75'].mean() * 100:.1f}%")
c3.metric("Stasiun tertinggi", ringkasan["rata_rata"].idxmax(), f"{ringkasan['rata_rata'].max():.1f} µg/m³", delta_color="off")
c4.metric("Stasiun terendah", ringkasan["rata_rata"].idxmin(), f"{ringkasan['rata_rata'].min():.1f} µg/m³", delta_color="off")

# ---------------- Pertanyaan 1 ----------------
st.header("Pertanyaan 1: PM2.5 per Stasiun")
st.write("Stasiun mana yang memiliki PM2.5 tertinggi dan terendah, dan berapa persen hari yang melampaui 75 µg/m³?")

d1 = ringkasan.sort_values("rata_rata", ascending=True)
fig, axes = plt.subplots(1, 2, figsize=(14, max(3.5, 0.5 * len(d1) + 1.5)), sharey=True)
w1 = [sorot(v, d1["rata_rata"].max(), d1["rata_rata"].min()) for v in d1["rata_rata"]]
axes[0].barh(d1.index, d1["rata_rata"], color=w1)
axes[0].set_title("Rata-rata PM2.5 harian", fontweight="bold")
axes[0].set_xlabel("PM2.5 (µg/m³)")
for i, v in enumerate(d1["rata_rata"]):
    axes[0].text(v + 0.8, i, f"{v:.1f}", va="center", fontsize=9)
w2 = [sorot(v, d1["persen_hari"].max(), d1["persen_hari"].min()) for v in d1["persen_hari"]]
axes[1].barh(d1.index, d1["persen_hari"], color=w2)
axes[1].set_title(f"Persentase hari dengan PM2.5 > {AMBANG} µg/m³", fontweight="bold")
axes[1].set_xlabel("Persentase hari (%)")
for i, v in enumerate(d1["persen_hari"]):
    axes[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", visible=False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
tertinggi = ringkasan["rata_rata"].idxmax()
terendah = ringkasan["rata_rata"].idxmin()
if len(ringkasan) > 1:
    st.info(
        f"Merah = tertinggi, biru = terendah. Pada data yang dipilih, {tertinggi} paling tinggi "
        f"({ringkasan['rata_rata'].max():.1f} µg/m³) dan {terendah} paling rendah ({ringkasan['rata_rata'].min():.1f} µg/m³)."
    )
else:
    st.info(f"Hanya satu stasiun yang dipilih ({tertinggi}). Pilih lebih dari satu stasiun untuk membandingkan.")

# ---------------- Pertanyaan 2 ----------------
st.header("Pertanyaan 2: Pola Bulanan dan Musiman")
st.write("Bagaimana tren PM2.5 bulanan pada tahun penuh 2014-2016, bulan apa tertinggi, dan berapa selisih musim dingin dibandingkan musim panas?")

df_full = df[df["year"].isin([2014, 2015, 2016])]
if df_full.empty:
    st.warning("Filter tanggal tidak mencakup tahun 2014–2016, sehingga pola bulanan tidak ditampilkan.")
else:
    pivot = df_full.pivot_table(index="month", columns="year", values="PM2.5", aggfunc="mean").reindex(range(1, 13))
    bulanan = df_full.groupby("month")["PM2.5"].mean().reindex(range(1, 13))
    musiman = df_full.groupby("musim")["PM2.5"].mean().reindex(URUT_MUSIM)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1.6, 1]})
    warna_tahun = {2014: "#9AA5AD", 2015: "#6C8FA6", 2016: "#2E86AB"}
    for tahun in pivot.columns:
        axes[0].plot(pivot.index, pivot[tahun], marker="o", linewidth=1.5, color=warna_tahun.get(tahun, "#888"), alpha=0.8, label=str(tahun))
    axes[0].plot(bulanan.index, bulanan.values, color="#C0392B", linewidth=3, marker="o", label="Rata-rata")
    puncak = bulanan.idxmax()
    axes[0].annotate(f"Puncak: {NAMA_BULAN[puncak - 1]} ({bulanan.max():.1f})", xy=(puncak, bulanan.max()),
                     xytext=(max(1, puncak - 4), bulanan.max() + 18), arrowprops=dict(arrowstyle="->", color="#C0392B"),
                     color="#C0392B", fontweight="bold")
    axes[0].set_xticks(range(1, 13))
    axes[0].set_xticklabels(NAMA_BULAN)
    axes[0].set_ylabel("PM2.5 (µg/m³)")
    axes[0].set_title("Rata-rata PM2.5 bulanan", fontweight="bold")
    axes[0].legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4)

    warna_musim = ["#C0392B" if m == "Musim Dingin" else "#2E86AB" if m == "Musim Panas" else "#B0B7BD" for m in URUT_MUSIM]
    axes[1].bar(URUT_MUSIM, musiman.values, color=warna_musim)
    for i, v in enumerate(musiman.values):
        if pd.notna(v):
            axes[1].text(i, v + 1.5, f"{v:.1f}", ha="center", fontweight="bold")
    axes[1].set_title("Rata-rata PM2.5 per musim", fontweight="bold")
    axes[1].set_ylabel("PM2.5 (µg/m³)")
    axes[1].tick_params(axis="x", rotation=15)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    dingin, panas = musiman["Musim Dingin"], musiman["Musim Panas"]
    if pd.notna(dingin) and pd.notna(panas):
        st.info(f"Musim dingin rata-rata {dingin:.1f} µg/m³, musim panas {panas:.1f} µg/m³: selisih {dingin - panas:.1f} µg/m³ ({(dingin - panas) / panas * 100:.0f}% lebih tinggi).")

# ---------------- Analisis lanjutan ----------------
st.header("Analisis Lanjutan: Kategori Kualitas Udara per Musim")
st.write("Hari dikelompokkan ke dalam kategori kualitas udara (binning PM2.5 harian), lalu dibandingkan antar musim.")

tabel = (pd.crosstab(df["musim"], df["kategori"], normalize="index") * 100).reindex(index=URUT_MUSIM, columns=LABEL).dropna(how="all").fillna(0)
fig, ax = plt.subplots(figsize=(11, 4))
tabel.plot(kind="barh", stacked=True, color=WARNA_KATEGORI, width=0.7, ax=ax)
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Persentase hari (%)")
ax.set_ylabel("")
ax.grid(axis="y", visible=False)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(title="Kategori", bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ---------------- Kesimpulan ----------------
st.header("Kesimpulan & Rekomendasi")
st.caption("Catatan: angka pada bagian kesimpulan dihitung dari seluruh data dan tidak berubah mengikuti filter di sebelah kiri.")
st.markdown(
    """
- **Pertanyaan 1:** Dongsi tertinggi (rata-rata 86,1 µg/m³; 43,5% hari di atas 75) dan Dingling terendah (66,8 µg/m³; 32,2% hari), berdasarkan seluruh data.
- **Pertanyaan 2:** PM2.5 memuncak pada Desember (112,2 µg/m³) dan terendah pada Agustus (51,1 µg/m³); musim dingin sekitar 62% lebih tinggi dari musim panas (2014–2016, seluruh stasiun).
- **Rekomendasi:** prioritaskan pengendalian emisi di stasiun dengan PM2.5 tertinggi, dan siapkan peringatan dini serta pembatasan emisi mulai Oktober sampai Maret (kewaspadaan tertinggi November–Desember).
"""
)