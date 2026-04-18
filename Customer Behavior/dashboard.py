import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Page Config
st.set_page_config(page_title="E-Commerce Digital Behavior Dashboard", page_icon="🛒", layout="wide")

st.title("🛒 E-Commerce Customer Behavior Dashboard")
st.markdown("Dashboard cerdas ini mengklasifikasi basis pengguna menggunakan algoritma K-Means Clustering dengan fokus pada interaksi *Digital Behavior* (Pembelian Online & Pemakaian Diskon) untuk memberikan rekomendasi penekanan Churn.")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('ecommerce_customer_data.csv')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'ecommerce_customer_data.csv' tidak ditemukan. Pastikan file berada di direktori yang sama.")
    st.stop()

# Clustering Logics
features_digital = ['Online_Purchases', 'Discount_Usage', 'Membership_Years']
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[features_digital])

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Digital_Segment'] = kmeans.fit_predict(df_scaled)

# Penamaan Klaster dinamis berdasarkan urutan aktivitas belanja
cluster_summary = df.groupby('Digital_Segment')[features_digital].mean().reset_index()
cluster_summary['Score'] = cluster_summary['Online_Purchases'] + (cluster_summary['Discount_Usage']*100)
sorted_clusters = cluster_summary.sort_values(by='Score').index.tolist()

segment_names = ["Casual Visitors", "Standard Users", "Deal Seekers", "Power Purchasers"]
mapping = {sorted_clusters[i]: segment_names[i] for i in range(4)}
df['Segment_Name'] = df['Digital_Segment'].map(mapping)
df['Churn_Label'] = df['Churn'].map({1: 'Churn', 0: 'Retained'})

st.sidebar.header("Filter Analisis")
selected_segment = st.sidebar.multiselect("Pilih Segmen:", options=segment_names, default=segment_names)

filtered_df = df[df['Segment_Name'].isin(selected_segment)]

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pengguna", len(filtered_df))
col2.metric("Rata-rata Transaksi Online", f"{filtered_df['Online_Purchases'].mean():.1f}")
col3.metric("Rata-rata Pemakaian Diskon", f"{filtered_df['Discount_Usage'].mean():.2%}")
churn_rate = filtered_df['Churn'].mean()
col4.metric("Tingkat Churn (Berhenti)", f"{churn_rate:.2%}", delta=f"{(churn_rate-0.5)*100:.1f}% vs Median", delta_color="inverse")

st.markdown("---")

# Visualizations Row 1
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("1. Persebaran Ukuran & Perilaku (Bubble Chart)")
    bubble_df = filtered_df.groupby('Segment_Name').agg({
        'Online_Purchases': 'mean', 'Discount_Usage': 'mean', 'Customer_ID': 'count'
    }).reset_index().rename(columns={'Customer_ID': 'Total_Customer'})
    
    fig1 = px.scatter(
        bubble_df, x='Online_Purchases', y='Discount_Usage', size='Total_Customer', color='Segment_Name',
        hover_name='Segment_Name', size_max=60, title="Rata-rata Belanja vs Rasio Diskon per Segmen"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_v2:
    st.subheader("2. Penentu Retensi (Correlation Heatmap)")
    corr = filtered_df[['Age', 'Membership_Years', 'Online_Purchases', 'Discount_Usage', 'Churn']].corr()
    fig2 = go.Figure(data=go.Heatmap(
                        z=corr.values, x=corr.columns, y=corr.columns,
                        text=corr.values.round(2), texttemplate="%{text}", colorscale='RdBu_r'))
    st.plotly_chart(fig2, use_container_width=True)

# Visualizations Row 2
col_v3, col_v4 = st.columns(2)

with col_v3:
    st.subheader("3. Proporsi Retensi Pada Segmen (Sunburst)")
    churn_segment = filtered_df.groupby(['Segment_Name', 'Churn_Label']).size().reset_index(name='Count')
    fig3 = px.sunburst(
        churn_segment, path=['Segment_Name', 'Churn_Label'], values='Count', color='Churn_Label',
        color_discrete_map={'Retained':'#2ca02c', 'Churn':'#d62728'}
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_v4:
    st.subheader("4. Analisa Demografi Pendapatan")
    trend_income = filtered_df.groupby(pd.qcut(filtered_df['Annual_Income'], q=10, duplicates='drop'))['Online_Purchases'].mean().reset_index()
    trend_income['Income_Bin'] = trend_income['Annual_Income'].astype(str)
    fig4 = px.bar(trend_income, x='Income_Bin', y='Online_Purchases', color='Income_Bin', title="Pembelian Online berbanding Slasifier Pendapatan Tahunan")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.info("💡 **Insight Eksekutif**: Segmen pelanggan *" + segment_names[3] + "* merupakan sumber penghasilan prioritas, sementara lonjakan Churn sangat berkorelasi terhadap durasi keanggotaan. Kurangi *budget burn* diskon massal, fokuskan pada optimasi retensi tahun pertama pada *" + segment_names[0] + "*.")
