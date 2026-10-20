from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="RetailPulse AI Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep the main page visually consistent with the screenshots.
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .rp-subtitle {
        color: #d1d5db;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }
    .rp-section {
        border-top: 1px solid rgba(128,128,128,.35);
        padding-top: 1.5rem;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom sidebar: one navigation menu only.
with st.sidebar:
    st.markdown("## 🛍️ RetailPulse")
    st.caption("Retail analytics and decision support")
    st.divider()
    st.page_link("app.py", label="Dashboard Overview", icon="🏠")
    st.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
    st.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
    st.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation + Churn Risk", icon="👥")
    st.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")

# Main overview, matching the first reference screenshot.
st.title("🚀 RetailPulse AI Analytics Platform")
st.header("📌 Overview")
st.markdown(
    """
    <div class="rp-subtitle">
    RetailPulse is an AI-powered retail analytics platform designed to help
    businesses understand customers, forecast demand, manage inventory, and
    make data-driven decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 📈 Demand Forecasting")
    st.write("Prophet + LSTM based 30-day demand forecasting.")
    st.markdown("### 👥 Customer Analytics")
    st.write("RFM analysis and customer segmentation using machine learning.")
    st.markdown("### ⚠️ Churn Prediction")
    st.write("Identify customers who are at risk of churn.")

with right:
    st.markdown("### 📦 Inventory Optimization")
    st.write("Forecast-based reorder recommendations and stock monitoring.")
    st.markdown("### 📊 Business Intelligence")
    st.write("Interactive analytics, KPIs, alerts and downloadable reports.")

st.markdown('<div class="rp-section"></div>', unsafe_allow_html=True)
st.header("🏗️ System Architecture")
st.markdown(
    "**Data → Processing → ML Models → Forecasting → Dashboard → Deployment → Insights**"
)

a, b, c, d, e = st.columns(5, gap="medium")
a.info("📥  **Data**")
b.info("⚙️  **Processing**")
c.info("🤖  **ML Models**")
d.info("📈  **Forecasting**")
e.info("💡  **Insights**")

st.markdown('<div class="rp-section"></div>', unsafe_allow_html=True)
st.success("✅ RetailPulse dashboard is ready.")
st.info(
    "👉 Use the sidebar to explore Sales Analytics, Demand Forecasting, "
    "Customer Segmentation + Churn Risk, and Inventory Optimization."
)

st.caption(
    "Note: This page is the dashboard overview. Detailed charts and filters "
    "are available on the individual pages."
)
