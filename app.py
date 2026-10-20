import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

st.set_page_config(
    page_title="RetailPulse Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Hide Streamlit's default page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar navigation styling */
    [data-testid="stSidebar"] .nav-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    [data-testid="stSidebar"] .nav-item {
        padding: 8px 4px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    '<div class="nav-title">RetailPulse</div>',
    unsafe_allow_html=True
)

# app.py is the main entry point, so do not create a page_link to itself.
# These links point to the four scripts stored in the pages/ directory.
st.sidebar.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
st.sidebar.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
st.sidebar.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation + Churn Risk", icon="👥")
st.sidebar.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")
st.sidebar.divider()

# app.py lives in the repository root, alongside the CSV/ZIP data files.
BASE_PATH = Path(__file__).resolve().parent
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
inventory_path = BASE_PATH / "cleaned_inventory_snapshot.csv"

if not sales_path.is_file():
    st.error(
        "Sales data file not found. Expected `cleaned_sales_transactions.zip` "
        f"in the repository root. Checked: {sales_path}"
    )
    st.stop()

if not inventory_path.is_file():
    st.error(
        "Inventory data file not found. Expected `cleaned_inventory_snapshot.csv` "
        f"in the repository root. Checked: {inventory_path}"
    )
    st.stop()

try:
    sales_data = pd.read_csv(
        sales_path,
        compression="zip",
        usecols=["receipt_id", "date", "quantity", "total_value"]
    )
except Exception as exc:
    st.error(
        "Could not read `cleaned_sales_transactions.zip`. Make sure the ZIP "
        "contains a CSV file with columns: receipt_id, date, quantity, total_value. "
        f"Details: {exc}"
    )
    st.stop()

try:
    inventory_data = pd.read_csv(
        inventory_path,
        usecols=["sku_id", "store_id", "stock_on_hand", "reorder_point"]
    )
except Exception as exc:
    st.error(
        "Could not read `cleaned_inventory_snapshot.csv`. Check that it contains "
        "sku_id, store_id, stock_on_hand, reorder_point. "
        f"Details: {exc}"
    )
    st.stop()

if sales_data.empty:
    st.error("Sales ZIP contains no sales records.")
