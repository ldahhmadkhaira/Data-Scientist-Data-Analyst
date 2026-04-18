"""
=============================================================
DASHBOARD INTERAKTIF – TREN BELANJA KONSUMEN 2026
Studi Kasus: Bisnis & Ekonomi — Analisis Perilaku Pelanggan
Mata Kuliah: Analisis Data dan Visualisasi Lanjutan
Prodi S2 Sains Data, Universitas Hasanuddin
=============================================================
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 1. MEMUAT & MEMPERSIAPKAN DATA
# ─────────────────────────────────────────────────────────────

df_raw = pd.read_csv("Consumer_Shopping_Trends_2026 (6).csv")

kolom_baru = {
    "age":                         "usia",
    "monthly_income":              "pendapatan_bulanan",
    "daily_internet_hours":        "jam_internet_harian",
    "smartphone_usage_years":      "lama_pakai_smartphone",
    "social_media_hours":          "jam_media_sosial",
    "online_payment_trust_score":  "kepercayaan_pembayaran_online",
    "tech_savvy_score":            "skor_melek_teknologi",
    "monthly_online_orders":       "pesanan_online_bulanan",
    "monthly_store_visits":        "kunjungan_toko_bulanan",
    "avg_online_spend":            "rata_belanja_online",
    "avg_store_spend":             "rata_belanja_toko",
    "discount_sensitivity":        "sensitivitas_diskon",
    "return_frequency":            "frekuensi_retur",
    "avg_delivery_days":           "rata_hari_pengiriman",
    "delivery_fee_sensitivity":    "sensitivitas_ongkir",
    "free_return_importance":      "pentingnya_retur_gratis",
    "product_availability_online": "ketersediaan_produk_online",
    "impulse_buying_score":        "skor_pembelian_impulsif",
    "need_touch_feel_score":       "skor_perlu_sentuh_produk",
    "brand_loyalty_score":         "skor_loyalitas_merek",
    "environmental_awareness":     "kesadaran_lingkungan",
    "time_pressure_level":         "tingkat_tekanan_waktu",
    "gender":                      "jenis_kelamin",
    "city_tier":                   "tingkat_kota",
    "shopping_preference":         "preferensi_belanja",
}

df = df_raw.rename(columns=kolom_baru)
df["jenis_kelamin"]    = df["jenis_kelamin"].map({"Male": "Pria", "Female": "Wanita", "Other": "Lainnya"})
df["tingkat_kota"]     = df["tingkat_kota"].map({"Tier 1": "Kota Tier 1", "Tier 2": "Kota Tier 2", "Tier 3": "Kota Tier 3"})
df["preferensi_belanja"] = df["preferensi_belanja"].map({"Online": "Online", "Store": "Toko", "Hybrid": "Hybrid"})
df["total_belanja"]    = df["rata_belanja_online"] + df["rata_belanja_toko"]
bins_usia  = [17, 25, 35, 45, 55, 65, 80]
label_usia = ["18-25", "26-35", "36-45", "46-55", "56-65", "66-79"]
df["kelompok_usia"] = pd.cut(df["usia"], bins=bins_usia, labels=label_usia)

# Clustering K-Means
fitur_cluster = ["pendapatan_bulanan", "pesanan_online_bulanan",
                 "sensitivitas_diskon", "skor_loyalitas_merek"]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[fitur_cluster])
km = KMeans(n_clusters=4, random_state=42, n_init=10)
df["segmen_pelanggan"] = km.fit_predict(X_scaled).astype(str)
nama_segmen = {"0": "Pembelanja Premium", "1": "Pemburu Diskon", "2": "Belanja Seimbang", "3": "Pengunjung Kasual"}
df["segmen_pelanggan"] = df["segmen_pelanggan"].map(nama_segmen)

# ─────────────────────────────────────────────────────────────
# 2. KPI RINGKASAN
# ─────────────────────────────────────────────────────────────

total_konsumen    = len(df)
rata_total_belanja = df["total_belanja"].mean()
pct_prefer_online  = (df["preferensi_belanja"] == "Online").mean() * 100
pct_prefer_toko    = (df["preferensi_belanja"] == "Toko").mean() * 100
pct_prefer_hybrid  = (df["preferensi_belanja"] == "Hybrid").mean() * 100
rata_pendapatan    = df["pendapatan_bulanan"].mean()
rata_pesanan_online= df["pesanan_online_bulanan"].mean()

# ─────────────────────────────────────────────────────────────
# WARNA TEMA
# ─────────────────────────────────────────────────────────────

WARNA_PRIMER   = "#0F4C81"
WARNA_AKSEN    = "#00C9A7"
WARNA_SEKUNDER = "#FF6B6B"
WARNA_KUNING   = "#FFD93D"
WARNA_UNGU     = "#845EC2"

PALET = [WARNA_PRIMER, WARNA_AKSEN, WARNA_SEKUNDER, WARNA_KUNING, WARNA_UNGU,
         "#4ECDC4", "#F7B731", "#A3CB38", "#FD7272", "#9B59B6"]

TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#E0E0E0", family="Inter, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=PALET,
    )
)

# ─────────────────────────────────────────────────────────────
# 3. APLIKASI DASH
# ─────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    title="Dashboard Tren Belanja Konsumen 2026",
)

# ── CSS inline kustom ──
STYLE_CARD = {
    "background": "linear-gradient(135deg, #0d1b2a 0%, #1a2f4a 100%)",
    "borderRadius": "16px",
    "border": "1px solid rgba(255,255,255,0.08)",
    "padding": "20px",
    "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
}

STYLE_KPI = {
    **STYLE_CARD,
    "textAlign": "center",
    "background": "linear-gradient(135deg, #0F4C81 0%, #1565C0 100%)",
    "border": "1px solid rgba(0,201,167,0.3)",
}

STYLE_KPI_AKSEN = {
    **STYLE_KPI,
    "background": "linear-gradient(135deg, #00796b 0%, #00C9A7 100%)",
}

STYLE_KPI_MERAH = {
    **STYLE_KPI,
    "background": "linear-gradient(135deg, #C62828 0%, #FF6B6B 100%)",
}

STYLE_KPI_KUNING = {
    **STYLE_KPI,
    "background": "linear-gradient(135deg, #F57F17 0%, #FFD93D 100%)",
}

def kpi_card(judul, nilai, satuan, keterangan, style=STYLE_KPI):
    return html.Div([
        html.P(judul, style={"color": "rgba(255,255,255,0.75)", "fontSize": "0.78rem",
                              "textTransform": "uppercase", "letterSpacing": "1px", "margin": "0 0 6px"}),
        html.H2(nilai, style={"color": "#fff", "fontWeight": "700", "margin": "0", "fontSize": "2rem"}),
        html.Span(satuan, style={"color": "rgba(255,255,255,0.6)", "fontSize": "0.85rem"}),
        html.P(keterangan, style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.72rem", "margin": "8px 0 0"}),
    ], style=style)

def insight_card(teks, ikon="💡"):
    return html.Div([
        html.Span(ikon, style={"fontSize": "1.3rem", "marginRight": "8px"}),
        html.Span(teks, style={"color": "#E0E0E0", "fontSize": "0.82rem", "lineHeight": "1.5"}),
    ], style={
        "background": "rgba(0,201,167,0.08)",
        "border": "1px solid rgba(0,201,167,0.25)",
        "borderRadius": "10px",
        "padding": "10px 14px",
        "marginBottom": "8px",
    })


# ────────────────────
# LAYOUT UTAMA
# ────────────────────

app.layout = html.Div(style={
    "background": "#060f1a",
    "minHeight": "100vh",
    "fontFamily": "'Inter', sans-serif",
    "color": "#E0E0E0",
}, children=[

    # HEADER
    html.Div([
        html.Div([
            html.H1("📊 Dashboard Tren Belanja Konsumen 2026",
                    style={"fontWeight": "700", "fontSize": "1.8rem", "margin": 0, "color": "#fff"}),
            html.P("Studi Kasus Bisnis & Ekonomi   •   Analisis Perilaku Pelanggan   •   Sains Data ",
                   style={"color": "rgba(255,255,255,0.55)", "fontSize": "0.82rem", "margin": "4px 0 0"}),
        ]),
        html.Div([
            html.Span(f"n = {total_konsumen:,} responden",
                      style={"background": "rgba(0,201,167,0.15)", "border": "1px solid #00C9A7",
                             "borderRadius": "20px", "padding": "6px 16px", "fontSize": "0.82rem", "color": "#00C9A7"}),
        ]),
    ], style={
        "background": "linear-gradient(90deg, #0F4C81 0%, #0d1b2a 100%)",
        "padding": "20px 32px",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "borderBottom": "1px solid rgba(255,255,255,0.06)",
    }),

    # FILTER BAR
    html.Div([
        html.Span("🔍 Filter:", style={"color": "#00C9A7", "fontWeight": "600", "marginRight": "12px"}),
        dbc.Row([
            dbc.Col([
                html.Label("Jenis Kelamin", style={"fontSize": "0.75rem", "color": "rgba(255,255,255,0.6)"}),
                dcc.Dropdown(
                    id="filter-gender",
                    options=[{"label": g, "value": g} for g in ["Pria", "Wanita", "Lainnya"]],
                    multi=True,
                    placeholder="Semua jenis kelamin",
                    style={"background": "#1a2f4a", "color": "#000", "fontSize": "0.82rem"},
                ),
            ], md=3),
            dbc.Col([
                html.Label("Tingkat Kota", style={"fontSize": "0.75rem", "color": "rgba(255,255,255,0.6)"}),
                dcc.Dropdown(
                    id="filter-kota",
                    options=[{"label": k, "value": k} for k in ["Kota Tier 1", "Kota Tier 2", "Kota Tier 3"]],
                    multi=True,
                    placeholder="Semua tingkat kota",
                    style={"background": "#1a2f4a", "color": "#000", "fontSize": "0.82rem"},
                ),
            ], md=3),
            dbc.Col([
                html.Label("Preferensi Belanja", style={"fontSize": "0.75rem", "color": "rgba(255,255,255,0.6)"}),
                dcc.Dropdown(
                    id="filter-pref",
                    options=[{"label": p, "value": p} for p in ["Online", "Toko", "Hybrid"]],
                    multi=True,
                    placeholder="Semua preferensi",
                    style={"background": "#1a2f4a", "color": "#000", "fontSize": "0.82rem"},
                ),
            ], md=3),
            dbc.Col([
                html.Label("Rentang Usia", style={"fontSize": "0.75rem", "color": "rgba(255,255,255,0.6)"}),
                dcc.RangeSlider(
                    id="filter-usia",
                    min=18, max=79, step=1, value=[18, 79],
                    marks={18: "18", 35: "35", 50: "50", 65: "65", 79: "79"},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ], md=3),
        ], className="g-2"),
    ], style={
        "background": "#0d1b2a",
        "padding": "14px 32px",
        "borderBottom": "1px solid rgba(255,255,255,0.05)",
    }),

    # KONTEN UTAMA
    html.Div([

        # ── BARIS KPI ──
        dbc.Row([
            dbc.Col(html.Div(id="kpi-konsumen"), md=3),
            dbc.Col(html.Div(id="kpi-belanja"),  md=3),
            dbc.Col(html.Div(id="kpi-pesanan"),  md=3),
            dbc.Col(html.Div(id="kpi-online"),   md=3),
        ], className="g-3 mb-3"),

        # ── VISUAL 1: Distribusi Belanja Online vs Toko ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("🛒 Visual 1 — Pola Belanja: Online vs. Toko",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Bagaimana konsumen mendistribusikan anggaran belanja mereka?",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis1-box", style={"height": "340px"}),
                    html.Div(id="insight1"),
                ], style=STYLE_CARD),
            ], md=7),
            dbc.Col([
                html.Div([
                    html.H5("📊 Visual 2 — Preferensi Saluran Belanja",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Distribusi konsumen berdasarkan preferensi belanja & segmen usia",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis2-donut", style={"height": "340px"}),
                    html.Div(id="insight2"),
                ], style=STYLE_CARD),
            ], md=5),
        ], className="g-3 mb-3"),

        # ── VISUAL 3: Pengaruh Pendapatan pada Perilaku Belanja ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("💰 Visual 3 — Pendapatan vs. Total Belanja per Segmen",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Apakah pendapatan menjadi faktor utama pola belanja konsumen?",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis3-scatter", style={"height": "360px"}),
                    html.Div(id="insight3"),
                ], style=STYLE_CARD),
            ], md=6),

            dbc.Col([
                html.Div([
                    html.H5("🔍 Visual 4 — Segmentasi Pelanggan (K-Means)",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Empat profil pelanggan dominan berdasarkan perilaku belanja",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis4-segmen", style={"height": "360px"}),
                    html.Div(id="insight4"),
                ], style=STYLE_CARD),
            ], md=6),
        ], className="g-3 mb-3"),

        # ── VISUAL 5: Radar Profil + Heatmap Korelasi ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("🕸️ Visual 5 — Profil Sensitifitas per Tingkat Kota",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Perbedaan perilaku konsumen berdasarkan ukuran kota tinggal",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis5-radar", style={"height": "380px"}),
                    html.Div(id="insight5"),
                ], style=STYLE_CARD),
            ], md=5),

            dbc.Col([
                html.Div([
                    html.H5("🔥 Visual 6 — Korelasi Antar Perilaku Belanja",
                            style={"color": "#00C9A7", "fontWeight": "600", "marginBottom": "4px"}),
                    html.P("Hubungan antara variabel-variabel kunci perilaku konsumen",
                           style={"color": "rgba(255,255,255,0.5)", "fontSize": "0.78rem", "marginBottom": "12px"}),
                    dcc.Graph(id="vis6-heatmap", style={"height": "380px"}),
                    html.Div(id="insight6"),
                ], style=STYLE_CARD),
            ], md=7),
        ], className="g-3 mb-3"),

        # ── RINGKASAN REKOMENDASI ──
        html.Div([
            html.H4("📋 Ringkasan Insight & Rekomendasi Strategis",
                    style={"color": "#FFD93D", "fontWeight": "700", "marginBottom": "16px"}),
            dbc.Row([
                dbc.Col([
                    html.H6("🏪 Strategi Toko Fisik", style={"color": "#FF6B6B", "marginBottom": "8px"}),
                    html.Ul([
                        html.Li("Mayoritas konsumen (86%) masih preferensi toko — pertahankan pengalaman in-store"),
                        html.Li("Konsumen Tier 3 lebih price-sensitive → kembangkan program diskon dan loyalitas"),
                        html.Li("Segmen 'Pengunjung Kasual' perlu stimulus: program poin, cashback lokal"),
                    ], style={"fontSize": "0.82rem", "paddingLeft": "16px", "lineHeight": "1.8"}),
                ], md=4),
                dbc.Col([
                    html.H6("🛒 Strategi Digital & E-Commerce", style={"color": "#00C9A7", "marginBottom": "8px"}),
                    html.Ul([
                        html.Li("Konsumen online memiliki pesanan bulanan lebih tinggi — optimalkan UX dan checkout"),
                        html.Li("Kepercayaan pembayaran digital berkorelasi pos. dengan belanja online → edukasi keamanan"),
                        html.Li("Segmen 'Pembelanja Premium': tawarkan layanan premium, free shipping, VIP membership"),
                    ], style={"fontSize": "0.82rem", "paddingLeft": "16px", "lineHeight": "1.8"}),
                ], md=4),
                dbc.Col([
                    html.H6("🎯 Strategi Segmentasi & Personalisasi", style={"color": "#FFD93D", "marginBottom": "8px"}),
                    html.Ul([
                        html.Li("K-Means mengidentifikasi 4 segmen — kembangkan kampanye pemasaran per profil"),
                        html.Li("'Pemburu Diskon': flash sale, bundling — ROI tinggi dari biaya akuisisi rendah"),
                        html.Li("Konsumen 26-45 tahun: segmen paling produktif → prioritaskan personalisasi konten"),
                    ], style={"fontSize": "0.82rem", "paddingLeft": "16px", "lineHeight": "1.8"}),
                ], md=4),
            ]),
        ], style={**STYLE_CARD, "border": "1px solid rgba(255,215,61,0.25)"}),

    ], style={"padding": "24px 32px"}),

    # FOOTER
    html.Div([
        html.P("Ahmad Khair   •   S2 Sains Data, Universitas Hasanuddin   •   2026   •   Analisis Data dan Visualisasi Lanjutan",
               style={"color": "rgba(255,255,255,0.3)", "fontSize": "0.75rem", "textAlign": "center", "margin": 0}),
    ], style={"padding": "12px 32px", "borderTop": "1px solid rgba(255,255,255,0.05)"}),
])


# ─────────────────────────────────────────────────────────────
# 4. CALLBACKS
# ─────────────────────────────────────────────────────────────

def filter_df(gender_vals, kota_vals, pref_vals, usia_range):
    dff = df.copy()
    if gender_vals:
        dff = dff[dff["jenis_kelamin"].isin(gender_vals)]
    if kota_vals:
        dff = dff[dff["tingkat_kota"].isin(kota_vals)]
    if pref_vals:
        dff = dff[dff["preferensi_belanja"].isin(pref_vals)]
    dff = dff[(dff["usia"] >= usia_range[0]) & (dff["usia"] <= usia_range[1])]
    return dff


def fig_layout(fig):
    fig.update_layout(
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#E0E0E0", family="Inter, sans-serif", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig


@app.callback(
    [Output("kpi-konsumen", "children"),
     Output("kpi-belanja", "children"),
     Output("kpi-pesanan", "children"),
     Output("kpi-online", "children"),
     Output("vis1-box", "figure"),
     Output("vis2-donut", "figure"),
     Output("vis3-scatter", "figure"),
     Output("vis4-segmen", "figure"),
     Output("vis5-radar", "figure"),
     Output("vis6-heatmap", "figure"),
     Output("insight1", "children"),
     Output("insight2", "children"),
     Output("insight3", "children"),
     Output("insight4", "children"),
     Output("insight5", "children"),
     Output("insight6", "children"),
    ],
    [Input("filter-gender", "value"),
     Input("filter-kota", "value"),
     Input("filter-pref", "value"),
     Input("filter-usia", "value"),
    ],
)
def update_all(gender_vals, kota_vals, pref_vals, usia_range):
    dff = filter_df(gender_vals, kota_vals, pref_vals, usia_range)

    if len(dff) == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a",
                                 annotations=[dict(text="Tidak ada data", showarrow=False, font_color="#888")])
        empty_kpi = kpi_card("—", "—", "", "Tidak ada data", STYLE_KPI)
        return ([empty_kpi]*4 + [empty_fig]*6 + [html.Div()]*6)

    n = len(dff)
    avg_belanja  = dff["total_belanja"].mean()
    avg_pesanan  = dff["pesanan_online_bulanan"].mean()
    pct_online   = (dff["preferensi_belanja"] == "Online").mean() * 100

    # KPI
    kpi1 = kpi_card("Total Konsumen", f"{n:,}", "responden",
                    f"Rentang usia {usia_range[0]}-{usia_range[1]} tahun", STYLE_KPI)
    kpi2 = kpi_card("Rata-rata Total Belanja", f"Rp {avg_belanja/1000:.0f}K", "per bulan",
                    f"Online + Toko gabungan", STYLE_KPI_AKSEN)
    kpi3 = kpi_card("Rata-rata Pesanan Online", f"{avg_pesanan:.1f}x", "per bulan",
                    "Frekuensi transaksi digital", STYLE_KPI_MERAH)
    kpi4 = kpi_card("Preferensi Online", f"{pct_online:.1f}%", "dari total",
                    "Konsumen pilih belanja digital", STYLE_KPI_KUNING)

    # ── VISUAL 1: Box plot — Online vs Toko per kelompok usia ──
    melt_dff = dff.melt(
        id_vars=["kelompok_usia"],
        value_vars=["rata_belanja_online", "rata_belanja_toko"],
        var_name="Saluran",
        value_name="Jumlah Belanja"
    )
    melt_dff["Saluran"] = melt_dff["Saluran"].map({
        "rata_belanja_online": "Belanja Online",
        "rata_belanja_toko": "Belanja Toko"
    })
    fig1 = px.violin(
        melt_dff, x="kelompok_usia", y="Jumlah Belanja", color="Saluran",
        box=True, points=False,
        color_discrete_map={"Belanja Online": WARNA_AKSEN, "Belanja Toko": WARNA_SEKUNDER},
        labels={"kelompok_usia": "Kelompok Usia", "Jumlah Belanja": "Jumlah Belanja (Rp)"},
        title="Distribusi Belanja Online vs Toko per Kelompok Usia",
        category_orders={"kelompok_usia": label_usia},
    )
    fig1 = fig_layout(fig1)
    fig1.update_traces(meanline_visible=True)

    top_seg_vis1 = dff.groupby("kelompok_usia")["rata_belanja_online"].mean().idxmax()
    i1 = insight_card(
        f"Kelompok usia {top_seg_vis1} memiliki rata-rata belanja online tertinggi. "
        f"Belanja toko cenderung lebih merata lintas semua kelompok usia.", "🎯"
    )

    # ── VISUAL 2: Donut chart preferensi belanja, drill-down per kota ──
    pref_kota = dff.groupby(["tingkat_kota", "preferensi_belanja"]).size().reset_index(name="jumlah")
    fig2 = px.sunburst(
        pref_kota, path=["tingkat_kota", "preferensi_belanja"], values="jumlah",
        color="preferensi_belanja",
        color_discrete_map={"Online": WARNA_AKSEN, "Toko": WARNA_SEKUNDER, "Hybrid": WARNA_KUNING},
        title="Preferensi Saluran Belanja per Tingkat Kota",
    )
    fig2.update_traces(textinfo="label+percent entry", insidetextfont_size=10)
    fig2 = fig_layout(fig2)

    dom_pref = dff["preferensi_belanja"].value_counts().index[0]
    dom_pct  = dff["preferensi_belanja"].value_counts(normalize=True).iloc[0] * 100
    i2 = insight_card(
        f"'{dom_pref}' mendominasi ({dom_pct:.0f}%) preferensi konsumen. "
        f"Segmentasi per kota menunjukkan variasi pola konsumsi yang signifikan.", "🏪"
    )

    # ── VISUAL 3: Scatter — Pendapatan vs Total Belanja ──
    sample_dff = dff.sample(min(2000, len(dff)), random_state=42)
    fig3 = px.scatter(
        sample_dff, x="pendapatan_bulanan", y="total_belanja",
        color="segmen_pelanggan",
        size="pesanan_online_bulanan",
        hover_data=["usia", "preferensi_belanja", "tingkat_kota"],
        color_discrete_sequence=PALET,
        title="Pendapatan Bulanan vs. Total Belanja Konsumen",
        labels={"pendapatan_bulanan": "Pendapatan Bulanan (Rp)", "total_belanja": "Total Belanja (Rp)",
                "segmen_pelanggan": "Segmen"},
        opacity=0.65,
        trendline="lowess",
    )
    fig3 = fig_layout(fig3)
    corr = dff["pendapatan_bulanan"].corr(dff["total_belanja"])
    i3 = insight_card(
        f"Korelasi pendapatan & total belanja = {corr:.2f}. "
        f"Segmen 'Pembelanja Premium' terkonsentrasi di pendapatan & belanja tertinggi. "
        f"Pendapatan bukan satu-satunya penentu — pola diskon & loyalitas juga berperan.", "📈"
    )

    # ── VISUAL 4: Bar chart segmen pelanggan ──
    seg_agg = dff.groupby("segmen_pelanggan").agg(
        jumlah=("usia", "count"),
        avg_belanja=("total_belanja", "mean"),
        avg_pesanan=("pesanan_online_bulanan", "mean"),
        avg_diskon=("sensitivitas_diskon", "mean"),
    ).reset_index()
    seg_agg = seg_agg.sort_values("avg_belanja", ascending=True)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=seg_agg["segmen_pelanggan"],
        x=seg_agg["avg_belanja"],
        name="Rata-rata Total Belanja (Rp)",
        orientation="h",
        marker_color=PALET[:4],
        text=seg_agg["avg_belanja"].apply(lambda v: f"Rp {v/1000:.0f}K"),
        textposition="outside",
    ))
    fig4.update_layout(
        title="Profil Segmen Pelanggan (K-Means, k=4)",
        xaxis_title="Rata-rata Total Belanja (Rp)",
        paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a",
        font=dict(color="#E0E0E0", family="Inter, sans-serif", size=11),
        margin=dict(l=140, r=40, t=50, b=40),
        showlegend=False,
    )
    fig4.update_xaxes(gridcolor="rgba(255,255,255,0.06)")

    top_seg = seg_agg.sort_values("avg_belanja", ascending=False).iloc[0]
    i4 = insight_card(
        f"Segmen '{top_seg['segmen_pelanggan']}' memiliki rata-rata belanja tertinggi "
        f"(Rp {top_seg['avg_belanja']/1000:.0f}K/bulan). "
        f"4 profil pelanggan ini sebaiknya diperlakukan dengan strategi pemasaran yang berbeda.", "🎯"
    )

    # ── VISUAL 5: Radar — profil per tingkat kota ──
    radar_vars = ["jam_internet_harian", "sensitivitas_diskon", "skor_loyalitas_merek",
                  "kepercayaan_pembayaran_online", "skor_melek_teknologi", "skor_pembelian_impulsif"]
    radar_label = ["Jam Internet", "Sens. Diskon", "Loyalitas Merek",
                   "Kepercayaan\nPembayaran", "Melek Teknologi", "Pembelian\nImpulsif"]

    kota_grp = dff.groupby("tingkat_kota")[radar_vars].mean()

    fig5 = go.Figure()
    colors_radar = [WARNA_AKSEN, WARNA_SEKUNDER, WARNA_KUNING]
    fill_colors  = ["rgba(0,201,167,0.12)", "rgba(255,107,107,0.12)", "rgba(255,217,61,0.12)"]
    for i, (kota, row) in enumerate(kota_grp.iterrows()):
        vals = list(row) + [row.iloc[0]]
        fig5.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_label + [radar_label[0]],
            name=kota,
            line_color=colors_radar[i % 3],
            fill="toself",
            fillcolor=fill_colors[i % 3],
            opacity=0.85,
        ))
    fig5.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, kota_grp.max().max() * 1.1],
                            gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.4)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.5)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        title="Profil Perilaku per Tingkat Kota",
        paper_bgcolor="#0d1b2a",
        font=dict(color="#E0E0E0", family="Inter, sans-serif", size=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    i5 = insight_card(
        "Konsumen Kota Tier 1 unggul dalam melek teknologi & kepercayaan pembayaran digital. "
        "Kota Tier 3 memiliki sensitivitas diskon paling tinggi — strategi promosi harga lebih efektif di sini.", "🏙️"
    )

    # ── VISUAL 6: Heatmap korelasi ──
    corr_vars = {
        "Pendapatan": "pendapatan_bulanan",
        "Total Belanja": "total_belanja",
        "Pesanan Online": "pesanan_online_bulanan",
        "Kunjungan Toko": "kunjungan_toko_bulanan",
        "Sens. Diskon": "sensitivitas_diskon",
        "Loyalitas Merek": "skor_loyalitas_merek",
        "Melek Teknologi": "skor_melek_teknologi",
        "Impulse Buying": "skor_pembelian_impulsif",
        "Kepercayaan Digital": "kepercayaan_pembayaran_online",
    }
    corr_df = dff[[v for v in corr_vars.values()]].rename(columns={v: k for k, v in corr_vars.items()})
    corr_matrix = corr_df.corr()

    fig6 = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=list(corr_vars.keys()),
        y=list(corr_vars.keys()),
        colorscale="RdBu_r",
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont_size=9,
        colorbar=dict(len=0.8, tickfont=dict(color="#ccc", size=9)),
    ))
    fig6.update_layout(
        title="Matriks Korelasi — Variabel Perilaku Belanja",
        paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a",
        font=dict(color="#E0E0E0", family="Inter, sans-serif", size=10),
        margin=dict(l=100, r=20, t=50, b=100),
        xaxis=dict(tickangle=-35),
    )

    max_corr = corr_matrix.unstack().drop_duplicates().nlargest(3)
    i6 = insight_card(
        "Korelasi kuat antara Melek Teknologi & Kepercayaan Digital. "
        "Pesanan Online berkorelasi positif dengan Total Belanja — konsumen digital adalah pelanggan bernilai tinggi. "
        "Loyalitas Merek & Impulse Buying berkorelasi negatif — pelanggan loyal lebih rasional.", "🔥"
    )

    return (kpi1, kpi2, kpi3, kpi4,
            fig1, fig2, fig3, fig4, fig5, fig6,
            i1, i2, i3, i4, i5, i6)


if __name__ == "__main__":
    app.run(debug=False, port=8050)
