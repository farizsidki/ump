# 🇮🇩 Dashboard UMP Indonesia

Visualisasi interaktif Upah Minimum Provinsi (UMP) seluruh Indonesia.

## Fitur

- Tren UMP per provinsi dari waktu ke waktu
- Ranking UMP antar provinsi per tahun
- Pertumbuhan YoY rata-rata nasional
- Filter tahun, provinsi, dan dark/light mode
- KPI cards: UMP nasional, tertinggi, terendah, CAGR

## Struktur File

```
├── app.py
├── style.css
├── ump.xlsx
├── requirements.txt
├── favicon.png
└── .streamlit/
    └── config.toml
```

## Jalankan Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Cloud

1. Push repo ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. New app → pilih repo → `app.py` → Deploy

## Stack

- [Streamlit](https://streamlit.io) — framework UI
- [Plotly](https://plotly.com) — chart interaktif
- [Pandas](https://pandas.pydata.org) — olah data
- [openpyxl](https://openpyxl.readthedocs.io) — baca file Excel

---

© Fariz Sidki
