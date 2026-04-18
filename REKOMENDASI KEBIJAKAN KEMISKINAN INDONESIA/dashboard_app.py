import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from urllib.request import urlopen

# 1. Konfigurasi App & Tema (Light Mode: FLATLY)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Executive Dashboard: Analisis Kemiskinan"

# 2. Persiapan Data
df = pd.read_csv('datasetkemiskinan.csv')
for col in df.columns[2:]:
    df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
df.dropna(inplace=True)

# Agregasi data provinsi untuk Peta dan Bar Chart
df_prov = df.groupby('Provinsi')['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].mean().reset_index()
df_prov = df_prov.sort_values(by='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)', ascending=True)

# KPI Calculations
avg_miskin = df['Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)'].mean()
avg_ipm = df['Indeks Pembangunan Manusia'].mean()
avg_pengeluaran = df['Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)'].mean()

# 3. Komponen Visualisasi
# Map Configuration
url = "https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/master/indonesia-prov.geojson"
try:
    with urlopen(url) as response:
        counties = json.load(response)
    
    # Matching names with GeoJSON
    df_prov['Prov_Map'] = df_prov['Provinsi'].str.upper()
    replace_dict = {
        'ACEH': 'DI. ACEH',
        'KEP. BANGKA BELITUNG': 'BANGKA BELITUNG',
        'D I YOGYAKARTA': 'DAERAH ISTIMEWA YOGYAKARTA',
        'NUSA TENGGARA BARAT': 'NUSATENGGARA BARAT'
    }
    df_prov['Prov_Map'] = df_prov['Prov_Map'].replace(replace_dict)

    fig_map = px.choropleth_map(df_prov, geojson=counties, locations='Prov_Map', featureidkey="properties.Propinsi",
                               color='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)',
                               color_continuous_scale="Viridis",
                               map_style="carto-positron",
                               zoom=3.5, center={"lat": -2.5489, "lon": 118.0149},
                               opacity=0.7,
                               title="Peta Sebaran Kemiskinan per Provinsi"
                              )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
except Exception as e:
    print(f"Error loading map: {e}")
    fig_map = go.Figure().add_annotation(text="Gagal memuat peta")

# Bar Chart Prov
fig_prov = px.bar(df_prov, 
                  x='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)', 
                  y='Provinsi', 
                  orientation='h',
                  title='Kemiskinan per Provinsi',
                  color='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)',
                  color_continuous_scale='Reds')

# Top 10 Kab/Kota
df_top10 = df.sort_values(by='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)', ascending=False).head(10)
fig_top10 = px.bar(df_top10, 
                  x='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)', 
                  y='Kab/Kota', 
                  color='Provinsi',
                  orientation='h',
                  title='Top 10 Kab/Kota Target Intervensi')
fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})

# Scatter Correlation
fig_scatter = px.scatter(df, 
                  x='Rata-rata Lama Sekolah Penduduk 15+ (Tahun)', 
                  y='Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)',
                  color='Tingkat Pengangguran Terbuka',
                  trendline='ols',
                  title='Korelasi Pendidikan vs Kemiskinan')

# Heatmap Matrix
numeric_df = df.select_dtypes(include=['float64', 'int64'])
fig_heatmap = px.imshow(numeric_df.corr(), 
                         text_auto='.2f', 
                         color_continuous_scale='RdBu_r',
                         title='Matriks Korelasi Sosial-Ekonomi')

# 4. Layout Dashboard
app.layout = dbc.Container([
    # Navbar / Header
    dbc.Row([
        dbc.Col(html.H1("Executive Poverty Analysis Dashboard", className="text-center text-primary my-4"), width=12)
    ], className="mb-4"),

    # KPI Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Rerata Kemiskinan"),
            dbc.CardBody([
                html.H3(f"{avg_miskin:.2f}%", className="text-danger"),
                html.P("Persentase Penduduk Miskin", className="card-text text-muted")
            ])
        ], color="light", outline=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Rerata IPM"),
            dbc.CardBody([
                html.H3(f"{avg_ipm:.2f}", className="text-success"),
                html.P("Indeks Pembangunan Manusia", className="card-text text-muted")
            ])
        ], color="light", outline=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Pengeluaran Per Kapita"),
            dbc.CardBody([
                html.H3(f"Rp {avg_pengeluaran:,.0f}", className="text-info"),
                html.P("Ribu Rupiah/Orang/Tahun", className="card-text text-muted")
            ])
        ], color="light", outline=True), width=4),
    ], className="mb-5"),

    # Main Visuals Row 1: Map
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody(dcc.Graph(figure=fig_map))
        ]), width=12)
    ], className="mb-4"),

    # Visuals Row 2: Prov Bar & Top 10
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody(dcc.Graph(figure=fig_prov))
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardBody(dcc.Graph(figure=fig_top10))
        ]), width=6),
    ], className="mb-4"),

    # Visuals Row 3: Scatter & Heatmap
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody(dcc.Graph(figure=fig_scatter))
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardBody(dcc.Graph(figure=fig_heatmap))
        ]), width=6),
    ], className="mb-4"),

    html.Footer("S2 Data Science - UNHAS | Analisis Pembangunan Daerah", className="text-center text-muted py-3")
], fluid=True)

if __name__ == '__main__':
    print("Dashboard is starting at http://127.0.0.1:8050/")
    app.run(debug=False, port=8050)
