# Analisis Kualitas Udara Beijing (PM2.5)

Proyek akhir kelas analisis data di Dicoding, dibuat oleh Rizky Wahyu Dina Putri.

Data yang dipakai adalah Air Quality Dataset: pengukuran per jam dari 12 stasiun pemantauan di Beijing, dari 1 Maret 2013 sampai 28 Februari 2017. Analisisnya difokuskan pada PM2.5.

## Pertanyaan yang dijawab

1. Stasiun mana yang rata-rata PM2.5 hariannya paling tinggi dan paling rendah, dan berapa persen harinya yang melewati batas 75 µg/m³?
2. Bagaimana pola PM2.5 bulanan pada tahun penuh 2014–2016, bulan apa yang paling tinggi, dan seberapa jauh selisih musim dingin dengan musim panas?

## Isi folder

- `dashboard/` berisi `dashboard.py` (kode dashboard Streamlit) dan `main_data.csv` (data harian hasil olahan dari notebook)
- `data/` berisi 12 file CSV asli, satu per stasiun
- `notebook.ipynb` berisi seluruh proses analisis, dari wrangling sampai kesimpulan
- `requirements.txt` berisi daftar library yang dibutuhkan
- `url.txt` berisi tautan dashboard yang sudah online

## Cara menjalankan dashboard

Di Python, lalu buka terminal di folder proyek ini.

Pasang library dulu:

`pip install -r requirements.txt`

Lalu jalankan dashboard:

`streamlit run dashboard/dashboard.py`

Kalau di Windows muncul pesan bahwa `streamlit` tidak dikenali, jalankan lewat Python:

`python -m streamlit run dashboard/dashboard.py`

Dashboard akan terbuka di browser, biasanya di http://localhost:8501.

## Dashboard online


## Catatan soal notebook

Sel pertama di bagian Gathering Data memakai `!unzip` dan hanya berguna kalau notebook dijalankan di Google Colab (file `Air-quality-dataset.zip` perlu diunggah dulu).