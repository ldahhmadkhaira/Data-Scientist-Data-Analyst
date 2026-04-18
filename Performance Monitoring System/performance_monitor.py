import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Performance Monitoring System", layout="wide", page_icon="📊")

# --- CUSTOM CSS PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0d141e; color: #ffffff; }
    
    /* Header Style */
    .dashboard-header {
        background: linear-gradient(90deg, #162a40 0%, #0d141e 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 5px solid #00d4ff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Metrics Row */
    .metric-card {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover { transform: scale(1.03); }
    
    .card-blue { background: linear-gradient(135deg, #1e3c72, #2a5298); }
    .card-green { background: linear-gradient(135deg, #0f9b0f, #22c55e); }
    .card-red { background: linear-gradient(135deg, #b91c1c, #ef4444); }
    .card-gold { background: linear-gradient(135deg, #b45309, #f59e0b); }
    
    .metric-label { font-size: 0.85rem; color: rgba(255,255,255,0.8); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.8rem; font-weight: 800; margin: 10px 0; }
    .metric-desc { font-size: 0.75rem; color: rgba(255,255,255,0.6); }

    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1a2a3e;
        border-radius: 10px 10px 0 0;
        color: white;
        padding: 0 30px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #00d4ff !important; color: #0d141e !important; }

    /* Summary Card */
    .summary-box {
        background-color: #162639;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #2d415a;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_superstore.csv')
    monthly = pd.read_csv('monthly_kpi.csv')
    monthly['Date'] = pd.to_datetime(monthly['Date'])
    return df, monthly

df, monthly = load_data()

# --- HEADER ---
st.markdown("""
<div class="dashboard-header">
    <h1 style='margin:0; font-size: 2.8rem;'>📊 Performance Monitoring System 2026</h1>
    <p style='margin:0; opacity: 0.8; font-weight: 400;'>Sistem Analisis Strategis & Laboratorium KPI • Divisi Kecerdasan Bisnis Korporat</p>
</div>
""", unsafe_allow_html=True)

# --- FILTER ROW ---
with st.container():
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        m_opt = ["Semua Pasar"] + list(df['Market'].unique())
        sel_market = st.selectbox("🌍 Filter Wilayah Pasar", m_opt)
    with c2:
        cat_opt = ["Semua Divisi"] + list(df['Category'].unique())
        sel_cat = st.selectbox("📦 Filter Divisi Produk", cat_opt)
    with c3:
        y_range = st.slider("📅 Rentang Periode Analisis", int(df['order year'].min()), int(df['order year'].max()), (2014, 2015))

# Filter Logic
mask = (df['order year'] >= y_range[0]) & (df['order year'] <= y_range[1])
if sel_market != "Semua Pasar": mask &= (df['Market'] == sel_market)
if sel_cat != "Semua Divisi": mask &= (df['Category'] == sel_cat)
f_df = df[mask]

# --- METRIC CALCULATIONS ---
total_sales = f_df['Sales'].sum()
total_profit = f_df['Profit'].sum()
margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0
avg_ach = monthly[monthly['order year'].between(y_range[0], y_range[1])]['Achievement_Pct'].mean()
growth_yoy = monthly[monthly['order year'] == y_range[1]]['Sales_YoY'].mean()

# --- INTERACTIVE TABS ---
tab1, tab2 = st.tabs(["📈 Dashboard Performa Utama", "📑 Executive Intelligence Summary"])

with tab1:
    # Metric Cards Row
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; gap: 20px; margin-bottom: 30px;">
        <div class="metric-card card-blue" style="flex:1;">
            <div class="metric-label">Total Penjualan</div>
            <div class="metric-value">${total_sales/1e6:.1f}M</div>
            <div class="metric-desc">Volume bruto semua segmen</div>
        </div>
        <div class="metric-card card-green" style="flex:1;">
            <div class="metric-label">Laba Bersih</div>
            <div class="metric-value">${total_profit/1e3:.1f}K</div>
            <div class="metric-desc">Efisiensi Margin {margin:.1f}%</div>
        </div>
        <div class="metric-card card-red" style="flex:1;">
            <div class="metric-label">Pencapaian KPI</div>
            <div class="metric-value">{avg_ach:.1f}%</div>
            <div class="metric-desc">Realisasi vs Target Pertumbuhan</div>
        </div>
        <div class="metric-card card-gold" style="flex:1;">
            <div class="metric-label">Indeks Pertumbuhan</div>
            <div class="metric-value">{growth_yoy:.1f}%</div>
            <div class="metric-desc">Performa Year-over-Year</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_row1_1, c_row1_2 = st.columns([2, 1])
    
    with c_row1_1:
        st.markdown("#### 📊 Tren Performa: Target vs Realisasi")
        t_data = monthly[monthly['order year'].between(y_range[0], y_range[1])]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=t_data['Date'], y=t_data['Target_Sales'], name='Target', line=dict(color='rgba(255,255,255,0.3)', dash='dot')))
        fig_trend.add_trace(go.Scatter(x=t_data['Date'], y=t_data['Sales'], name='Realisasi', fill='tozeroy', line=dict(color='#00d4ff', width=4)))
        fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_trend, use_container_width=True)

    with c_row1_2:
        st.markdown("#### 🌍 Kontribusi Wilayah Pasar")
        m_sum = f_df.groupby('Market')['Sales'].sum().reset_index()
        fig_p = px.pie(m_sum, values='Sales', names='Market', hole=.6, template='plotly_dark',
                      color_discrete_sequence=px.colors.sequential.Teal)
        fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=380, showlegend=True, legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.2))
        st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")
    c_row2_1, c_row2_2 = st.columns([1, 1.5])
    
    with c_row2_1:
        st.markdown("#### 📦 Efisiensi Divisi (Profit)")
        cat_p = f_df.groupby('Category').agg({'Profit':'sum'}).reset_index()
        fig_b = px.bar(cat_p, x='Category', y='Profit', color='Category', template='plotly_dark',
                      color_discrete_sequence=['#3b82f6', '#10b981', '#ef4444'])
        fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
        st.plotly_chart(fig_b, use_container_width=True)

    with c_row2_2:
        st.markdown("#### 🔍 Deteksi Deviasi Performa")
        m_miss = monthly[(monthly['Achievement_Pct'] < 100) & (monthly['order year'].between(y_range[0], y_range[1]))]
        if not m_miss.empty:
            st.error(f"Peringatan: Ditemukan {len(m_miss)} periode di bawah target. Divisi Furniture memerlukan perhatian khusus.")
            st.dataframe(m_miss[['Date', 'Sales', 'Target_Sales', 'Achievement_Pct']].tail(5).style.format({"Achievement_Pct": "{:.1f}%"}), use_container_width=True)
        else:
            st.success("Luar Biasa: Semua KPI dalam rentang periode ini mencapai target operasional.")

with tab2:
    st.markdown("### 🏛️ Laporan Kecerdasan Eksekutif")
    
    # DYNAMIC INSIGHT LOGIC
    worst_cat = f_df.groupby('Category')['Profit'].sum().idxmin()
    best_market = f_df.groupby('Market')['Sales'].sum().idxmax()
    miss_pct = (len(m_miss) / len(monthly[monthly['order year'].between(y_range[0], y_range[1])])) * 100 if len(y_range) > 0 else 0
    
    st.markdown(f"""
    <div class="summary-box">
        <h4>📌 Ringkasan Strategis</h4>
        <p>Berdasarkan analisis filter saat ini di pasar <b>{sel_market}</b> dan divisi <b>{sel_cat}</b>:</p>
        <ul>
            <li><b>Status KPI</b>: Sekitar <b>{miss_pct:.1f}%</b> dari periode pemantauan gagal mencapai target pertumbuhan 15%.</li>
            <li><b>Area Kritis</b>: Divisi <b>{worst_cat}</b> teridentifikasi sebagai penyumbang margin terendah/defisit bulan ini.</li>
            <li><b>Lokomotif Revenue</b>: Pasar <b>{best_market}</b> saat ini menjadi penggerak utama volume penjualan Anda.</li>
        </ul>
    </div>
    
    <div style="margin-top: 20px;">
        <h4>💡 Rekomendasi Keputusan Bisnis</h4>
        <div style="background-color: #0e1a2b; padding: 20px; border-radius: 10px; border-left: 4px solid #f59e0b;">
            <p><b>1. Optimasi Biaya furniture</b>: Segera meninjau kebijakan diskon dan biaya logistik pada divisi <b>{worst_cat}</b> untuk mengembalikan profitabilitas.</p>
            <p><b>2. Penetrasi Pasar</b>: Tingkatkan alokasi marketing pada wilayah <b>{best_market}</b> untuk memaksimalkan momentum pertumbuhan yang sedang berlangsung.</p>
            <p><b>3. Perencanaan Stok</b>: Siapkan kapasitas tambahan 20% pada akhir Q4 (Oktober-Desember) untuk menghindari <i>opportunity loss</i> akibat lonjakan musiman.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Catatan: Data di atas diperbarui secara otomatis berdasarkan filter pasar dan divisi yang Anda pilih pada tab dashboard.")
